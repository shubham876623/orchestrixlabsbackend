import logging
import threading

from django.conf import settings
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import AnonRateThrottle
from .models import ContactMessage
from .serializers import ContactMessageSerializer

logger = logging.getLogger(__name__)


class ContactRateThrottle(AnonRateThrottle):
    scope = 'contact'
    rate = '3/hour'


def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def _send_notification(msg_id):
    """Send founder notification; record success/failure on the ContactMessage row."""
    try:
        msg = ContactMessage.objects.get(pk=msg_id)
    except ContactMessage.DoesNotExist:
        logger.error('Contact notification skipped: message id=%s not found', msg_id)
        return

    if not settings.EMAIL_HOST_USER or not settings.NOTIFY_EMAIL:
        ContactMessage.objects.filter(pk=msg_id).update(
            notify_status=ContactMessage.NotifyStatus.SKIPPED,
            notify_error='EMAIL_HOST_USER or NOTIFY_EMAIL not configured',
        )
        logger.warning('Contact notification skipped for id=%s: email not configured', msg_id)
        return

    try:
        send_mail(
            subject=f'[Orchestrix Labs] New message from {msg.name}',
            message=(
                f'Name: {msg.name}\n'
                f'Email: {msg.email}\n'
                f'Service: {msg.service or "—"}\n'
                f'Budget: {msg.budget or "—"}\n\n'
                f'Message:\n{msg.message}'
            ),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.NOTIFY_EMAIL],
            fail_silently=False,
        )
        ContactMessage.objects.filter(pk=msg_id).update(
            notify_status=ContactMessage.NotifyStatus.SENT,
            notify_error='',
        )
        logger.info('Contact notification sent for id=%s', msg_id)
    except Exception as exc:
        err = str(exc)[:500]
        ContactMessage.objects.filter(pk=msg_id).update(
            notify_status=ContactMessage.NotifyStatus.FAILED,
            notify_error=err,
        )
        logger.exception('Contact notification failed for id=%s', msg_id)


class ContactView(APIView):
    throttle_classes = [ContactRateThrottle]

    def post(self, request):
        serializer = ContactMessageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        msg = serializer.save(ip_address=get_client_ip(request))

        # Persist first; notify in background. Lead never depends on SMTP success.
        threading.Thread(target=_send_notification, args=(msg.pk,), daemon=True).start()

        return Response(
            {'detail': 'Message received. We will reply within 24 hours.'},
            status=status.HTTP_201_CREATED,
        )
