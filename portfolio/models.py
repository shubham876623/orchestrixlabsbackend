from django.db import models


class Project(models.Model):
    CATEGORY_CHOICES = [
        ('Voice AI & Chatbots', 'Voice AI & Chatbots'),
        ('Machine Learning & AI', 'Machine Learning & AI'),
        ('Web Scraping & Automation', 'Web Scraping & Automation'),
        ('Full-Stack Development', 'Full-Stack Development'),
        ('Workflow Automation', 'Workflow Automation'),
    ]

    title = models.CharField(max_length=255)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, db_index=True)
    summary = models.TextField()
    description = models.TextField()
    tech = models.JSONField(default=list)
    highlights = models.JSONField(default=list)
    impact = models.JSONField(default=list)
    featured = models.BooleanField(default=False, db_index=True)
    order = models.PositiveIntegerField(default=0, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'

    def __str__(self):
        return self.title
