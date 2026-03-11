from django.db import models


class PageView(models.Model):
    path = models.CharField(max_length=255, db_index=True)
    referrer = models.CharField(max_length=500, blank=True, default='')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True, default='')
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    # Parsed from user-agent
    device_type = models.CharField(max_length=20, blank=True, default='')  # desktop, mobile, tablet, bot
    browser = models.CharField(max_length=80, blank=True, default='')
    os = models.CharField(max_length=80, blank=True, default='')

    # Geo (resolved from IP)
    country = models.CharField(max_length=100, blank=True, default='')
    city = models.CharField(max_length=150, blank=True, default='')

    # Sent by frontend
    screen_width = models.PositiveIntegerField(null=True, blank=True)
    screen_height = models.PositiveIntegerField(null=True, blank=True)
    language = models.CharField(max_length=20, blank=True, default='')
    timezone = models.CharField(max_length=60, blank=True, default='')

    # Session tracking
    session_id = models.CharField(max_length=64, blank=True, default='', db_index=True)

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


# ─── CMS Models ──────────────────────────────────────────────────────────────

class Testimonial(models.Model):
    """Client testimonials displayed on Home & Reviews pages."""
    client_name = models.CharField(max_length=150)
    client_role = models.CharField(max_length=150, blank=True, default='')
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=5.0)
    quote = models.TextField()
    tags = models.JSONField(default=list, blank=True)
    source = models.CharField(max_length=50, default='Upwork')
    featured = models.BooleanField(default=False, db_index=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Testimonial'

    def __str__(self):
        return f'{self.client_name} — {self.rating}★'


class FAQ(models.Model):
    """FAQs displayed on the Services page."""
    question = models.CharField(max_length=500)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'

    def __str__(self):
        return self.question[:80]


class InsightBadge(models.Model):
    """Upwork insight/skill badges shown on multiple pages."""
    label = models.CharField(max_length=100)
    count = models.PositiveIntegerField(default=0)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', '-count']
        verbose_name = 'Insight Badge'

    def __str__(self):
        return f'{self.label} ({self.count})'


class SiteContent(models.Model):
    """Singleton — editable page content (hero text, about, contact info, etc.)."""

    # Home hero
    hero_headline = models.CharField(max_length=300, default='Build Smarter. Scale Faster. With AI.')
    hero_subheadline = models.TextField(default='Orchestrix Labs builds production-ready AI systems, voice bots, automation pipelines, and full-stack platforms — engineered to perform from day one.')
    hero_cta_primary = models.CharField(max_length=100, default='See Our Work')
    hero_cta_secondary = models.CharField(max_length=100, default='Start a Project')

    # About page
    about_headline = models.CharField(max_length=300, default='We turn complex problems into intelligent software.')
    about_story = models.TextField(default='', blank=True, help_text='Main about page narrative. Supports paragraphs separated by newlines.')
    about_values = models.JSONField(default=list, blank=True, help_text='List of {title, description} objects')

    # Contact info
    contact_email = models.EmailField(default='contact@orchestrixlabs.com')
    contact_linkedin = models.URLField(max_length=500, blank=True, default='')
    contact_github = models.URLField(max_length=500, blank=True, default='')
    contact_upwork = models.URLField(max_length=500, blank=True, default='')

    # Services page
    services_headline = models.CharField(max_length=300, default='Everything you need to build an intelligent business.')
    services_data = models.JSONField(default=list, blank=True, help_text='Full services array [{id, title, tagline, description, features, tools, color, accent}]')
    process_steps = models.JSONField(default=list, blank=True, help_text='Process steps [{step, title, description}]')

    # SEO / global
    site_name = models.CharField(max_length=100, default='Orchestrix Labs')
    site_tagline = models.CharField(max_length=300, default='AI-Powered Software Development Agency')

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Site Content'
        verbose_name_plural = 'Site Content'

    def __str__(self):
        return f'Site Content (updated {self.updated_at:%Y-%m-%d})'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
