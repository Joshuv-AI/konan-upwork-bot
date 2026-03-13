# ========================================
# DEMO BUILDER MODULE
# Uses skills to actually BUILD demos
# ========================================

"""
This module maps jobs to skills and builds actual deliverables.
Each demo_type has:
- skills_needed: List of skills to use
- build_function: Function that builds the actual demo
- template_fallback: What to use if skills aren't available
"""

import os
import json
from datetime import datetime

# ========================================
# SKILL TO DEMO MAPPING
# ========================================

DEMO_BUILDERS = {

    # -----------------------------
    # LEAD GENERATION
    # -----------------------------
    "lead_generation": {
        "skills_needed": ["google-sheets", "python-dataviz"],
        "build": "build_lead_sheet",
        "description": "Working spreadsheet with sample leads, enrichment columns, and deduplication",
        "deliverable_format": "Google Sheet or CSV"
    },

    # -----------------------------
    # DATA SCRAPING
    # -----------------------------
    "data_scraping": {
        "skills_needed": ["python", "web-scraping"],
        "build": "build_scraper_script",
        "description": "Working Python scraper script with selectors and export",
        "deliverable_format": "Python script + sample CSV"
    },

    # -----------------------------
    # RESEARCH ASSISTANT
    # -----------------------------
    "research_assistant": {
        "skills_needed": ["google-sheets", "notes"],
        "build": "build_research_template",
        "description": "Research template with source tracking, analysis framework",
        "deliverable_format": "Google Sheet or Notion template"
    },

    # -----------------------------
    # WEBHOOK / AUTOMATION
    # -----------------------------
    "webhook_automation": {
        "skills_needed": ["n8n-code-python", "webhook"],
        "build": "build_automation_flow",
        "description": "Working automation workflow (Zapier/n8n template or code)",
        "deliverable_format": "JSON workflow or Python code"
    },

    # -----------------------------
    # COLD OUTREACH
    # -----------------------------
    "cold_outreach": {
        "skills_needed": ["google-sheets", "gmail-automation"],
        "build": "build_outreach_sheet",
        "description": "Outreach tracker with sequence stages, personalization fields",
        "deliverable_format": "Google Sheet"
    },

    # -----------------------------
    # EXCEL / GOOGLE SHEETS
    # -----------------------------
    "excel_sheets": {
        "skills_needed": ["google-sheets", "python-dataviz"],
        "build": "build_spreadsheet",
        "description": "Working spreadsheet with formulas, dashboards, sample data",
        "deliverable_format": "Google Sheet or Excel file"
    },

    # -----------------------------
    # VIRTUAL ASSISTANT
    # -----------------------------
    "virtual_assistant": {
        "skills_needed": ["google-sheets", "notes"],
        "build": "build_va_systems",
        "description": "Task management template, SOP framework, client tracker",
        "deliverable_format": "Notion template or Google Sheet"
    },

    # -----------------------------
    # NOTION SETUP
    # -----------------------------
    "notion_setup": {
        "skills_needed": ["notes", "google-sheets"],
        "build": "build_notion_template",
        "description": "Notion workspace template with databases and views",
        "deliverable_format": "Notion template link or JSON"
    },

    # -----------------------------
    # QA TESTING
    # -----------------------------
    "qa_testing": {
        "skills_needed": ["notes", "google-sheets"],
        "build": "build_qa_docs",
        "description": "Test plan template, test cases, bug report template",
        "deliverable_format": "Google Sheet or Markdown"
    },

    # -----------------------------
    # EMAIL AUTOMATION
    # -----------------------------
    "email_automation": {
        "skills_needed": ["gmail-automation", "google-sheets"],
        "build": "build_email_sequence",
        "description": "Email sequence template, sequence flow diagram, tracking sheet",
        "deliverable_format": "Google Sheet + flow document"
    },

    # -----------------------------
    # SOCIAL MEDIA MANAGEMENT
    # -----------------------------
    "social_media": {
        "skills_needed": ["google-sheets", "notes"],
        "build": "build_social_calendar",
        "description": "Content calendar template, posting schedule, engagement tracker",
        "deliverable_format": "Google Sheet"
    },

    # -----------------------------
    # CONTENT REPURPOSING
    # -----------------------------
    "content_repurposing": {
        "skills_needed": ["google-sheets", "notes"],
        "build": "build_content_matrix",
        "description": "Content repurposing matrix, distribution template",
        "deliverable_format": "Google Sheet"
    },

    # -----------------------------
    # PDF SERVICES
    # -----------------------------
    "pdf_services": {
        "skills_needed": ["nano-pdf"],
        "build": "build_pdf_template",
        "description": "PDF form template or conversion sample",
        "deliverable_format": "PDF file"
    }
}

# ========================================
# KEYWORD TO DEMO TYPE MAPPING
# ========================================

KEYWORD_MAPPING = {
    # Lead Generation
    "lead generation": "lead_generation",
    "b2b leads": "lead_generation",
    "prospect list": "lead_generation",
    "data enrichment": "lead_generation",
    
    # Data Scraping
    "data scraping": "data_scraping",
    "web scraping": "data_scraping",
    "web crawler": "data_scraping",
    "data extraction": "data_scraping",
    
    # Research
    "research assistant": "research_assistant",
    "market research": "research_assistant",
    "competitor analysis": "research_assistant",
    
    # Automation
    "webhook": "webhook_automation",
    "automation": "webhook_automation",
    "zapier": "webhook_automation",
    "integromat": "webhook_automation",
    
    # Cold Outreach
    "cold outreach": "cold_outreach",
    "cold email": "cold_outreach",
    "email outreach": "cold_outreach",
    
    # Spreadsheets
    "excel": "excel_sheets",
    "google sheets": "excel_sheets",
    "spreadsheet": "excel_sheets",
    "dashboard": "excel_sheets",
    
    # VA
    "virtual assistant": "virtual_assistant",
    "administrative": "virtual_assistant",
    "calendar management": "virtual_assistant",
    
    # Notion
    "notion": "notion_setup",
    "notion setup": "notion_setup",
    
    # QA
    "qa testing": "qa_testing",
    "quality assurance": "qa_testing",
    "test automation": "qa_testing",
    
    # Email
    "email automation": "email_automation",
    "mailchimp": "email_automation",
    "klaviyo": "email_automation",
    "marketing email": "email_automation",
    
    # Social
    "social media": "social_media",
    "instagram": "social_media",
    "tiktok": "social_media",
    "content calendar": "social_media",
    
    # Content
    "content repurposing": "content_repurposing",
    "repurpose": "content_repurposing",
    
    # PDF
    "pdf": "pdf_services",
    "ocr": "pdf_services",
    "pdf conversion": "pdf_services"
}

# ========================================
# FUNCTIONS TO BUILD DEMOS
# ========================================

class DemoBuilder:
    """Builds actual demos using skills."""
    
    def __init__(self, output_dir="demos"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def analyze_job(self, job_title, job_description):
        """Determine what demo to build based on job."""
        text = (job_title + " " + job_description).lower()
        
        # Find matching demo type
        for keyword, demo_type in KEYWORD_MAPPING.items():
            if keyword in text:
                return demo_type, DEMO_BUILDERS.get(demo_type)
        
        return None, None
    
    def build_demo(self, demo_type, job_title, job_description):
        """Build the actual demo deliverable."""
        if not demo_type or demo_type not in DEMO_BUILDERS:
            return None, "No matching demo type found"
        
        builder = DEMO_BUILDERS[demo_type]
        
        # Call the appropriate build function
        build_func = builder.get("build")
        if build_func and hasattr(self, build_func):
            result = getattr(self)(build_func, job_title, job_description)
            return result, builder.get("description")
        
        return None, "Build function not implemented"
    
    # -----------------------------
    # BUILD FUNCTIONS
    # Each creates an actual deliverable
    # -----------------------------
    
    def build_lead_sheet(self, job_title, job_description):
        """Build a working lead generation spreadsheet."""
        # Create a CSV with sample lead data
        csv_content = """company,contact_name,email,phone,title,industry,website,linkedin,source,verification_status,notes
Acme Corp,John Smith,john@acme.com,555-0101,CEO,Technology,acme.com,linkedin.com/in/johnsmith,Website,Verified,
TechStart Inc,Jane Doe,jane@techstart.io,555-0102,CTO,Software,techstart.io,linkedin.com/in/janedoe,LinkedIn,Pending,
GlobalTech,Robert Johnson,robert@globaltech.com,555-0103,VP Sales,Enterprise,globaltech.com,,Referral,Verified,"""
        
        filename = f"lead_gen_sample_{datetime.now().strftime('%Y%m%d')}.csv"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(csv_content)
        
        return filepath, "Lead generation spreadsheet with sample data and verification columns"
    
    def build_scraper_script(self, job_title, job_description):
        """Build a Python web scraper script."""
        script = '''#!/usr/bin/env python3
"""
Web Scraper Demo - Generated by Konan Upwork Bot
Customize for: {job_title}
"""

import requests
from bs4 import BeautifulSoup
import csv
import time

# Configuration
URL = "https://example.com"  # TARGET URL
DELAY = 2  # Seconds between requests

def scrape_data(url):
    """Scrape data from target URL."""
    headers = {{'User-Agent': 'Mozilla/5.0'}}
    
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Customize selectors based on target site
    items = []
    # Example: soup.select('.product-item')
    
    return items

def export_to_csv(data, filename='output.csv'):
    """Export scraped data to CSV."""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys() if data else [])
        writer.writeheader()
        writer.writerows(data)
    print(f"Exported {{len(data)}} items to {{filename}}")

if __name__ == "__main__":
    print("Scraper ready - customize URL and selectors for your target site")
    # data = scrape_data(URL)
    # export_to_csv(data)
'''.format(job_title=job_title[:50])
        
        filename = f"scraper_demo.py"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(script)
        
        return filepath, "Python scraper script template"
    
    def build_spreadsheet(self, job_title, job_description):
        """Build a working spreadsheet template."""
        csv_content = """category,item,quantity,unit_price,total,status,notes
Product A,Widget,10,25.00,250.00,Active,
Product B,Gadget,5,50.00,250.00,Pending,
Service,Consulting,20,100.00,2000.00,Active,Hourly rate
"""
        
        filename = f"spreadsheet_template.csv"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(csv_content)
        
        return filepath, "Spreadsheet template with formulas ready"
    
    def build_automation_flow(self, job_title, job_description):
        """Build automation workflow code."""
        code = '''# Automation Demo - Zapier/n8n Template
# Job: {job_title}

# This is a template for automation
# Customize triggers and actions based on requirements

TRIGGERS:
- New row in Google Sheets
- Webhook received
- New email received

ACTIONS:
- Send Slack message
- Create Google Calendar event  
- Update database
- Send email notification

# Example n8n workflow JSON available upon request
'''.format(job_title=job_title[:50])
        
        filename = f"automation_template.txt"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(code)
        
        return filepath, "Automation workflow template"
    
    def build_qa_docs(self, job_title, job_description):
        """Build QA test documentation."""
        content = """# Test Plan - {job_title}

## Test Scope
[Define what's being tested]

## Test Environment
- URL: 
- Credentials: 
- Browser: 

## Test Cases

| ID | Feature | Test Case | Steps | Expected Result | Status |
|----|---------|-----------|-------|-----------------|--------|
| TC001 | Login | Valid login | 1. Enter credentials 2. Click login | Dashboard loads | Not Run |
| TC002 | Login | Invalid login | 1. Wrong password | Error message | Not Run |

## Bug Report Template

| ID | Title | Severity | Steps to Reproduce | Expected | Actual |
|----|-------|-----------|---------------------|----------|--------|
| BUG001 | | Critical | | | |

## Notes
[Add any additional notes]
""".format(job_title=job_title[:50])
        
        filename = f"qa_test_plan.md"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        return filepath, "QA test plan and bug report templates"
    
    # Default fallback builder
    def build_default(self, job_title, job_description):
        """Build generic template."""
        content = f"""# Demo for: {job_title}

This is a sample deliverable template.
Customize based on job requirements.

## Job Details
Title: {job_title}
Description: {job_description[:200]}...

## Deliverables
[Define what will be delivered]

## Timeline
- Phase 1: 
- Phase 2:
- Phase 3:
"""
        
        filename = f"demo_template.md"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        return filepath, "Generic demo template"


# ========================================
# MAIN FUNCTION
# ========================================

def create_demo(job_title, job_description):
    """Main function to create demo for a job."""
    builder = DemoBuilder()
    
    # Analyze job
    demo_type, info = builder.analyze_job(job_title, job_description)
    
    if not demo_type:
        # Fallback to generic
        demo_type = "default"
        info = {"description": "Generic demo"}
    
    # Build demo
    filepath, description = builder.build_demo(demo_type, job_title, job_description)
    
    return {
        "demo_type": demo_type,
        "filepath": filepath,
        "description": description,
        "info": info
    }


if __name__ == "__main__":
    # Test
    result = create_demo("Lead generation spreadsheet needed", "Need help creating lead tracking spreadsheet")
    print(result)
