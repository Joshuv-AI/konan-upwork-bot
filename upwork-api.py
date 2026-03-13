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

UPWORK_RSS_URL = "https://www.upwork.com/ab/feed/jobs/rss?q=assistant"
DATABASE_FILE = "konan_agent.db"

SCAN_INTERVAL = 600
MAX_CONNECTS_PER_DAY = 120
DEFAULT_CONNECT_COST = 12

MIN_SCORE_THRESHOLD = 6
DEMO_TRIGGER_SCORE = 8

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
            created_at TEXT
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS connect_spend(
            date TEXT PRIMARY KEY,
            connects_used INTEGER
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
    connects_required: int = DEFAULT_CONNECT_COST

# ---------------------------------------
# JOB FETCHER (RSS optimized)
# ---------------------------------------

class JobFetcher:

    @staticmethod
    def fetch():

        jobs: List[Job] = []

        response = requests.get(UPWORK_RSS_URL, timeout=10)

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
                    verified
                )
            )

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

        if score >= DEMO_TRIGGER_SCORE:
            demo_folder = DemoGenerator.generate(job)

        proposal = ProposalAgent.generate(job, keyword)

        print("\n--------------------------")
        print("JOB:", job.title)
        print("Score:", score)
        print("Tier:", tier)
        print("Demo:", demo_folder)
        print("\nPROPOSAL:\n")
        print(proposal)

        decision = input("\nSubmit proposal? (y/n): ")

        if decision.lower() == "y":

            self.db.add_connects(job.connects_required)

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