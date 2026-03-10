from django.conf import settings
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncDate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import PageView, SiteStat
from .serializers import SiteStatSerializer
from contact.models import ContactMessage
from portfolio.models import Project
from portfolio.serializers import ProjectSerializer, ProjectCreateUpdateSerializer


def _check_auth(request):
    """Simple bearer token auth against DASHBOARD_SECRET."""
    secret = getattr(settings, 'DASHBOARD_SECRET', '')
    auth = request.headers.get('Authorization', '')
    token = auth.removeprefix('Bearer ').strip()
    return bool(secret and token == secret)


class TrackPageView(APIView):
    throttle_classes = []

    def post(self, request):
        path = request.data.get('path', '/')
        if not path or len(path) > 255:
            return Response({'ok': False}, status=status.HTTP_400_BAD_REQUEST)

        # Skip tracking for dashboard/admin/api paths
        if path.startswith(('/dashboard', '/admin', '/api')):
            return Response({'ok': True})

        ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() \
             or request.META.get('REMOTE_ADDR')

        PageView.objects.create(
            path=path,
            referrer=request.data.get('referrer', '')[:500],
            ip_address=ip or None,
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
        )
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
                'daily': [{'date': str(d['date']), 'count': d['count']} for d in daily_views],
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
