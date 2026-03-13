#!/usr/bin/env python3
"""
Konan Upwork Agent - MERGED VERSION
Combines optimizations + full template system

Features:
- XML RSS parsing
- Semantic deduplication
- Rate limiting
- Client quality signals
- Competition scoring
- 13 Templates with detection
- Enhanced Demo Builder (template + skills = actual product)
- Gist upload for demos
"""

import os
import uuid
import hashlib
import sqlite3
import logging
import requests
import xml.etree.ElementTree as ET
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional
from math import sqrt

# -----------------------
# CONFIG
# -----------------------

UPWORK_RSS_URL = "https://www.upwork.com/ab/feed/jobs/rss?q=assistant"
DATABASE_FILE = "konan_agent.db"
SCAN_INTERVAL = 600
MAX_CONNECTS_PER_DAY = 120
MAX_PROPOSALS_PER_HOUR = 20
DEFAULT_CONNECT_COST = 12
MIN_SCORE_THRESHOLD = 6
DEMO_TRIGGER_SCORE = 8
TOP_DEMO_JOBS = 10
LOG_LEVEL = logging.INFO
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")

# 13 Target Keywords
TARGET_JOBS = [
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

# Keyword synonyms
KEYWORD_SYNONYMS = {
    "lead generation": ["prospect list", "contact extraction", "email list building"],
    "data scraping": ["web scraping", "data extraction"],
    "virtual assistant": ["remote assistant", "admin support"],
    "social media": ["social media management"],
}

logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger("konan")

# -----------------------
# DATABASE
# -----------------------

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
                client_spend REAL,
                client_rating REAL,
                payment_verified INTEGER,
                proposals_sent INTEGER,
                proposals_accepted INTEGER,
                hired INTEGER,
                vector TEXT,
                template_type TEXT
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

    def save_job(self, job, tier, score, vector, template_type=None):
        self.cursor.execute("""
            INSERT OR REPLACE INTO jobs(
                id, title, description, score, tier, connects, created_at,
                client_spend, client_rating, payment_verified, proposals_sent,
                proposals_accepted, hired, vector, template_type
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            job.id, job.title, job.description, score, tier,
            job.connects_required, datetime.utcnow().isoformat(),
            job.client_spend, job.client_rating, int(job.payment_verified),
            0, 0, 0, vector, template_type
        ))
        self.conn.commit()

    def connects_today(self):
        today = datetime.utcnow().date().isoformat()
        self.cursor.execute("SELECT connects_used FROM connect_spend WHERE date=?", (today,))
        row = self.cursor.fetchone()
        return row["connects_used"] if row else 0

    def add_connects(self, amount):
        today = datetime.utcnow().date().isoformat()
        used = self.connects_today()
        self.cursor.execute("""
            INSERT OR REPLACE INTO connect_spend(date, connects_used)
            VALUES(?, ?)
        """, (today, used + amount))
        self.conn.commit()

    def update_proposal_feedback(self, job_id, accepted=False, hired=False):
        self.cursor.execute("""
            UPDATE jobs
            SET proposals_sent = proposals_sent + 1,
                proposals_accepted = proposals_accepted + ?,
                hired = hired + ?
            WHERE id = ?
        """, (int(accepted), int(hired), job_id))
        self.conn.commit()

    def is_semantic_duplicate(self, vector, threshold=0.9):
        self.cursor.execute("SELECT vector FROM jobs WHERE vector IS NOT NULL")
        for row in self.cursor.fetchall():
            try:
                existing_vec = list(map(float, row["vector"].split(",")))
                sim = cosine_similarity(existing_vec, vector)
                if sim > threshold:
                    return True
            except:
                pass
        return False

# -----------------------
# UTILITIES
# -----------------------

def cosine_similarity(v1, v2):
    dot = sum(a*b for a,b in zip(v1,v2))
    norm1 = sqrt(sum(a*a for a in v1))
    norm2 = sqrt(sum(b*b for b in v2))
    return dot / (norm1*norm2 + 1e-8)

def text_to_vector(text, dim=50):
    vec = [0]*dim
    for i, c in enumerate(text):
        vec[i%dim] += ord(c)
    return vec

# -----------------------
# DATA MODEL
# -----------------------

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
    proposal_count: int = 0

# -----------------------
# JOB FETCHER (XML)
# -----------------------

class JobFetcher:

    @staticmethod
    def fetch():
        jobs: List[Job] = []
        try:
            response = requests.get(UPWORK_RSS_URL, timeout=10)
            root = ET.fromstring(response.content)
            for item in root.findall(".//item"):
                try:
                    title = item.findtext("title", "").lower()
                    description = item.findtext("description", "").lower()
                    pub_date = item.findtext("pubDate")
                    created = datetime.utcnow()
                    if pub_date:
                        try:
                            created = datetime.strptime(pub_date[:25], "%a, %d %b %Y %H:%M:%S")
                        except:
                            pass

                    client_spend = None
                    rating = None
                    verified = False
                    proposal_count = 0

                    spend_match = re.search(r"\$([0-9,]+)\s+spent", description)
                    if spend_match:
                        client_spend = float(spend_match.group(1).replace(",", ""))
                    rating_match = re.search(r"([0-5]\.[0-9])\s+rating", description)
                    if rating_match:
                        rating = float(rating_match.group(1))
                    if "payment verified" in description:
                        verified = True
                    proposal_match = re.search(r"(\d+)\s+proposals", description)
                    if proposal_match:
                        proposal_count = int(proposal_match.group(1))

                    job_id = hashlib.sha256((title + description).encode()).hexdigest()[:32]
                    jobs.append(Job(
                        id=job_id, title=title, description=description,
                        created=created, client_spend=client_spend,
                        client_rating=rating, payment_verified=verified,
                        proposal_count=proposal_count
                    ))
                except Exception as e:
                    logger.warning(f"Job parsing failed: {e}")
        except Exception as e:
            logger.error(f"RSS fetch failed: {e}")
        return jobs

# -----------------------
# JOB PARSER
# -----------------------

class JobParser:

    def __init__(self):
        self.keywords = TARGET_JOBS

    def categorize(self, job):
        text = (job.title + " " + job.description).lower()
        for key in self.keywords:
            if key in text:
                return key
        return None

# -----------------------
# JOB SCORING
# -----------------------

class JobScorer:

    @staticmethod
    def age_minutes(job):
        return (datetime.utcnow() - job.created).total_seconds() / 60

    @staticmethod
    def score(job, keyword):
        score = 5
        age = JobScorer.age_minutes(job)
        if age < 15: score += 4
        elif age < 60: score += 2
        elif age < 120: score += 1

        if job.payment_verified: score += 1
        if job.client_rating and job.client_rating > 4.5: score += 1
        if job.client_spend and job.client_spend > 1000: score += 1
        if job.proposal_count > 20: score -= 2

        return min(max(score, 0), 10)

# -----------------------
# PRIORITIZATION
# -----------------------

class JobPrioritizer:

    @staticmethod
    def tier(score):
        if score >= 9: return "tier1"
        if score >= 7: return "tier2"
        return "tier3"

# -----------------------
# TEMPLATE DETECTION
# -----------------------

TEMPLATE_KEYWORDS = {
    "lead_generation": ["lead generation", "prospect list", "b2b leads"],
    "data_scraping": ["data scraping", "web scraping", "data extraction"],
    "research_assistant": ["research assistant", "market research"],
    "webhook_automation": ["webhook", "automation", "zapier"],
    "cold_outreach": ["cold outreach", "cold email", "email outreach"],
    "excel_sheets": ["excel", "google sheets", "spreadsheet", "dashboard"],
    "virtual_assistant": ["virtual assistant", "admin support"],
    "notion_setup": ["notion", "notion setup"],
    "qa_testing": ["qa testing", "quality assurance"],
    "email_automation": ["email automation", "mailchimp"],
    "social_media": ["social media", "instagram", "tiktok"],
    "content_repurposing": ["content repurposing", "repurpose"],
    "pdf_services": ["pdf", "ocr"],
}

def detect_template(job_title, job_description):
    """Detect which template matches this job."""
    text = (job_title + " " + job_description).lower()
    best_match = None
    best_score = 0
    
    for template, keywords in TEMPLATE_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > best_score:
            best_score = score
            best_match = template
    
    return best_match if best_score >= 1 else None

# -----------------------
# ENHANCED DEMO BUILDER
# -----------------------

class EnhancedDemoBuilder:
    """Builds demos using template + skills = actual product."""
    
    IMPROVERS = {
        "lead_generation": True,
        "data_scraping": True,
        "research_assistant": True,
        "webhook_automation": True,
        "cold_outreach": True,
        "excel_sheets": True,
        "virtual_assistant": True,
        "notion_setup": True,
        "qa_testing": True,
        "email_automation": True,
        "social_media": True,
        "content_repurposing": True,
        "pdf_services": True,
    }
    
    ROOT = "demos"
    
    @staticmethod
    def generate(job, template_type):
        folder = None
        try:
            os.makedirs(EnhancedDemoBuilder.ROOT, exist_ok=True)
            folder = os.path.join(EnhancedDemoBuilder.ROOT, uuid.uuid4().hex[:8])
            os.makedirs(folder)
            
            # Generate based on template type
            if template_type == "lead_generation":
                EnhancedDemoBuilder._build_lead_gen(job, folder)
            elif template_type == "data_scraping":
                EnhancedDemoBuilder._build_scraper(job, folder)
            elif template_type == "excel_sheets":
                EnhancedDemoBuilder._build_spreadsheet(job, folder)
            elif template_type == "qa_testing":
                EnhancedDemoBuilder._build_qa(job, folder)
            else:
                EnhancedDemoBuilder._build_generic(job, folder)
            
        except Exception as e:
            logger.warning(f"Demo generation failed: {e}")
        return folder
    
    @staticmethod
    def _build_lead_gen(job, folder):
        # CSV with sample data
        csv_path = os.path.join(folder, "sample_leads.csv")
        with open(csv_path, "w") as f:
            f.write("company,contact,email,phone,title,industry,status,notes\n")
            f.write("Acme Corp,John Smith,john@acme.com,555-0101,CEO,Tech,New,\n")
            f.write("TechStart,Jane Doe,jane@techstart.io,555-0102,CTO,SaaS,Contacted,\n")
        
        # Script with validation
        script_path = os.path.join(folder, "lead_validation.py")
        with open(script_path, "w") as f:
            f.write("""#!/usr/bin/env python3
# Lead Validation Script
import re

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone):
    digits = re.sub(r'\\D', '', phone)
    return len(digits) == 10

# Example usage:
# leads = load_csv('sample_leads.csv')
# for lead in leads:
#     if validate_email(lead['email']):
#         print(f"Valid: {lead['email']}")
""")
        
        # README
        readme = os.path.join(folder, "README.md")
        with open(readme, "w") as f:
            f.write(f"# Demo for: {job.title}\n\n")
            f.write("## Files\n")
            f.write("- sample_leads.csv - Sample lead data\n")
            f.write("- lead_validation.py - Email/phone validation script\n\n")
            f.write("## Features\n")
            f.write("- Email validation function\n")
            f.write("- Phone validation function\n")
            f.write("- Ready to customize for your needs\n")
    
    @staticmethod
    def _build_scraper(job, folder):
        script_path = os.path.join(folder, "scraper.py")
        with open(script_path, "w") as f:
            f.write(f"""#!/usr/bin/env python3
# Web Scraper Demo - {job.title}
import requests
from bs4 import BeautifulSoup
import csv

URL = "https://example.com"  # Customize URL

def scrape_data(url):
    headers = {{'User-Agent': 'Mozilla/5.0'}}
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    items = []
    # Add your selectors here
    # for item in soup.select('.item-class'):
    #     items.append({{'title': item.get_text()}})
    
    return items

def save_csv(data, filename='output.csv'):
    if not data:
        return
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

if __name__ == "__main__":
    data = scrape_data(URL)
    save_csv(data)
    print(f"Scraped {{len(data)}} items")
""")
        
        readme = os.path.join(folder, "README.md")
        with open(readme, "w") as f:
            f.write(f"# Demo for: {job.title}\n\n")
            f.write("## Customizable\n")
            f.write("- Set your target URL\n")
            f.write("- Add CSS selectors for your data\n")
            f.write("- Run and get CSV output\n")
    
    @staticmethod
    def _build_spreadsheet(job, folder):
        csv_path = os.path.join(folder, "sample_data.csv")
        with open(csv_path, "w") as f:
            f.write("item,quantity,price,total,status,notes\n")
            f.write("Product A,10,25.00,250.00,Active,\n")
            f.write("Service B,5,100.00,500.00,Pending,\n")
        
        formulas_path = os.path.join(folder, "formulas.txt")
        with open(formulas_path, "w") as f:
            f.write("""# Google Sheets Formulas

# Total calculation
=E2*B2

# Email validation
=ISEMAIL(C2)

# Status indicator
=IF(F2="Active", "✅", "❌")

# Date
=TODAY()

# VLOOKUP example
=IFERROR(VLOOKUP(A2, lookup_sheet!A:B, 2, FALSE), "N/A")
""")
        
        readme = os.path.join(folder, "README.md")
        with open(readme, "w") as f:
            f.write(f"# Demo for: {job.title}\n\n")
            f.write("## Files\n")
            f.write("- sample_data.csv - Sample data\n")
            f.write("- formulas.txt - Google Sheets formulas\n")
    
    @staticmethod
    def _build_qa(job, folder):
        testcases_path = os.path.join(folder, "test_cases.md")
        with open(testcases_path, "w") as f:
            f.write(f"""# Test Cases - {job.title}

## Test Case Template

| ID | Feature | Test Case | Steps | Expected Result | Status |
|----|---------|-----------|-------|-----------------|--------|
| TC01 | | | | | Not Run |
| TC02 | | | | | Not Run |

## Bug Report Template

| ID | Title | Severity | Steps to Reproduce | Expected | Actual |
|----|-------|-----------|---------------------|----------|---------|
| BUG01 | | | | | |

## Test Data
- Add test data here
""")
        
        readme = os.path.join(folder, "README.md")
        with open(readme, "w") as f:
            f.write(f"# Demo for: {job.title}\n\n")
            f.write("## What's Included\n")
            f.write("- Test case template\n")
            f.write("- Bug report template\n")
            f.write("- Test data section\n")
    
    @staticmethod
    def _build_generic(job, folder):
        readme = os.path.join(folder, "README.md")
        with open(readme, "w") as f:
            f.write(f"# Demo for: {job.title}\n\n")
            f.write("Demo files generated based on job requirements.\n")
            f.write("Customize for your specific needs.\n")

# -----------------------
# GIST UPLOAD
# -----------------------

def upload_to_gist(folder, job_title):
    """Upload demo folder to GitHub Gist."""
    import base64
    
    gist_token = os.environ.get("GITHUB_TOKEN", "")
    if not gist_token:
        return None
    
    files = {}
    try:
        for filename in os.listdir(folder):
            filepath = os.path.join(folder, filename)
            if os.path.isfile(filepath):
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    files[filename] = {"content": f.read()}
    except:
        return None
    
    if not files:
        return None
    
    try:
        response = requests.post(
            "https://api.github.com/gists",
            headers={
                "Authorization": f"token {gist_token}",
                "Accept": "application/vnd.github+json"
            },
            json={
                "description": f"Demo: {job_title}",
                "public": False,
                "files": files
            }
        )
        if response.status_code == 201:
            return response.json()["html_url"]
    except:
        pass
    
    return None

# -----------------------
# DISCORD ALERTS
# -----------------------

def send_discord_alert(job_title, score, tier, status, connects):
    """Send Discord alert for job actions."""
    if not DISCORD_WEBHOOK_URL:
        return
    
    colors = {"tier1": 3066993, "tier2": 3447003, "tier3": 15105570}
    embeds = [{
        "title": f"📋 Job Alert: {status}",
        "description": job_title[:100],
        "color": colors.get(tier, 0),
        "fields": [
            {"name": "Score", "value": f"{score}/10", "inline": True},
            {"name": "Tier", "value": tier, "inline": True},
            {"name": "Connects", "value": str(connects), "inline": True}
        ],
        "timestamp": datetime.utcnow().isoformat()
    }]
    
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"embeds": embeds}, timeout=5)
    except:
        pass

# -----------------------
# PROPOSAL AGENT
# -----------------------

class ProposalAgent:

    @staticmethod
    def extract_problem(description):
        sentences = re.split(r"[.!?]", description)
        for s in sentences:
            if len(s) > 40:
                return s.strip()
        return description[:120]

    @staticmethod
    def generate(job, keyword, template_type=None):
        problem = ProposalAgent.extract_problem(job.description)
        
        # Template-aware proposal
        if template_type:
            proposal = f"""
Hi,

I noticed you're looking for help with {keyword}.

Based on your posting, I understand you need:
"{problem}"

I've built similar solutions for {keyword} projects, including working demos.

My approach:
1. Understand your specific requirements
2. Build a tailored solution
3. Deliver with documentation

I can provide a working demo to show my capability.

Quick question: What's your timeline for this project?

Best,
"""
        else:
            proposal = f"""
Hi,

I noticed you're looking for help with {keyword}.

Problem as I understand:
"{problem}"

My approach:

1. Review requirements and inputs
2. Build a clean working solution
3. Deliver structured, reusable output

I've handled similar {keyword} tasks before.

Quick question: Do you want this as one-time or reusable long-term?

Best,
"""
        return proposal.strip()

# -----------------------
# KONAN BOT
# -----------------------

class KonanBot:

    def __init__(self):
        self.db = Database()
        self.parser = JobParser()
        self.proposals_sent_hour = 0
        self.hour_window_start = datetime.utcnow()

    def rate_limit_check(self):
        now = datetime.utcnow()
        if (now - self.hour_window_start).total_seconds() > 3600:
            self.proposals_sent_hour = 0
            self.hour_window_start = now
        return self.proposals_sent_hour < MAX_PROPOSALS_PER_HOUR

    def process_jobs_batch(self, jobs):
        scored_jobs = []
        for job in jobs:
            try:
                if self.db.job_exists(job.id):
                    continue
                keyword = self.parser.categorize(job)
                if not keyword:
                    continue
                score = JobScorer.score(job, keyword)
                if score < MIN_SCORE_THRESHOLD:
                    continue
                vector = text_to_vector(job.title + job.description)
                if self.db.is_semantic_duplicate(vector):
                    continue
                scored_jobs.append((score, job, keyword, vector))
            except Exception as e:
                logger.error(f"Job processing failed: {e}")
        scored_jobs.sort(key=lambda x: x[0], reverse=True)
        return scored_jobs

    def run(self):
        """
        FLOW:
        1. Scan jobs → Show proposals (NO demo yet)
        2. User chooses: Submit / Review Queue / Skip
        3. (Demo built ONLY via --build-demo after approval)
        """
        jobs = JobFetcher.fetch()
        scored_jobs = self.process_jobs_batch(jobs)
        
        for score, job, keyword, vector in scored_jobs:
            try:
                tier = JobPrioritizer.tier(score)
                connects_used = self.db.connects_today()
                if connects_used + job.connects_required > MAX_CONNECTS_PER_DAY:
                    continue
                if not self.rate_limit_check():
                    continue
                
                # Detect template (for later demo building)
                template_type = detect_template(job.title, job.description)
                
                # Generate proposal (NO demo built here!)
                proposal = ProposalAgent.generate(job, keyword, template_type)
                
                # Display job info
                print("\n" + "="*50)
                print(f"JOB: {job.title[:60]}...")
                print(f"Score: {score}/10 | Tier: {tier}")
                print(f"Template: {template_type or 'Custom'}")
                print(f"Connects: {job.connects_required}")
                print("-"*50)
                print("PROPOSAL:\n")
                print(proposal)
                
                # Decision (NO demo built here!)
                print("\nOptions:")
                print("1. Submit proposal (uses 1 connect)")
                print("2. Add to review queue")
                print("3. Skip")
                decision = input("\nChoose (1/2/3): ")
                
                if decision == "1":
                    self.db.add_connects(job.connects_required)
                    self.db.update_proposal_feedback(job.id, accepted=True)
                    self.db.save_job(job, tier, score, ",".join(map(str, vector)), template_type)
                    self.proposals_sent_hour += 1
                    print("✓ Proposal submitted! Use --build-demo later to add demo.")
                    # Discord alert
                    send_discord_alert(job.title, score, tier, "Submitted", job.connects_required)
                elif decision == "2":
                    self.db.save_job(job, tier, score, ",".join(map(str, vector)), template_type)
                    print("✓ Added to review queue")
                    # Discord alert
                    send_discord_alert(job.title, score, tier, "Queued", 0)
                else:
                    # Save skipped jobs too (for deduplication)
                    self.db.save_job(job, tier, score, ",".join(map(str, vector)), template_type)
                    print("Skipped (saved for dedup)")
                    
            except Exception as e:
                logger.error(f"Job submission failed: {e}")

    def build_demo_for_queued_jobs(self):
        """
        Called via: python upwork-api.py --build-demo
        
        FLOW:
        1. Get jobs from review queue
        2. Build demo for each (template + skills = actual product)
        3. Upload to Gist
        4. Return demo URLs for review
        """
        print("\n=== BUILDING DEMOS FOR QUEUED JOBS ===\n")
        
        # Get queued jobs (proposals_sent = 0, have template_type)
        self.db.cursor.execute("""
            SELECT * FROM jobs 
            WHERE proposals_sent = 0 
            AND template_type IS NOT NULL
            ORDER BY score DESC
            LIMIT ?
        """, (TOP_DEMO_JOBS,))
        
        rows = self.db.cursor.fetchall()
        if not rows:
            print("No jobs in review queue. Run scan first.")
            return
        
        for row in rows:
            job_id = row["id"]
            title = row["title"]
            description = row["description"]
            template_type = row["template_type"]
            
            print(f"\n--- Building demo for: {title[:40]}... ---")
            print(f"Template: {template_type}")
            
            # Create job object for demo builder
            job = Job(
                id=job_id,
                title=title,
                description=description,
                created=datetime.utcnow()
            )
            
            # Build demo
            demo_folder = EnhancedDemoBuilder.generate(job, template_type)
            
            if demo_folder:
                # Upload to Gist
                gist_url = upload_to_gist(demo_folder, title)
                
                if gist_url:
                    print(f"✓ Demo built & uploaded!")
                    print(f"  Gist URL: {gist_url}")
                else:
                    print(f"✓ Demo built (local: {demo_folder})")
            else:
                print(f"✗ Demo build failed")
        
        print("\n=== DEMO BUILD COMPLETE ===")

# -----------------------
# MAIN
# -----------------------

import sys

def main():
    bot = KonanBot()
    
    # Check for --build-demo flag
    if len(sys.argv) > 1 and sys.argv[1] == "--build-demo":
        # Build demos for queued jobs
        bot.build_demo_for_queued_jobs()
    else:
        # Normal scan loop
        while True:
            bot.run()
            import time
            time.sleep(SCAN_INTERVAL)

if __name__ == "__main__":
    main()
