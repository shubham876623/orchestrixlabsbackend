import threading

from django.conf import settings
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import AnonRateThrottle
from .serializers import ContactMessageSerializer


class ContactRateThrottle(AnonRateThrottle):
    rate = '3/hour'


def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def _send_notification(msg):
    """Send email in a background thread so it never blocks the response."""
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
            fail_silently=True,
        )
    except Exception:
        pass


class ContactView(APIView):
    throttle_classes = [ContactRateThrottle]

    def post(self, request):
        serializer = ContactMessageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        msg = serializer.save(ip_address=get_client_ip(request))

        # Send email in background thread — never block the API response
        if settings.EMAIL_HOST_USER:
            threading.Thread(target=_send_notification, args=(msg,), daemon=True).start()

        return Response({'detail': 'Message received. We will reply within 24 hours.'}, status=status.HTTP_201_CREATED)
