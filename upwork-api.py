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
# PROPOSAL PERSONALIZATION AGENT
# ---------------------------------------

class ProposalAgent:

    @staticmethod
    def extract_problem(description):

        sentences = re.split(r"[.!?]", description)

        for s in sentences:
            if len(s) > 40:
                return s.strip()

        return description[:120]

    @staticmethod
    def generate(job, keyword):

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

I’ve handled similar work involving {keyword} automation and data workflows.

Quick question:
Do you mainly want a one-time task completed, or something reusable long-term?

Best,
"""

        return proposal.strip()

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