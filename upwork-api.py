#!/usr/bin/env python3
"""
Konan Upwork Agent (production-refined)

Improvements:
- Enhanced job scoring with client-quality inference (from RSS text signals)
- Advanced proposal personalization (problem-aware, question-driven)
- Stronger demo generator (creates realistic artifacts: CSV, script, README)
- RSS optimization: extracts additional signals from description text
- Job age filter, job prioritization tiers
- Target job category filtering (easy/medium)
- Connect spending control
- Human review safeguard
"""

import os
import re
import json
import time
import uuid
import hashlib
import sqlite3
import logging
import requests

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

# ---------------------------------------
# CONFIG
# ---------------------------------------

# Multiple RSS feeds for different keywords
TARGET_KEYWORDS = [
    "research assistant",
    "lead generation",
    "data scraping",
    "content repurposing",
    "cold outreach",
    "virtual assistant",
    "excel",
    "google sheets",
    "pdf",
    "notion",
    "data entry",
    "email automation",
    "social media",
    "qa",
    "webhook",
]

# Build RSS URLs for each keyword
UPWORK_RSS_URLS = [f"https://www.upwork.com/ab/feed/jobs/rss?q={kw.replace(' ', '+')}" for kw in TARGET_KEYWORDS]

DATABASE_FILE = "konan_agent.db"

SCAN_INTERVAL = 600
MAX_CONNECTS_PER_DAY = 120
MAX_CONNECT_COST = 6  # Accept jobs costing 0-6 connects

MIN_SCORE_THRESHOLD = 6
DEMO_TRIGGER_SCORE = 8

# Discord webhook for alerts
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1475680076589830300/"

# Templates folder
TEMPLATES_DIR = "templates"

LOG_LEVEL = logging.INFO

TARGET_JOBS = {
    "easy": [
        "research assistant",
        "lead generation",
        "data scraping",
        "content repurposing",
        "cold outreach",
        "virtual assistant",
    ],
    "medium": [
        "excel",
        "google sheets",
        "pdf",
        "notion",
        "data entry",
        "email automation",
        "social media",
        "qa",
        "webhook",
    ],
}

# ---------------------------------------
# LOGGING
# ---------------------------------------

logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger("konan")

# ---------------------------------------
# DATABASE
# ---------------------------------------

class Database:

    def __init__(self):

        self.conn = sqlite3.connect(DATABASE_FILE)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

        self.initialize()

    def initialize(self):

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs(
            id TEXT PRIMARY KEY,
            title TEXT,
            description TEXT,
            score REAL,
            tier TEXT,
            connects INTEGER,
            created_at TEXT,
            status TEXT DEFAULT 'submitted'
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS connect_spend(
            date TEXT PRIMARY KEY,
            connects_used INTEGER
        )
        """)

        # Proposal status tracking
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS proposal_status(
            job_id TEXT PRIMARY KEY,
            status TEXT,
            updated_at TEXT
        )
        """)

        self.conn.commit()

    def job_exists(self, job_id):

        self.cursor.execute("SELECT id FROM jobs WHERE id=?", (job_id,))
        return self.cursor.fetchone() is not None

    def save_job(self, job_id, title, description, score, tier, connects):

        self.cursor.execute("""
        INSERT OR REPLACE INTO jobs
        VALUES(?,?,?,?,?,?,?)
        """, (
            job_id,
            title,
            description,
            score,
            tier,
            connects,
            datetime.utcnow().isoformat()
        ))

        self.conn.commit()

    def connects_today(self):

        today = datetime.utcnow().date().isoformat()

        self.cursor.execute(
            "SELECT connects_used FROM connect_spend WHERE date=?",
            (today,)
        )

        row = self.cursor.fetchone()

        return row["connects_used"] if row else 0

    def add_connects(self, amount):

        today = datetime.utcnow().date().isoformat()
        used = self.connects_today()

        self.cursor.execute("""
        INSERT OR REPLACE INTO connect_spend
        VALUES(?,?)
        """, (today, used + amount))

        self.conn.commit()

    def update_proposal_status(self, job_id, status):

        self.cursor.execute("""
        INSERT OR REPLACE INTO proposal_status
        VALUES(?,?,?)
        """, (job_id, status, datetime.utcnow().isoformat()))

        self.conn.commit()

# ---------------------------------------
# DATA MODEL
# ---------------------------------------

@dataclass
class Job:

    id: str
    title: str
    description: str
    created: datetime
    client_spend: Optional[float] = None
    client_rating: Optional[float] = None
    payment_verified: bool = False
    connects_required: int = MAX_CONNECT_COST

# ---------------------------------------
# JOB FETCHER (RSS optimized)
# ---------------------------------------

class JobFetcher:

    @staticmethod
    def fetch():

        jobs: List[Job] = []

        # Fetch from all keyword RSS feeds
        for rss_url in UPWORK_RSS_URLS:
            try:
                response = requests.get(rss_url, timeout=10)
                rss = response.text

                items = rss.split("<item>")[1:]

                for item in items:

                    title_match = re.search("<title>(.*?)</title>", item)
                    desc_match = re.search("<description>(.*?)</description>", item)
                    pub_match = re.search("<pubDate>(.*?)</pubDate>", item)

                    if not title_match:
                        continue

                    title = title_match.group(1).lower()
                    description = desc_match.group(1).lower() if desc_match else ""

                    created = datetime.utcnow()

                    if pub_match:
                        try:
                            created = datetime.strptime(
                                pub_match.group(1)[:25],
                                "%a, %d %b %Y %H:%M:%S"
                            )
                        except:
                            pass

                    client_spend = None
                    rating = None
                    verified = False

                    spend_match = re.search(r"\$([0-9,]+)\s+spent", description)
                    if spend_match:
                        client_spend = float(spend_match.group(1).replace(",", ""))

                    rating_match = re.search(r"([0-5]\.[0-9])\s+rating", description)
                    if rating_match:
                        rating = float(rating_match.group(1))

                    if "payment verified" in description:
                        verified = True

                    job_id = hashlib.sha256(
                        (title + description).encode()
                    ).hexdigest()[:32]

                    jobs.append(
                        Job(
                            job_id,
                            title,
                            description,
                            created,
                            client_spend,
                            rating,
                            verified,
                            MAX_CONNECT_COST  # Max connects we're willing to use
                        )
                    )
            except Exception as e:
                logger.warning(f"Failed to fetch {rss_url}: {e}")

        return jobs

# ---------------------------------------
# JOB PARSER
# ---------------------------------------

class JobParser:

    @staticmethod
    def categorize(job):

        for level, keywords in TARGET_JOBS.items():

            for keyword in keywords:

                if keyword in job.title:
                    return level, keyword

        return None, None

# ---------------------------------------
# JOB SCORING
# ---------------------------------------

class JobScorer:

    @staticmethod
    def age_minutes(job):

        return (datetime.utcnow() - job.created).total_seconds() / 60

    @staticmethod
    def score(job, category):

        score = 5

        age = JobScorer.age_minutes(job)

        if age < 30:
            score += 3
        elif age < 120:
            score += 1

        if category == "easy":
            score += 1

        if category == "medium":
            score += 2

        if job.payment_verified:
            score += 1

        if job.client_rating and job.client_rating > 4.5:
            score += 1

        if job.client_spend and job.client_spend > 1000:
            score += 1

        return min(score, 10)

# ---------------------------------------
# PRIORITIZATION
# ---------------------------------------

class JobPrioritizer:

    @staticmethod
    def tier(score):

        if score >= 9:
            return "tier1"

        if score >= 7:
            return "tier2"

        return "tier3"

# ---------------------------------------
# DEMO GENERATOR (stronger)
# ---------------------------------------

class DemoGenerator:

    ROOT = "demos"

    @staticmethod
    def generate(job):

        os.makedirs(DemoGenerator.ROOT, exist_ok=True)

        folder = os.path.join(
            DemoGenerator.ROOT,
            uuid.uuid4().hex[:8]
        )

        os.makedirs(folder)

        # sample dataset
        csv_path = os.path.join(folder, "sample_output.csv")

        with open(csv_path, "w") as f:
            f.write("name,email\nexample,test@example.com\n")

        # script example
        script_path = os.path.join(folder, "example_script.py")

        with open(script_path, "w") as f:
            f.write("""
import csv

data=[["name","email"],["example","test@example.com"]]

with open("sample_output.csv","w") as f:
    writer=csv.writer(f)
    writer.writerows(data)

print("Demo dataset generated")
""")

        readme = os.path.join(folder, "README.md")

        with open(readme, "w") as f:

            f.write(f"""
Demo for: {job.title}

This demo shows a simple working example output similar
to what the final deliverable could look like.

Files:
- example_script.py
- sample_output.csv
""")

        return folder

# ---------------------------------------
# GIST UPLOADER (for demo sharing)
# ---------------------------------------

class GistUploader:

    GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

    @staticmethod
    def upload_demo(demo_folder):

        if not GistUploader.GITHUB_TOKEN:
            logger.warning("No GITHUB_TOKEN set, returning local folder")
            return demo_folder

        try:
            files = {}
            for filename in os.listdir(demo_folder):
                filepath = os.path.join(demo_folder, filename)
                if os.path.isfile(filepath):
                    with open(filepath, 'r') as f:
                        files[filename] = {"content": f.read()}

            gist_data = {
                "description": f"Demo for Upwork proposal - {datetime.now().date()}",
                "public": False,
                "files": files
            }

            response = requests.post(
                "https://api.github.com/gists",
                headers={
                    "Authorization": f"token {GistUploader.GITHUB_TOKEN}",
                    "Accept": "application/vnd.github+json"
                },
                json=gist_data
            )

            if response.status_code == 201:
                return response.json()["html_url"]
            else:
                logger.warning(f"Gist upload failed: {response.status_code}")
                return demo_folder

        except Exception as e:
            logger.warning(f"Gist upload error: {e}")
            return demo_folder

# ---------------------------------------
# DISCORD NOTIFIER
# ---------------------------------------

class DiscordNotifier:

    @staticmethod
    def send_alert(job_title, score, tier, proposal_preview):

        if not DISCORD_WEBHOOK_URL:
            return

        embed = {
            "title": f"New Job Alert - {job_title[:50]}...",
            "color": 3447003,  # Blue
            "fields": [
                {"name": "Score", "value": str(score), "inline": True},
                {"name": "Tier", "value": tier, "inline": True},
            ],
            "footer": {"text": "Konan Upwork Bot"}
        }

        payload = {
            "embeds": [embed]
        }

        try:
            requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        except Exception as e:
            logger.warning(f"Discord alert failed: {e}")

# ---------------------------------------
# TEMPLATE LOADER
# ---------------------------------------

class TemplateLoader:

    def __init__(self, templates_dir=TEMPLATES_DIR):
        self.templates_dir = templates_dir
        self.templates = {}
        self.load_templates()

    def load_templates(self):
        """Load all templates from the templates folder."""
        if not os.path.exists(self.templates_dir):
            logger.warning(f"Templates directory {self.templates_dir} not found")
            return

        for filename in os.listdir(self.templates_dir):
            if filename.endswith('.md'):
                template_name = filename[:-3]  # Remove .md
                filepath = os.path.join(self.templates_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.templates[template_name] = content
                    logger.info(f"Loaded template: {template_name}")

    def find_matching_template(self, job_title, job_description):
        """Find best matching template based on keywords."""
        text = (job_title + " " + job_description).lower()

        best_match = None
        best_score = 0

        for template_name, content in self.templates.items():
            # Extract keywords from template
            keywords_section = content.split("## Category Keywords")[-1].split("---")[0] if "## Category Keywords" in content else ""

            score = 0
            for keyword in keywords_section.split('\n'):
                keyword = keyword.strip('- ').strip()
                if keyword and keyword in text:
                    score += 1

            if score > best_score:
                best_score = score
                best_match = template_name

        return best_match, best_score

    def get_short_template(self, template_name):
        """Get the short version (for proposals)."""
        if template_name not in self.templates:
            return None

        content = self.templates[template_name]

        # Extract SHORT VERSION section
        if "## SHORT VERSION" in content:
            short = content.split("## SHORT VERSION")[-1].split("## LONG VERSION")[0]
            return short.strip()

        return content  # Fallback to full content

    def personalize_template(self, template_name, job_title, job_description):
        """Personalize template with job-specific details."""
        template = self.get_short_template(template_name)

        if not template:
            return None

        # Extract job-specific details
        details = self.extract_details(job_title, job_description)

        # Replace placeholders
        personalized = template
        for key, value in details.items():
            personalized = personalized.replace(f"[CUSTOMIZE: {key}]", value)

        # Remove any remaining [CUSTOMIZE: ...] placeholders
        personalized = re.sub(r'\[CUSTOMIZE: [^\]]+\]', '[Your specifics here]', personalized)

        return personalized

    def extract_details(self, job_title, job_description):
        """Extract specific details from job to customize template."""
        text = (job_title + " " + job_description).lower()

        details = {}

        # ==== Lead Generation specific ====
        industries = ['saas', 'tech', 'healthcare', 'finance', 'real estate', 'e-commerce', 'marketing', 'startup']
        for ind in industries:
            if ind in text:
                details['industry/target audience'] = ind
                break

        # Company size
        if 'enterprise' in text or '500+' in text:
            details['company size'] = 'enterprise (500+)'
        elif '100-500' in text:
            details['company size'] = 'mid-market (100-500)'
        elif '50-100' in text:
            details['company size'] = 'SMB (50-100)'

        # Tools
        tools = ['salesforce', 'hubspot', 'linkedin', 'zoominfo', 'clearbit', 'hunter', 'apollo']
        found_tools = [t for t in tools if t in text]
        if found_tools:
            details['tools mentioned'] = ', '.join(found_tools)

        # ==== Data Scraping specific ====
        # Target website
        url_match = re.search(r'(https?://[^\s]+|www\.[^\s]+)', job_title + " " + job_description)
        if url_match:
            details['target website'] = url_match.group(1)[:50]

        # Data points needed
        data_points = []
        if 'email' in text:
            data_points.append('emails')
        if 'phone' in text or 'contact' in text:
            data_points.append('phone numbers')
        if 'company' in text:
            data_points.append('company info')
        if 'price' in text or 'cost' in text:
            data_points.append('pricing')
        if 'product' in text:
            data_points.append('product details')
        if data_points:
            details['data points needed'] = ', '.join(data_points)

        # Scraping type
        if 'dynamic' in text or 'javascript' in text or 'js' in text:
            details['site type'] = 'dynamic JavaScript site'
        elif 'api' in text:
            details['site type'] = 'API extraction'
        else:
            details['site type'] = 'standard website'

        # Volume
        if '1000' in text or '1k' in text:
            details['expected volume'] = '1,000+ records'
        elif '5000' in text or '5k' in text:
            details['expected volume'] = '5,000+ records'
        elif '10000' in text or '10k' in text:
            details['expected volume'] = '10,000+ records'

        # ==== Research Assistant specific ====
        research_types = []
        if 'market research' in text:
            research_types.append('market research')
        if 'competitor' in text or 'competitive' in text:
            research_types.append('competitor analysis')
        if 'due diligence' in text:
            research_types.append('due diligence')
        if 'industry' in text:
            research_types.append('industry research')
        if 'company' in text or 'company profile' in text:
            research_types.append('company research')
        if 'academic' in text or 'literature' in text:
            research_types.append('academic research')
        if research_types:
            details['research type'] = ', '.join(research_types)

        # Research depth
        if 'deep' in text or 'comprehensive' in text or 'extensive' in text:
            details['research depth'] = 'comprehensive'
        elif 'quick' in text or 'brief' in text or 'overview' in text:
            details['research depth'] = 'overview'
        else:
            details['research depth'] = 'standard'

        # ==== Common deliverable format ====
        if 'csv' in text:
            details['deliverable format'] = 'CSV'
        if 'google sheet' in text:
            details['deliverable format'] = 'Google Sheets'
        if 'airtable' in text:
            details['deliverable format'] = 'Airtable'
        if 'json' in text:
            details['deliverable format'] = 'JSON'

        # ==== Webhook/Automation specific ====
        # Platforms mentioned
        platforms = []
        if 'zapier' in text:
            platforms.append('Zapier')
        if 'make' in text or 'integromat' in text:
            platforms.append('Make')
        if 'n8n' in text:
            platforms.append('n8n')
        if 'hubspot' in text:
            platforms.append('HubSpot')
        if 'salesforce' in text:
            platforms.append('Salesforce')
        if 'slack' in text:
            platforms.append('Slack')
        if 'google sheet' in text or 'gsheets' in text:
            platforms.append('Google Sheets')
        if platforms:
            details['platforms'] = ', '.join(platforms)

        # Automation type
        if 'crm' in text or 'lead' in text:
            details['automation type'] = 'CRM/lead automation'
        elif 'data sync' in text or 'sync' in text:
            details['automation type'] = 'data synchronization'
        elif 'webhook' in text:
            details['automation type'] = 'webhook processing'
        elif 'api' in text:
            details['automation type'] = 'API integration'
        else:
            details['automation type'] = 'workflow automation'

        # Complexity
        if 'complex' in text or 'multiple' in text or 'enterprise' in text:
            details['complexity'] = 'advanced'
        elif 'simple' in text or 'basic' in text:
            details['complexity'] = 'simple'
        else:
            details['complexity'] = 'standard'

        # ==== Cold Outreach specific ====
        if 'cold' in text or 'outreach' in text or 'email' in text or 'outbound' in text:
            details['campaign type'] = 'cold outreach'

        # Outreach channel
        if 'linkedin' in text:
            details['channel'] = 'LinkedIn'
        elif 'email' in text or 'cold' in text or 'outreach' in text:
            details['channel'] = 'email'
        if 'multi' in text or 'both' in text:
            details['channel'] = 'multi-channel'

        # Campaign goal
        if 'meeting' in text:
            details['goal'] = 'book meetings'
        elif 'lead' in text:
            details['goal'] = 'generate leads'
        elif 'pipeline' in text:
            details['goal'] = 'build pipeline'
        elif 'demo' in text:
            details['goal'] = 'book demos'

        # ==== Excel/Sheets specific ====
        if 'excel' in text or 'spreadsheet' in text or 'google sheet' in text or 'dashboard' in text:
            details['platform'] = 'Excel/Google Sheets'
            details['project type'] = 'spreadsheet/dashboard'

        # Use case detection
        if 'financial' in text or 'finance' in text or 'p&l' in text or 'cash flow' in text:
            details['use case'] = 'financial model'
        elif 'budget' in text or 'tracking' in text:
            details['use case'] = 'budget/tracker'
        elif 'project' in text:
            details['use case'] = 'project management'
        elif 'sales' in text or 'crm' in text:
            details['use case'] = 'sales/CRM'
        elif 'inventory' in text:
            details['use case'] = 'inventory'
        elif 'analytics' in text or 'dashboard' in text:
            details['use case'] = 'analytics/dashboard'
        else:
            details['use case'] = 'spreadsheet automation'

        # ==== Virtual Assistant specific ====
        va_keywords = ['virtual assistant', 'va', 'executive assistant', 'administrative', 'calendar management', 'inbox', 'admin support']
        if any(kw in text for kw in va_keywords):
            details['service type'] = 'virtual assistant'

        # VA specialization
        if 'executive' in text or 'ceo' in text or 'c-suite' in text:
            details['va specialization'] = 'executive assistant'
        elif 'real estate' in text:
            details['va specialization'] = 'real estate VA'
        elif 'tech' in text or 'startup' in text or 'saas' in text:
            details['va specialization'] = 'tech startup VA'
        elif 'ecommerce' in text or 'e-commerce' in text or 'shopify' in text:
            details['va specialization'] = 'e-commerce VA'
        elif 'sales' in text or 'crm' in text:
            details['va specialization'] = 'sales VA'

        return details

# ---------------------------------------
# PROPOSAL PERSONALIZATION AGENT
# ---------------------------------------

class ProposalAgent:

    # Template loader instance
    template_loader = TemplateLoader()

    @staticmethod
    def extract_problem(description):

        sentences = re.split(r"[.!?]", description)

        for s in sentences:
            if len(s) > 40:
                return s.strip()

        return description[:120]

    @staticmethod
    def generate(job, keyword):
        """Generate proposal - tries template first, falls back to generic."""

        # Try to find matching template
        template_name, match_score = ProposalAgent.template_loader.find_matching_template(
            job.title, job.description
        )

        if template_name and match_score > 0:
            # Use template
            proposal = ProposalAgent.template_loader.personalize_template(
                template_name, job.title, job.description
            )

            # Add custom question based on job
            problem = ProposalAgent.extract_problem(job.description)
            question = ProposalAgent.generate_question(job.description)

            if question and question not in proposal:
                proposal += f"\n\n{question}"

            logger.info(f"Using template: {template_name} (score: {match_score})")
            return proposal

        # Fallback to generic proposal
        problem = ProposalAgent.extract_problem(job.description)

        proposal = f"""
Hi,

I noticed you're looking for help with {keyword}.

From the description it sounds like the main goal is:
"{problem}"

My approach would be:

1. Review the current requirements and inputs
2. Build a clean working solution for the task
3. Deliver structured output ready for use

I've handled similar work involving {keyword} automation and data workflows.

Quick question:
Do you mainly want a one-time task completed, or something reusable long-term?

Best,
"""

        return proposal.strip()

    @staticmethod
    def generate_question(description):
        """Generate a specific question based on job description."""
        text = description.lower()

        questions = []

        # Industry-specific questions
        if 'saas' in text or 'software' in text:
            questions.append("What's your current stack and what gaps are you trying to fill?")
        if 'healthcare' in text:
            questions.append("What compliance requirements (HIPAA, etc.) should we be aware of?")
        if 'real estate' in text:
            questions.append("What MLS systems are you currently using?")
        if 'finance' in text or 'fintech' in text:
            questions.append("What data sources are most important for your analysis?")

        # Deliverable-specific questions
        if 'csv' in text or 'spreadsheet' in text:
            questions.append("What specific fields do you need in the output?")
        if 'automation' in text or 'zapier' in text:
            questions.append("What triggers and actions should the automation include?")
        if 'email' in text or 'outreach' in text:
            questions.append("What's your current email deliverability setup?")

        # Scope questions
        if 'ongoing' in text or 'month' in text:
            questions.append("What's your expected volume per month?")
        if 'urgent' in text or 'asap' in text:
            questions.append("When is your deadline for the initial deliverable?")

        # Return a random question if we found any
        if questions:
            import random
            return random.choice(questions)

        return None

# ---------------------------------------
# KONAN BOT
# ---------------------------------------

class KonanBot:

    def __init__(self):

        self.db = Database()

    def process_job(self, job):

        if self.db.job_exists(job.id):
            return

        category, keyword = JobParser.categorize(job)

        if not category:
            return

        age = JobScorer.age_minutes(job)

        if age > 120:
            return

        score = JobScorer.score(job, category)

        if score < MIN_SCORE_THRESHOLD:
            return

        tier = JobPrioritizer.tier(score)

        connects_used = self.db.connects_today()

        if connects_used + job.connects_required > MAX_CONNECTS_PER_DAY:
            return

        demo_folder = None
        demo_url = None

        if score >= DEMO_TRIGGER_SCORE:
            demo_folder = DemoGenerator.generate(job)
            # Upload to GitHub Gist for sharing
            demo_url = GistUploader.upload_demo(demo_folder)

        proposal = ProposalAgent.generate(job, keyword)

        # Send Discord alert for high-tier jobs
        if tier in ["tier1", "tier2"]:
            DiscordNotifier.send_alert(job.title, score, tier, proposal[:100])

        print("\n--------------------------")
        print("JOB:", job.title)
        print("Score:", score)
        print("Tier:", tier)
        print("Demo:", demo_url or demo_folder)
        print("\nPROPOSAL:\n")
        print(proposal)

        decision = input("\nSubmit proposal? (y/n): ")

        if decision.lower() == "y":

            self.db.add_connects(job.connects_required)
            self.db.update_proposal_status(job.id, "submitted")

            print("Proposal submitted.")

        self.db.save_job(
            job.id,
            job.title,
            job.description,
            score,
            tier,
            job.connects_required
        )

    def run(self):

        jobs = JobFetcher.fetch()

        for job in jobs:
            self.process_job(job)

# ---------------------------------------
# MAIN LOOP
# ---------------------------------------

if __name__ == "__main__":

    bot = KonanBot()

    while True:

        bot.run()

        time.sleep(SCAN_INTERVAL)