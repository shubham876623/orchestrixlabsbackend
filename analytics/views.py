import re
import hmac
import threading
import logging

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncDate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import AnonRateThrottle

from .models import PageView, SiteStat, Testimonial, FAQ, InsightBadge, SiteContent
from .serializers import (
    SiteStatSerializer, TestimonialSerializer, FAQSerializer,
    InsightBadgeSerializer, SiteContentSerializer,
)
from contact.models import ContactMessage
from portfolio.models import Project
from portfolio.serializers import ProjectSerializer, ProjectCreateUpdateSerializer

logger = logging.getLogger(__name__)


class TrackingRateThrottle(AnonRateThrottle):
    rate = '60/minute'


class DashboardLoginThrottle(AnonRateThrottle):
    """Strict rate limit on dashboard auth attempts to prevent brute-force."""
    rate = '10/hour'
    scope = 'dashboard_login'


def _get_client_ip(request):
    return (request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
            or request.META.get('REMOTE_ADDR', ''))


def _check_auth(request):
    """Bearer token auth with brute-force protection."""
    secret = getattr(settings, 'DASHBOARD_SECRET', '')
    if not secret:
        return False  # No secret configured — reject all

    auth = request.headers.get('Authorization', '')
    token = auth.removeprefix('Bearer ').strip()
    if not token:
        return False

    # Rate-limit failed auth attempts per IP
    ip = _get_client_ip(request)
    lockout_key = f'dash_lockout:{ip}'
    if cache.get(lockout_key):
        return False  # IP is locked out

    # Constant-time comparison to prevent timing attacks
    if hmac.compare_digest(token, secret):
        # Reset fail counter on success
        cache.delete(f'dash_fails:{ip}')
        return True

    # Track failures
    fail_key = f'dash_fails:{ip}'
    fails = cache.get(fail_key, 0) + 1
    cache.set(fail_key, fails, timeout=3600)
    if fails >= 5:
        cache.set(lockout_key, True, timeout=900)  # Lock out for 15 min after 5 failures
        logger.warning(f'Dashboard brute-force lockout: {ip} after {fails} failed attempts')

    return False


def _parse_user_agent(ua_string):
    """Parse user-agent string into device_type, browser, os."""
    try:
        from user_agents import parse
        ua = parse(ua_string)
        if ua.is_bot:
            device_type = 'bot'
        elif ua.is_mobile:
            device_type = 'mobile'
        elif ua.is_tablet:
            device_type = 'tablet'
        elif ua.is_pc:
            device_type = 'desktop'
        else:
            device_type = 'other'
        browser = f'{ua.browser.family} {ua.browser.version_string}'.strip()
        os_name = f'{ua.os.family} {ua.os.version_string}'.strip()
        return device_type, browser, os_name
    except Exception:
        return '', '', ''


def _resolve_geo_async(pageview_id, ip):
    """Resolve IP to country/city in background thread using ip-api.com (free, no key)."""
    try:
        import requests as req
        r = req.get(f'http://ip-api.com/json/{ip}?fields=country,city', timeout=3)
        if r.status_code == 200:
            data = r.json()
            if data.get('country'):
                PageView.objects.filter(pk=pageview_id).update(
                    country=data.get('country', '')[:100],
                    city=data.get('city', '')[:150],
                )
    except Exception:
        pass  # silently fail — geo is best-effort


class TrackPageView(APIView):
    throttle_classes = [TrackingRateThrottle]

    def post(self, request):
        path = request.data.get('path', '/')
        if not path or len(path) > 255:
            return Response({'ok': False}, status=status.HTTP_400_BAD_REQUEST)

        # Sanitize path: only allow valid URL path characters (letters, digits, /, -, _, .)
        if not re.match(r'^[a-zA-Z0-9/_\-\.#?&=%+]+$', path):
            return Response({'ok': False}, status=status.HTTP_400_BAD_REQUEST)

        # Skip tracking for dashboard/admin/api paths
        if path.startswith(('/dashboard', '/admin', '/api')):
            return Response({'ok': True})

        ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() \
             or request.META.get('REMOTE_ADDR')

        ua_string = request.META.get('HTTP_USER_AGENT', '')[:500]
        device_type, browser, os_name = _parse_user_agent(ua_string)

        # Frontend sends these extra fields — sanitize all input
        screen_width = request.data.get('screen_width')
        screen_height = request.data.get('screen_height')

        # Strip HTML tags from all string inputs to prevent stored XSS
        def _strip_html(val, maxlen=500):
            s = re.sub(r'<[^>]+>', '', str(val or ''))
            return s[:maxlen]

        raw_referrer = _strip_html(request.data.get('referrer', ''), 500)
        raw_lang = _strip_html(request.data.get('language', ''), 20)
        raw_tz = _strip_html(request.data.get('timezone', ''), 60)
        raw_sid = _strip_html(request.data.get('session_id', ''), 64)

        try:
            sw = int(screen_width) if screen_width else None
            sh = int(screen_height) if screen_height else None
            # Reject unreasonable values
            if sw and (sw < 0 or sw > 10000): sw = None
            if sh and (sh < 0 or sh > 10000): sh = None
        except (ValueError, TypeError):
            sw, sh = None, None

        pv = PageView.objects.create(
            path=path,
            referrer=raw_referrer,
            ip_address=ip or None,
            user_agent=ua_string,
            device_type=device_type,
            browser=browser[:80],
            os=os_name[:80],
            screen_width=sw,
            screen_height=sh,
            language=raw_lang,
            timezone=raw_tz,
            session_id=raw_sid,
        )

        # Resolve geo in background thread (non-blocking)
        if ip:
            threading.Thread(target=_resolve_geo_async, args=(pv.pk, ip), daemon=True).start()

        return Response({'ok': True})


class SiteStatView(APIView):
    """Public endpoint — returns site stats shown on Home/About/Portfolio."""
    throttle_classes = []

    def get(self, request):
        stat = SiteStat.get()
        return Response(SiteStatSerializer(stat).data)


class DashboardStatsView(APIView):
    """Protected dashboard stats endpoint."""
    throttle_classes = []

    def get(self, request):
        if not _check_auth(request):
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timezone.timedelta(days=7)
        month_start = today_start - timezone.timedelta(days=30)

        total_views = PageView.objects.count()
        views_today = PageView.objects.filter(timestamp__gte=today_start).count()
        views_week = PageView.objects.filter(timestamp__gte=week_start).count()
        views_month = PageView.objects.filter(timestamp__gte=month_start).count()

        # Unique visitors (by IP or session)
        unique_today = PageView.objects.filter(timestamp__gte=today_start).values('ip_address').distinct().count()
        unique_week = PageView.objects.filter(timestamp__gte=week_start).values('ip_address').distinct().count()
        unique_month = PageView.objects.filter(timestamp__gte=month_start).values('ip_address').distinct().count()

        top_pages = (
            PageView.objects.values('path')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )

        daily_views = (
            PageView.objects.filter(timestamp__gte=week_start)
            .annotate(date=TruncDate('timestamp'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )

        # Device breakdown (last 30 days)
        devices = list(
            PageView.objects.filter(timestamp__gte=month_start)
            .exclude(device_type='')
            .values('device_type')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        # Browser breakdown (last 30 days, top 8)
        browsers = list(
            PageView.objects.filter(timestamp__gte=month_start)
            .exclude(browser='')
            .values('browser')
            .annotate(count=Count('id'))
            .order_by('-count')[:8]
        )

        # Country breakdown (last 30 days, top 10)
        countries = list(
            PageView.objects.filter(timestamp__gte=month_start)
            .exclude(country='')
            .values('country')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )

        # Top referrers (last 30 days, top 10)
        referrers = list(
            PageView.objects.filter(timestamp__gte=month_start)
            .exclude(referrer='')
            .values('referrer')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )

        total_contacts = ContactMessage.objects.count()
        unread_contacts = ContactMessage.objects.filter(status='new').count()

        total_projects = Project.objects.count()
        in_progress_projects = Project.objects.filter(status='in_progress').count()
        completed_projects = Project.objects.filter(status='completed').count()

        return Response({
            'visits': {
                'total': total_views,
                'today': views_today,
                'this_week': views_week,
                'this_month': views_month,
                'unique_today': unique_today,
                'unique_week': unique_week,
                'unique_month': unique_month,
                'daily': [{'date': str(d['date']), 'count': d['count']} for d in daily_views],
                'devices': devices,
                'browsers': browsers,
                'countries': countries,
                'referrers': referrers,
            },
            'contacts': {
                'total': total_contacts,
                'unread': unread_contacts,
                'read': total_contacts - unread_contacts,
            },
            'projects': {
                'total': total_projects,
                'in_progress': in_progress_projects,
                'completed': completed_projects,
            },
            'top_pages': list(top_pages),
        })


class DashboardVisitorsView(APIView):
    """Protected — paginated visitor log with filtering."""
    throttle_classes = []

    def get(self, request):
        if not _check_auth(request):
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        qs = PageView.objects.all()

        # Filters
        path_filter = request.query_params.get('path')
        if path_filter:
            qs = qs.filter(path__icontains=path_filter)

        country_filter = request.query_params.get('country')
        if country_filter:
            qs = qs.filter(country__icontains=country_filter)

        device_filter = request.query_params.get('device')
        if device_filter:
            qs = qs.filter(device_type=device_filter)

        date_from = request.query_params.get('from')
        if date_from:
            qs = qs.filter(timestamp__date__gte=date_from)

        date_to = request.query_params.get('to')
        if date_to:
            qs = qs.filter(timestamp__date__lte=date_to)

        # Pagination (safe integer parsing)
        try:
            page_num = max(1, int(request.query_params.get('page', 1)))
        except (ValueError, TypeError):
            page_num = 1
        try:
            per_page = min(max(1, int(request.query_params.get('per_page', 50))), 100)
        except (ValueError, TypeError):
            per_page = 50
        total = qs.count()
        offset = (page_num - 1) * per_page
        visitors = qs[offset:offset + per_page]

        data = []
        for v in visitors:
            data.append({
                'id': v.id,
                'path': v.path,
                'referrer': v.referrer,
                'ip_address': v.ip_address,
                'timestamp': v.timestamp.isoformat(),
                'device_type': v.device_type,
                'browser': v.browser,
                'os': v.os,
                'country': v.country,
                'city': v.city,
                'screen_width': v.screen_width,
                'screen_height': v.screen_height,
                'language': v.language,
                'timezone': v.timezone,
                'session_id': v.session_id,
            })

        return Response({
            'results': data,
            'total': total,
            'page': page_num,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page if total > 0 else 1,
        })


class DashboardContactsView(APIView):
    """Protected — list all contacts."""
    throttle_classes = []

    def get(self, request):
        if not _check_auth(request):
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        contacts = ContactMessage.objects.all().values(
            'id', 'name', 'email', 'service', 'budget', 'message', 'status', 'created_at', 'ip_address'
        )
        return Response(list(contacts))


class DashboardContactUpdateView(APIView):
    """Protected — update contact status."""
    throttle_classes = []

    def patch(self, request, pk):
        if not _check_auth(request):
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            contact = ContactMessage.objects.get(pk=pk)
        except ContactMessage.DoesNotExist:
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status')
        valid = [c[0] for c in ContactMessage.Status.choices]
        if new_status not in valid:
            return Response({'detail': f'Invalid status. Must be one of: {valid}'}, status=status.HTTP_400_BAD_REQUEST)

        contact.status = new_status
        contact.save(update_fields=['status'])
        return Response({'id': contact.pk, 'status': contact.status})


class DashboardSiteStatUpdateView(APIView):
    """Protected — update site stats."""
    throttle_classes = []

    def get(self, request):
        if not _check_auth(request):
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        stat = SiteStat.get()
        return Response(SiteStatSerializer(stat).data)

    def patch(self, request):
        if not _check_auth(request):
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        stat = SiteStat.get()
        serializer = SiteStatSerializer(stat, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─── Dashboard Project CRUD ─────────────────────────────────────────────────

class DashboardProjectsView(APIView):
    """Protected — list all projects or create a new one."""
    throttle_classes = []

    def get(self, request):
        if not _check_auth(request):
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        projects = Project.objects.all()
        return Response(ProjectSerializer(projects, many=True).data)

    def post(self, request):
        if not _check_auth(request):
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = ProjectCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            project = serializer.save()
            return Response(ProjectSerializer(project).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DashboardProjectDetailView(APIView):
    """Protected — get, update or delete a single project."""
    throttle_classes = []

    def get(self, request, pk):
        if not _check_auth(request):
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            project = Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(ProjectSerializer(project).data)

    def patch(self, request, pk):
        if not _check_auth(request):
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            project = Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProjectCreateUpdateSerializer(project, data=request.data, partial=True)
        if serializer.is_valid():
            project = serializer.save()
            return Response(ProjectSerializer(project).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if not _check_auth(request):
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            project = Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ─── Public CMS Endpoints ─────────────────────────────────────────────────

class TestimonialsPublicView(APIView):
    throttle_classes = []

    def get(self, request):
        qs = Testimonial.objects.filter(is_active=True)
        return Response(TestimonialSerializer(qs, many=True).data)


class FAQPublicView(APIView):
    throttle_classes = []

    def get(self, request):
        qs = FAQ.objects.filter(is_active=True)
        return Response(FAQSerializer(qs, many=True).data)


class InsightBadgesPublicView(APIView):
    throttle_classes = []

    def get(self, request):
        qs = InsightBadge.objects.filter(is_active=True)
        return Response(InsightBadgeSerializer(qs, many=True).data)


class SiteContentPublicView(APIView):
    throttle_classes = []

    def get(self, request):
        content = SiteContent.get()
        return Response(SiteContentSerializer(content).data)


# ─── Dashboard CMS CRUD ──────────────────────────────────────────────────

class DashboardTestimonialsView(APIView):
    throttle_classes = []

    def get(self, request):
        if not _check_auth(request):
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(TestimonialSerializer(Testimonial.objects.all(), many=True).data)

    def post(self, request):
        if not _check_auth(request):
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = TestimonialSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DashboardTestimonialDetailView(APIView):
    throttle_classes = []

    def patch(self, request, pk):
        if not _check_auth(request):
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            obj = Testimonial.objects.get(pk=pk)
        except Testimonial.DoesNotExist:
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = TestimonialSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if not _check_auth(request):
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            obj = Testimonial.objects.get(pk=pk)
        except Testimonial.DoesNotExist:
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DashboardFAQsView(APIView):
    throttle_classes = []

    def get(self, request):
        if not _check_auth(request):
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(FAQSerializer(FAQ.objects.all(), many=True).data)

    def post(self, request):
        if not _check_auth(request):
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = FAQSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DashboardFAQDetailView(APIView):
    throttle_classes = []

    def patch(self, request, pk):
        if not _check_auth(request):
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            obj = FAQ.objects.get(pk=pk)
        except FAQ.DoesNotExist:
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = FAQSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if not _check_auth(request):
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            obj = FAQ.objects.get(pk=pk)
        except FAQ.DoesNotExist:
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DashboardBadgesView(APIView):
    throttle_classes = []

    def get(self, request):
        if not _check_auth(request):
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(InsightBadgeSerializer(InsightBadge.objects.all(), many=True).data)

    def post(self, request):
        if not _check_auth(request):
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = InsightBadgeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DashboardBadgeDetailView(APIView):
    throttle_classes = []

    def patch(self, request, pk):
        if not _check_auth(request):
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            obj = InsightBadge.objects.get(pk=pk)
        except InsightBadge.DoesNotExist:
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = InsightBadgeSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if not _check_auth(request):
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            obj = InsightBadge.objects.get(pk=pk)
        except InsightBadge.DoesNotExist:
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DashboardSiteContentView(APIView):
    throttle_classes = []

    def get(self, request):
        if not _check_auth(request):
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(SiteContentSerializer(SiteContent.get()).data)

    def patch(self, request):
        if not _check_auth(request):
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        content = SiteContent.get()
        serializer = SiteContentSerializer(content, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
