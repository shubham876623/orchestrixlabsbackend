"""
Contact API tests — run locally with:
  python manage.py test contact.tests_contact_api -v 2

Uses test data only. Does not send live email (locmem backend).
"""
from django.core import mail
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from contact.models import ContactMessage


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    EMAIL_HOST_USER='test@orchestrixlabs.local',
    NOTIFY_EMAIL='founder@orchestrixlabs.local',
    REST_FRAMEWORK={
        'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
        'DEFAULT_THROTTLE_CLASSES': [],
        'DEFAULT_THROTTLE_RATES': {},
    },
)
class ContactApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Disable contact throttle for deterministic unit tests
        from contact.views import ContactView
        ContactView.throttle_classes = []
        self.url = '/api/contact/'
        self.valid = {
            'name': 'Test Lead',
            'email': 'test.lead@example.com',
            'service': 'Voice AI & Chatbots',
            'budget': '$1,000 – $5,000',
            'message': 'We need a voice agent for inbound restaurant orders and CRM logging.',
            'website': '',
        }

    def test_valid_submission_persists_and_notifies(self):
        res = self.client.post(self.url, self.valid, format='json')
        self.assertEqual(res.status_code, 201)
        msg = ContactMessage.objects.get(email='test.lead@example.com')
        self.assertEqual(msg.name, 'Test Lead')
        self.assertIn(msg.notify_status, [
            ContactMessage.NotifyStatus.SENT,
            ContactMessage.NotifyStatus.PENDING,
        ])
        # Thread may finish after response; run notifier synchronously if still pending
        if msg.notify_status == ContactMessage.NotifyStatus.PENDING:
            from contact.views import _send_notification
            _send_notification(msg.pk)
            msg.refresh_from_db()
        self.assertEqual(msg.notify_status, ContactMessage.NotifyStatus.SENT)
        self.assertEqual(len(mail.outbox), 1)

    def test_rejects_short_message(self):
        payload = {**self.valid, 'message': 'Too short'}
        res = self.client.post(self.url, payload, format='json')
        self.assertEqual(res.status_code, 400)
        self.assertIn('message', res.data)

    def test_rejects_missing_service(self):
        payload = {**self.valid, 'service': ''}
        res = self.client.post(self.url, payload, format='json')
        self.assertEqual(res.status_code, 400)

    def test_honeypot_rejects_bots(self):
        payload = {**self.valid, 'website': 'http://spam.example'}
        res = self.client.post(self.url, payload, format='json')
        self.assertEqual(res.status_code, 400)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_public_projects_hide_financials(self):
        from portfolio.models import Project
        Project.objects.create(
            title='Test Project',
            category='AI',
            status='completed',
            summary='Summary',
            project_value='$999',
            hours_worked=12,
            order=1,
        )
        res = self.client.get('/api/projects/')
        self.assertEqual(res.status_code, 200)
        row = res.data[0]
        self.assertNotIn('project_value', row)
        self.assertNotIn('hours_worked', row)
        self.assertNotIn('price_type', row)
