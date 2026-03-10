from django.db import models


class Project(models.Model):
    CATEGORY_CHOICES = [
        ('Voice AI & Chatbots', 'Voice AI & Chatbots'),
        ('Machine Learning & AI', 'Machine Learning & AI'),
        ('Web Scraping & Automation', 'Web Scraping & Automation'),
        ('Full-Stack Development', 'Full-Stack Development'),
        ('Workflow Automation', 'Workflow Automation'),
    ]

    class Status(models.TextChoices):
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'

    title = models.CharField(max_length=255)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IN_PROGRESS, db_index=True)
    summary = models.TextField(blank=True, default='')
    description = models.TextField(blank=True, default='')
    tech = models.JSONField(default=list)
    highlights = models.JSONField(default=list)
    impact = models.JSONField(default=list)
    featured = models.BooleanField(default=False, db_index=True)
    order = models.PositiveIntegerField(default=0, db_index=True)

    # Client info
    client_name = models.CharField(max_length=150, blank=True, default='')
    rating = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)
    review = models.TextField(blank=True, default='')
    tags = models.JSONField(default=list, blank=True)

    # Project details
    project_value = models.CharField(max_length=50, blank=True, default='')
    hours_worked = models.PositiveIntegerField(null=True, blank=True)
    price_type = models.CharField(max_length=20, blank=True, default='')  # "Fixed price" or "$25.00 /hr"
    start_date = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)

    # Extended detail fields
    job_description = models.TextField(blank=True, default='')
    deliverables = models.TextField(blank=True, default='')
    live_url = models.URLField(max_length=500, blank=True, default='')
    upwork_url = models.URLField(max_length=500, blank=True, default='')
    images = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-completion_date', '-start_date', 'order', 'id']
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'

    def __str__(self):
        return self.title
