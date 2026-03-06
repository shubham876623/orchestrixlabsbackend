from django.db import models


class PageView(models.Model):
    path = models.CharField(max_length=255, db_index=True)
    referrer = models.CharField(max_length=500, blank=True, default='')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True, default='')
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Page View'
        verbose_name_plural = 'Page Views'

    def __str__(self):
        return f'{self.path} @ {self.timestamp:%Y-%m-%d %H:%M}'


class SiteStat(models.Model):
    """Singleton-style model — only one row, editable from admin."""
    total_earnings = models.CharField(max_length=30, default='$100K+')
    total_hours = models.PositiveIntegerField(default=4828)
    total_jobs = models.PositiveIntegerField(default=143)
    years_experience = models.PositiveIntegerField(default=6)
    jss_score = models.PositiveIntegerField(default=100, help_text='Job Success Score (0-100)')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Site Stats'
        verbose_name_plural = 'Site Stats'

    def __str__(self):
        return f'Site Stats (updated {self.updated_at:%Y-%m-%d})'

    def save(self, *args, **kwargs):
        # Enforce singleton — always use pk=1
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
