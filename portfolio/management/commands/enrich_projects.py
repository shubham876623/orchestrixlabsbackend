"""
Management command to enrich projects with summaries, reviews, ratings, tech stacks.
Run once per batch — safe to re-run (updates by ID).
"""
from django.core.management.base import BaseCommand
from portfolio.models import Project


ENRICHMENTS = [
    {
        "id": 146,
        "title": "AI Agent for HR & Personal Assistant",
        "rating": 5.0,
        "review": "",
        "summary": "Built a bilingual AI agent (Arabic & English) to handle HR tasks and personal productivity — integrated with Gmail, Google Drive, Calendar, and MS Office for a client in Saudi Arabia.",
        "job_description": "Client needed a custom AI Agent to assist with HR & Organizational Development work and personal productivity. The agent had to work in both Arabic and English and integrate with Gmail/Outlook, Google Drive/Docs/Sheets, Calendar, and MS Office.",
        "deliverables": "Developed a fully functional bilingual AI agent with natural language understanding in Arabic and English. Integrated with Gmail, Google Calendar, Google Drive, and MS Office suite. Built HR workflow automation including document generation, scheduling, and organizational task management.",
        "tech": ["Python", "OpenAI API", "LangChain", "Google APIs", "Microsoft Graph API", "NLP"],
    },
    {
        "id": 11,
        "title": "Web Scraping for List Creation",
        "rating": 5.0,
        "review": "I really appreciated the opportunity to work together. The job was completed on time and as promised!",
        "summary": "Scraped multiple websites to compile structured data lists with high accuracy — delivered on time with a bonus from the client.",
        "job_description": "Client needed a skilled freelancer to scrape specific websites and create organized lists of relevant data. Required experience in web scraping and data entry with strong attention to detail and accuracy.",
        "deliverables": "Built custom web scrapers to extract targeted data from multiple websites. Cleaned and structured the scraped data into organized lists. Delivered accurate, formatted datasets ready for the client's use — completed ahead of schedule.",
        "tech": ["Python", "Selenium", "BeautifulSoup", "Pandas", "Data Cleaning"],
    },
    {
        "id": 49,
        "title": "Qualitative Data Analyst Needed for NVivo/MAXQDA Coding",
        "rating": 5.0,
        "review": "Shubham delivered high-quality work on the qualitative analysis project. He had a strong understanding of qualitative research methods, provided well-structured and insightful analysis and ensured that all deliverables were aligned with the project requirements.",
        "summary": "Performed qualitative data analysis using NVivo for academic research — coded large datasets, generated themes, and delivered publication-ready insights.",
        "job_description": "Client sought a skilled qualitative data analyst to assist with data analysis and coding using NVivo or MAXQDA. Required handling large datasets, coding qualitative data, generating themes, and providing insights suitable for academic publication.",
        "deliverables": "Coded qualitative datasets using NVivo with systematic thematic analysis. Identified key themes and patterns across the data. Delivered well-structured analysis with insights aligned to academic publication standards and project requirements.",
        "tech": ["NVivo", "Qualitative Analysis", "Thematic Coding", "Research Methods"],
    },
    {
        "id": 26,
        "title": "Text to CAD",
        "rating": 5.0,
        "review": "Good communicator, ready with innovative ideas, worked with integrity and was honest about results. Reliable collaborator.",
        "summary": "Built an end-to-end Text-to-CAD pipeline — users describe a part in plain English and the system generates a 3D CAD model using LLM parsing and CadQuery, exposed via a FastAPI REST API.",
        "job_description": "Client needed an AI-powered system to convert text prompts into 3D CAD models. Required an LLM-based text parser, clarification logic for missing dimensions, CAD primitive mapping, model generation with CadQuery, a REST API endpoint, error handling, testing, deployment, and documentation.",
        "deliverables": "Built LLM-based text parser converting natural language to structured JSON specs. Implemented clarifier logic to prompt users for missing dimensions and features. Mapped structured schemas to CAD primitives and generated 3D models via CadQuery with file export. Developed FastAPI REST API with /generate-cad endpoint. Added robust error handling, unit tests, CLI tool, and deployment on cloud infrastructure with full API documentation.",
        "tech": ["Python", "FastAPI", "CadQuery", "OpenAI API", "LangChain", "REST API", "Docker", "3D Modeling"],
    },
]


class Command(BaseCommand):
    help = 'Enrich projects with summaries, reviews, ratings, and tech stacks'

    def handle(self, *args, **options):
        for item in ENRICHMENTS:
            try:
                project = Project.objects.get(pk=item['id'])
            except Project.DoesNotExist:
                self.stderr.write(self.style.ERROR(f"Project {item['id']} not found: {item['title']}"))
                continue

            project.rating = item['rating']
            project.review = item['review']
            project.summary = item['summary']
            project.job_description = item['job_description']
            project.deliverables = item['deliverables']
            project.tech = item['tech']
            project.save()

            self.stdout.write(self.style.SUCCESS(f"Enriched: {project.title}"))

        self.stdout.write(self.style.SUCCESS(f"\nDone! Enriched {len(ENRICHMENTS)} projects."))
