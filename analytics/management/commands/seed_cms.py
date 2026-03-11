"""Seed CMS tables with default content (testimonials, FAQs, badges, site content)."""
from django.core.management.base import BaseCommand
from analytics.models import Testimonial, FAQ, InsightBadge, SiteContent


TESTIMONIALS = [
    {
        'client_name': 'Verified Upwork Client',
        'client_role': 'AI Framework Development',
        'rating': 5.0,
        'quote': "Love working with Shubham, he's the best at what he does and he always tries his best! Thanks Shubham!",
        'tags': ['Collaborative', 'Committed to Quality'],
        'source': 'Upwork',
        'featured': True,
        'order': 1,
    },
    {
        'client_name': 'Verified Upwork Client',
        'client_role': 'Qualitative Data Analysis',
        'rating': 5.0,
        'quote': 'Shubham delivered high-quality work on the qualitative analysis project. He had a strong understanding of qualitative research methods, provided well-structured and insightful analysis and ensured that all deliverables were aligned with the project requirements.',
        'tags': ['Committed to Quality'],
        'source': 'Upwork',
        'featured': True,
        'order': 2,
    },
    {
        'client_name': 'Verified Upwork Client',
        'client_role': 'Web Scraping & Data Collection',
        'rating': 5.0,
        'quote': 'He was excellent to work with and would highly recommend. Fast, reliable, and did great work.',
        'tags': ['Reliable', 'Committed to Quality', 'Solution Oriented'],
        'source': 'Upwork',
        'featured': True,
        'order': 3,
    },
    {
        'client_name': 'Verified Upwork Client',
        'client_role': 'AI & Full-Stack Development',
        'rating': 5.0,
        'quote': 'Experienced coder for AI related projects offering full stack development, great communicator and cooperator.',
        'tags': ['Clear Communicator', 'Collaborative'],
        'source': 'Upwork',
        'featured': True,
        'order': 4,
    },
    {
        'client_name': 'Verified Upwork Client',
        'client_role': 'Django Backend Development',
        'rating': 5.0,
        'quote': 'Shubham is a skilled developer who completed the project ahead of schedule. He understood the requirements immediately and delivered clean, well-documented code.',
        'tags': ['Reliable', 'Solution Oriented'],
        'source': 'Upwork',
        'featured': True,
        'order': 5,
    },
    {
        'client_name': 'Verified Upwork Client',
        'client_role': 'Python Automation',
        'rating': 5.0,
        'quote': 'Really great experience. Shubham was proactive in flagging potential issues early and always kept us in the loop. Will definitely hire again.',
        'tags': ['Collaborative', 'Accountable for Outcomes'],
        'source': 'Upwork',
        'featured': True,
        'order': 6,
    },
]

FAQS = [
    {
        'question': 'How long does a typical project take?',
        'answer': 'Most projects take 2-6 weeks depending on scope. Simple automations or scrapers can be done in days. Complex AI systems or full-stack platforms may take 2-3 months. We always give you a clear timeline upfront.',
        'order': 1,
    },
    {
        'question': 'What does pricing look like?',
        'answer': 'We work both hourly ($25/hr on Upwork) and fixed-price. Most clients prefer fixed-price for well-defined projects. We scope everything clearly before starting — no surprise bills.',
        'order': 2,
    },
    {
        'question': 'What tech stack do you use?',
        'answer': 'Python is our core — Django, FastAPI, Flask for backends. React + Tailwind for frontends. OpenAI, LangChain, FAISS for AI. Selenium, Playwright, Scrapy for scraping. AWS, Docker, PostgreSQL for infrastructure.',
        'order': 3,
    },
    {
        'question': 'Do you offer post-launch support?',
        'answer': 'Yes. Every project includes 2 weeks of free bug-fix support after delivery. For ongoing maintenance, we offer affordable retainer plans. Many clients continue working with us for months after the initial project.',
        'order': 4,
    },
    {
        'question': 'Can you work with our existing codebase?',
        'answer': 'Absolutely. We frequently jump into existing projects — fixing bugs, adding features, optimizing performance, or migrating to modern stacks. We are comfortable with legacy code and messy repos.',
        'order': 5,
    },
]

BADGES = [
    {'label': 'Collaborative', 'count': 28, 'order': 1},
    {'label': 'Clear Communicator', 'count': 24, 'order': 2},
    {'label': 'Committed to Quality', 'count': 23, 'order': 3},
    {'label': 'Reliable', 'count': 18, 'order': 4},
    {'label': 'Solution Oriented', 'count': 15, 'order': 5},
    {'label': 'Accountable for Outcomes', 'count': 8, 'order': 6},
    {'label': 'Professional', 'count': 5, 'order': 7},
]


class Command(BaseCommand):
    help = 'Seed CMS tables with default content'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Delete existing data before seeding')

    def handle(self, *args, **options):
        if options['clear']:
            Testimonial.objects.all().delete()
            FAQ.objects.all().delete()
            InsightBadge.objects.all().delete()
            self.stdout.write('Cleared existing CMS data.')

        # Testimonials
        if not Testimonial.objects.exists():
            for t in TESTIMONIALS:
                Testimonial.objects.create(**t)
            self.stdout.write(self.style.SUCCESS(f'Created {len(TESTIMONIALS)} testimonials'))
        else:
            self.stdout.write('Testimonials already exist — skipping.')

        # FAQs
        if not FAQ.objects.exists():
            for f in FAQS:
                FAQ.objects.create(**f)
            self.stdout.write(self.style.SUCCESS(f'Created {len(FAQS)} FAQs'))
        else:
            self.stdout.write('FAQs already exist — skipping.')

        # Badges
        if not InsightBadge.objects.exists():
            for b in BADGES:
                InsightBadge.objects.create(**b)
            self.stdout.write(self.style.SUCCESS(f'Created {len(BADGES)} badges'))
        else:
            self.stdout.write('Badges already exist — skipping.')

        # SiteContent singleton
        SiteContent.get()
        self.stdout.write(self.style.SUCCESS('SiteContent singleton initialized.'))
