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
    {
        "id": 47,
        "title": "Research of competitor success models",
        "rating": 5.0,
        "review": "Experienced coder for ai related projects offering full stack development, great communicator and cooperators.",
        "summary": "Conducted competitive analysis of existing text/voice-to-CAD models in the market — evaluated performance levels, identified gaps, and recommended a strategic pathway to success.",
        "job_description": "Client needed to gauge the performance level of competitor 'text/voice to CAD' models that exist in the market and suggest a clear pathway to success for their own product.",
        "deliverables": "Researched and benchmarked existing text-to-CAD and voice-to-CAD solutions. Analyzed strengths, weaknesses, and feature gaps across competitors. Delivered a comprehensive report with performance evaluations and a strategic roadmap for building a competitive product.",
        "tech": ["Market Research", "AI/ML Analysis", "Competitive Intelligence", "CAD Technology", "Strategic Planning"],
    },
    {
        "id": 69,
        "title": "Python + PostgreSQL Project: Fetch Top-Selling Amazon Saudi Products via API",
        "rating": 5.0,
        "review": "Good freelancer",
        "summary": "Built a multi-phase data pipeline to fetch top-selling products from Amazon Saudi Arabia via PA API 5.0, store in PostgreSQL, and export to CSV/Excel — scalable to 10,000+ products.",
        "job_description": "Client needed a Python solution to fetch top-selling products from Amazon Saudi Arabia using PA API 5.0, store data in PostgreSQL with scalable schema design, handle API rate limits, and provide CSV/Excel export with full documentation.",
        "deliverables": "Built Python script to fetch product data (title, ASIN, price, rating, sales rank, URL) from Amazon PA API with rate limiting and retry logic. Designed efficient PostgreSQL schema for products, categories, and prices scalable to 10,000+ records. Implemented CSV/Excel export and provided complete setup documentation for periodic data updates.",
        "tech": ["Python", "PostgreSQL", "Amazon PA API 5.0", "Data Pipeline", "Rate Limiting", "CSV/Excel Export"],
    },
    {
        "id": 144,
        "title": "AI Voice Agent Integration Expert Needed for Synthflow Project",
        "rating": 4.0,
        "review": "Experienced coder and automation professional. Familiar with Retell AI.",
        "summary": "Integrated AI Voice Agents using Synthflow and Retell AI for an Australian client — built seamless voice interactions as part of an ongoing development partnership to enhance AI capabilities.",
        "job_description": "Client sought an experienced developer to integrate AI Voice Agents using Synthflow technology. Required strong understanding of voice technologies, experience creating seamless voice interactions, and interest in a long-term collaboration to enhance AI capabilities.",
        "deliverables": "Integrated Synthflow AI voice agents with client systems. Built seamless voice interaction workflows for automated conversations. Configured Retell AI for enhanced voice processing. Established ongoing development partnership for continued AI capability improvements.",
        "tech": ["Synthflow", "Retell AI", "Voice AI", "Python", "API Integration", "Automation"],
    },
    {
        "id": 27,
        "title": "Test our website services manually in India",
        "rating": None,
        "review": "",
        "summary": "Conducted comprehensive manual QA testing of a website across desktop and mobile devices — identified bugs, usability issues, and provided improvement recommendations.",
        "job_description": "Client needed a detail-oriented tester to manually test their website across multiple devices and browsers. Required functional, UI/UX, regression, and cross-browser testing with documented bug reports including screenshots and video recordings.",
        "deliverables": "Performed thorough manual testing across desktop and mobile. Documented bugs and usability issues with screenshots. Conducted functional, UI/UX, regression, and cross-browser testing. Provided actionable improvement suggestions for site usability and user experience.",
        "tech": ["Manual QA Testing", "Cross-Browser Testing", "Mobile Testing", "Bug Reporting", "UI/UX Review"],
    },
    {
        "id": 106,
        "title": "Example Django JWT MySQL REST API with test cases",
        "rating": None,
        "review": "",
        "summary": "Built a complete Django REST API example with JWT authentication, MySQL database, CRUD endpoints for User and Book models, and comprehensive test cases.",
        "job_description": "Client needed an example Django REST API project with JWT user authentication, MySQL database, CRUD endpoints (Create, Read, Update, Delete), User and Book models, and full test case coverage.",
        "deliverables": "Developed a complete Django REST API with JWT authentication flow. Configured MySQL database with User and Book models. Built full CRUD endpoints with proper validation. Wrote comprehensive test cases covering all endpoints and auth flows.",
        "tech": ["Django", "Django REST Framework", "JWT", "MySQL", "Python", "Unit Testing"],
    },
    {
        "id": 145,
        "title": "AI Hub Development: Build and Monetize AI Bot Interaction Platform",
        "rating": 5.0,
        "review": "Clear communication and sound insights",
        "summary": "Developed an AI Hub platform where users interact with multiple AI bots — featuring free-tier access with paid upgrades, payment integration, and a scalable architecture.",
        "job_description": "Client wanted to create an 'AI Hub' where users can interact with a selection of AI bots. The platform needed limited free interactions with the option for users to pay for extended access, requiring AI development and payment integration expertise.",
        "deliverables": "Built an AI Hub platform with multiple bot selection and interaction. Implemented free-tier usage limits with paid upgrade flow. Integrated payment processing for extended access. Designed scalable architecture for adding new AI agents over time.",
        "tech": ["Python", "OpenAI API", "Payment Integration", "Full-Stack Development", "Scalable Architecture"],
    },
    {
        "id": 25,
        "title": "Twilio Voice Integration for AI Receptionist (Emma)",
        "rating": 3.6,
        "review": "Shubham assisted with the initial voice assistant integration using Twilio Studio. While we eventually moved the project to another developer, his early contributions were helpful. With stronger time management and communication, he has potential for future engagements.",
        "summary": "Assisted with initial Twilio Voice integration for an AI-powered receptionist (Emma) — set up call routing, Twilio Studio flows, and GPT-4 voice response integration for a condo management platform.",
        "job_description": "Client was launching an AI receptionist (Emma) for a condo management platform. Needed Twilio Voice setup with call routing, AI-generated voice replies via ChatGPT API, fallback routing to voicemail, and call logging with transcripts stored in Supabase.",
        "deliverables": "Set up Twilio voice number and call routing configuration. Integrated Twilio Studio with OpenAI GPT-4 for AI-generated voice responses. Configured initial call flow logic with fallback routing. Contributed to the foundational voice AI architecture.",
        "tech": ["Twilio", "Twilio Studio", "OpenAI GPT-4", "React", "Supabase", "Voice AI", "Webhooks"],
    },
    {
        "id": 29,
        "title": "Support vertexai custom model deployment (same day)",
        "rating": 5.0,
        "review": "",
        "summary": "Resolved urgent deployment issues for custom ML models on Google Vertex AI — deployed fine-tuned models using custom containers with same-day turnaround.",
        "job_description": "Client faced sticky issues deploying custom models and fine-tunes to Google Vertex AI using custom containers. Needed someone with hands-on Vertex AI deployment experience for an urgent same-day fix, with potential for ongoing work deploying multiple models.",
        "deliverables": "Diagnosed and resolved Vertex AI custom container deployment issues. Successfully deployed fine-tuned models to Vertex AI endpoints. Configured custom container settings for production readiness. Delivered same-day with potential path for deploying additional models.",
        "tech": ["Google Vertex AI", "Custom Containers", "ML Deployment", "Docker", "Python", "GCP"],
    },
    {
        "id": 130,
        "title": "Build a Private Psychiatrist ChatGPT Assistant",
        "rating": 5.0,
        "review": "A good freelancer. Available to speak.",
        "summary": "Built a private psychiatrist AI assistant powered by GPT-4 with document upload, vector database storage, and semantic search — serving as a continuously growing clinical and academic resource.",
        "job_description": "Client needed a Private Psychiatrist ChatGPT Assistant using GPT-4 via OpenAI API. Required document upload (PDF, Word, text), permanent storage in a local vector database, semantic search across documents, and GPT-4 integration combining private knowledge with general psychiatric knowledge.",
        "deliverables": "Built a GPT-4 powered psychiatrist assistant with document upload and processing (PDF, Word, text). Implemented local vector database for permanent document storage. Added semantic search across all uploaded materials. Integrated RAG pipeline combining private knowledge retrieval with GPT-4's general medical knowledge for comprehensive clinical responses.",
        "tech": ["OpenAI GPT-4", "Python", "Vector Database", "RAG", "LangChain", "Document Processing", "Semantic Search"],
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
