from django.db import models


class ContactMessage(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', 'New'
        DISCUSSION = 'discussion', 'Discussion'
        IN_PROGRESS = 'in_progress', 'In Progress'
        STARTED_WORK = 'started_work', 'Started Work'
        COMPLETED = 'completed', 'Completed'
        ARCHIVED = 'archived', 'Archived'

    class NotifyStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SENT = 'sent', 'Sent'
        FAILED = 'failed', 'Failed'
        SKIPPED = 'skipped', 'Skipped'

    name = models.CharField(max_length=120)
    email = models.EmailField()
    service = models.CharField(max_length=100, blank=True)
    budget = models.CharField(max_length=50, blank=True)
    message = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    notify_status = models.CharField(
        max_length=20,
        choices=NotifyStatus.choices,
        default=NotifyStatus.PENDING,
        help_text='Tracks whether founder email notification succeeded.',
    )
    notify_error = models.CharField(max_length=500, blank=True, default='')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'

    def __str__(self):
        return f"{self.name} — {self.service or 'General'} ({self.created_at.strftime('%Y-%m-%d')})"
