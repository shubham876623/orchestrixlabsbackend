"""
Management command to import Upwork contracts from CSV into the Project model.
Skips cancelled contracts and auto-categorizes based on title keywords.
"""
import csv
import re
from datetime import datetime
from pathlib import Path

from django.core.management.base import BaseCommand
from portfolio.models import Project


# ── Category mapping based on title keywords ──────────────────────────────────
CATEGORY_RULES = [
    # Voice AI & Chatbots — check first (more specific)
    (
        r'voice|synthflow|twilio|call.?center|receptionist|ai.?agent|ai.?hub|chatbot|chat.?bot|appointment|order.?taking',
        'Voice AI & Chatbots',
    ),
    # Machine Learning & AI
    (
        r'machine.?learning|deep.?learning|ml\b|nlp\b|model.?train|dreambooth|image.?background|forecast|'
        r'data.?analy|qualitative|nvivo|maxqda|vertex.?ai|sagemaker|openai|psychiatrist|ai.?framework|'
        r'statistics|analytics.?pro|accuracy.?of.?the.?model|cad',
        'Machine Learning & AI',
    ),
    # Web Scraping & Automation
    (
        r'scrap|crawl|spider|selenium|puppeteer|bot\b|data.?extract|data.?capture|data.?collect|'
        r'data.?min|linkedin|facebook.*scrap|scrub|engagement.?scrap|browser.?ext|chrome.?driver|'
        r'proxy|document.?extract|text.?from.?image|extract.?test|web.?scrape',
        'Web Scraping & Automation',
    ),
    # Workflow Automation
    (
        r'zapier|automat(?:e|ion)|data.?entry|workflow|postman|etl|databricks|hubspot|'
        r'omni.?channel|follow.?unfollow|outreach|form.?entries|email.?cross|pinescript|'
        r'google.?cloud|oauth',
        'Workflow Automation',
    ),
    # Full-Stack Development (catch-all for dev work)
    (
        r'django|flask|full.?stack|frontend|web.?app|website|docker|api\b|database|postgresql|'
        r'mysql|jwt|microservice|python.?dev|app.?dev|logicapp|script|code|excel|csv|'
        r'product.?price|research|competitor',
        'Full-Stack Development',
    ),
]


def categorize(title):
    title_lower = title.lower()
    for pattern, category in CATEGORY_RULES:
        if re.search(pattern, title_lower):
            return category
    return 'Full-Stack Development'  # default fallback


def parse_date(date_str):
    """Parse ISO date string to date object."""
    if not date_str or not date_str.strip():
        return None
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
    except (ValueError, TypeError):
        return None


def parse_price(val):
    """Parse price string like '130.00' or '1,000.00' to clean string."""
    if not val or not val.strip():
        return ''
    cleaned = val.strip().replace(',', '')
    try:
        amount = float(cleaned)
        if amount >= 1000:
            return f'${amount:,.2f}'
        return f'${amount:.2f}'
    except (ValueError, TypeError):
        return ''


class Command(BaseCommand):
    help = 'Import Upwork contracts from CSV into Project model'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv',
            type=str,
            default='contracts.csv',
            help='Path to the contracts CSV file',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete all existing projects before importing',
        )

    def handle(self, *args, **options):
        csv_path = Path(options['csv'])
        if not csv_path.exists():
            # Try relative to manage.py directory
            csv_path = Path(__file__).resolve().parents[3] / options['csv']
        if not csv_path.exists():
            self.stderr.write(self.style.ERROR(f'CSV file not found: {options["csv"]}'))
            return

        if options['clear']:
            deleted, _ = Project.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Deleted {deleted} existing projects.'))

        # Skip statuses that indicate cancelled/refunded contracts
        skip_milestones = {'CancelledByClient', 'CancelledByFreelancer'}

        created = 0
        skipped = 0
        existing_titles = set(Project.objects.values_list('title', flat=True))

        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                title = row.get('Title', '').strip()
                if not title:
                    skipped += 1
                    continue

                # Skip cancelled contracts
                milestone = row.get('Milestone Status', '').strip()
                refund = row.get('Refund status (from project funds)', '').strip()
                if milestone in skip_milestones and refund == 'Accepted':
                    self.stdout.write(f'  Skipping cancelled: {title}')
                    skipped += 1
                    continue

                # Skip if already exists (by title)
                if title in existing_titles:
                    skipped += 1
                    continue

                # Parse fields
                contract_status = row.get('Status', '').strip()
                contract_type = row.get('Contract type', '').strip()
                hourly_rate = row.get('Hourly Rate', '').strip()
                fixed_price = row.get('Fixed Price Amount Agreed', '').strip()
                weekly_limit = row.get('Weekly Limit', '').strip()
                start_date = parse_date(row.get('Start Date', ''))
                end_date = parse_date(row.get('End Date', ''))
                client_name = row.get('Contact person', '').strip()

                # Map status
                if contract_status in ('Active', 'Paused'):
                    project_status = 'in_progress'
                else:
                    project_status = 'completed'

                # Price type
                if contract_type == 'Fixed Price' and fixed_price:
                    price_type = 'Fixed price'
                    project_value = parse_price(fixed_price)
                elif hourly_rate:
                    price_type = f'${float(hourly_rate):.2f} /hr'
                    project_value = ''
                else:
                    price_type = ''
                    project_value = ''

                # Weekly limit as hours
                hours = None
                if weekly_limit:
                    try:
                        h = int(float(weekly_limit))
                        if h > 0:
                            hours = h
                    except (ValueError, TypeError):
                        pass

                # Category
                category = categorize(title)

                # Create project
                Project.objects.create(
                    title=title,
                    category=category,
                    status=project_status,
                    price_type=price_type,
                    project_value=project_value,
                    hours_worked=hours,
                    start_date=start_date,
                    completion_date=end_date,
                    client_name=client_name.split()[0] if client_name else '',  # First name only
                    order=0,
                )
                existing_titles.add(title)
                created += 1

        self.stdout.write(self.style.SUCCESS(
            f'Done! Created {created} projects, skipped {skipped}.'
        ))
