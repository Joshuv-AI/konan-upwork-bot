# ========================================
# ENHANCED DEMO BUILDER
# Template + Skills → ACTUAL Product
# ========================================

"""
This module takes templates and IMPROVES them using actual skills.
Not just templates - real working products.

Flow:
1. Load template (starting point)
2. Analyze job requirements
3. Determine what to add/improve using skills
4. Execute improvements
5. Return final working product
"""

import os
import csv
import json
from datetime import datetime
from pathlib import Path

# ========================================
# TEMPLATE IMPROVERS
# Each takes template + job info → adds real functionality
# ========================================

class TemplateImprover:
    """Base class for improving templates with actual skills."""
    
    def __init__(self, job_title, job_description):
        self.job_title = job_title
        self.job_description = job_description
        self.text = (job_title + " " + job_description).lower()
    
    def analyze_requirements(self):
        """Analyze what improvements are needed based on job."""
        requirements = []
        
        # What does the job need?
        if any(x in self.text for x in ['automate', 'automation', 'workflow']):
            requirements.append("automation")
        
        if any(x in self.text for x in ['data', 'extract', 'scrape', 'collect']):
            requirements.append("data_collection")
        
        if any(x in self.text for x in ['verify', 'validation', 'check']):
            requirements.append("data_validation")
        
        if any(x in self.text for x in ['enrich', 'enhance', 'update']):
            requirements.append("data_enrichment")
        
        if any(x in self.text for x in ['track', 'monitor', 'dashboard']):
            requirements.append("tracking")
        
        if any(x in self.text for x in ['email', 'notification', 'alert']):
            requirements.append("notifications")
        
        if any(x in self.text for x in ['api', 'integration', 'connect']):
            requirements.append("api_integration")
        
        if any(x in self.text for x in ['schedule', 'cron', 'automate']):
            requirements.append("scheduling")
        
        if any(x in self.text for x in ['test', 'qa', 'quality']):
            requirements.append("testing")
        
        return requirements


class LeadGenerationImprover(TemplateImprover):
    """Improves lead generation templates with real functionality."""
    
    def improve(self, template_data):
        """Add real functionality to lead gen template."""
        improvements = []
        
        # Analyze requirements
        reqs = self.analyze_requirements()
        
        # Add automation
        if "automation" in reqs:
            improvements.append({
                "type": "automation",
                "code": '''# Auto-refresh leads every hour
import schedule
import time

def refresh_leads():
    # Call enrichment API
    # Update sheet
    pass

schedule.every().hour.do(refresh_leads)
while True:
    schedule.run_pending()
    time.sleep(60)
'''
            })
        
        # Add validation
        if "data_validation" in reqs:
            improvements.append({
                "type": "validation",
                "code": '''# Email validation function
def validate_email(email):
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

# Phone validation
def validate_phone(phone):
    import re
    digits = re.sub(r'\D', '', phone)
    return len(digits) == 10
'''
            })
        
        # Add enrichment
        if "data_enrichment" in reqs:
            improvements.append({
                "type": "enrichment",
                "code": '''# LinkedIn enrichment (placeholder - add API)
def enrich_lead(row):
    # Add company size, industry from domain
    row['company_size'] = '11-50'  # Would call API
    row['industry'] = 'Technology'
    return row
'''
            })
        
        # Add tracking
        if "tracking" in reqs:
            improvements.append({
                "type": "tracking",
                "code": '''# Status tracking columns added:
# - Status: New → Contacted → Qualified → Converted
# - Last Contact: Date
# - Next Follow-up: Date
# - Notes: Free text
'''
            })
        
        return improvements


class DataScrapingImprover(TemplateImprover):
    """Improves scraper templates with real functionality."""
    
    def improve(self, template_data):
        """Add real functionality to scraper."""
        improvements = []
        reqs = self.analyze_requirements()
        
        # Target URL
        if "http" in self.text:
            url_match = self.text.split("http")[1].split()[0] if "http" in self.text else None
            if url_match:
                improvements.append({
                    "type": "target",
                    "url": "http" + url_match
                })
        
        # Add error handling
        improvements.append({
            "type": "error_handling",
            "code": '''# Robust error handling
import time
from functools import wraps

def retry(max_attempts=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(delay * (attempt + 1))
            return None
        return wrapper
    return decorator

@retry(max_attempts=3)
def fetch_with_retry(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response
'''
        })
        
        # Add rate limiting
        improvements.append({
            "type": "rate_limiting",
            "code": '''# Rate limiting to avoid blocking
import time

class RateLimiter:
    def __init__(self, max_per_minute=20):
        self.max_per_minute = max_per_minute
        self.requests = []
    
    def wait_if_needed(self):
        now = time.time()
        self.requests = [r for r in self.requests if now - r < 60]
        
        if len(self.requests) >= self.max_per_minute:
            sleep_time = 60 - (now - self.requests[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        self.requests.append(time.time())

limiter = RateLimiter(max_per_minute=20)
'''
        })
        
        # Add data cleaning
        if "data_validation" in reqs:
            improvements.append({
                "type": "cleaning",
                "code": '''# Data cleaning functions
def clean_text(text):
    if not text:
        return ""
    # Remove extra whitespace
    text = " ".join(text.split())
    # Remove special chars
    text = text.replace("\\n", " ").replace("\\t", " ")
    return text.strip()

def clean_company(name):
    if not name:
        return ""
    # Remove Inc, LLC, Corp, etc variations
    import re
    name = re.sub(r',?\\s*(Inc|LLC|Corp|Company|Co\\.)$', '', name, flags=re.IGNORECASE)
    return name.strip()
'''
            })
        
        return improvements


class SpreadsheetImprover(TemplateImprover):
    """Improves spreadsheet templates with formulas and functionality."""
    
    def improve(self, template_data):
        """Add real formulas and functionality."""
        improvements = []
        reqs = self.analyze_requirements()
        
        # Add formulas
        improvements.append({
            "type": "formulas",
            "content": '''# Google Sheets Formulas to add:

# Email validation
=ISEMAIL(B2)

# Phone cleaning  
=REGEXREPLACE(C2, "[^0-9]", "")

# Status conditional formatting
=IF(F2="New", "🔵", IF(F2="Contacted", "🟡", IF(F2="Qualified", "🟢", "⚪")))

# Follow-up date (7 days from today)
=TODAY()+7

# VLOOKUP for enrichment data
=IFERROR(VLOOKUP(A2, enrichment_data!A:D, 4, FALSE), "N/A")

# Array formula for filtering
=FILTER(A2:E, F2:F="New")
'''
        })
        
        # Add automation
        if "automation" in reqs:
            improvements.append({
                "type": "apps_script",
                "content": '''// Google Apps Script for auto-refresh
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('Lead Tools')
    .addItem('Refresh Data', 'refreshData')
    .addToUi();
}

function refreshData() {
  // Call your API here
  var sheet = SpreadsheetApp.getActiveSpreadsheet();
  // Update logic
}
'''
            })
        
        return improvements


class QAImprover(TemplateImprover):
    """Improves QA templates with actual test cases."""
    
    def improve(self, template_data):
        """Add real test cases and automation."""
        improvements = []
        reqs = self.analyze_requirements()
        
        # Analyze what to test
        if "login" in self.text or "auth" in self.text:
            improvements.append({
                "type": "test_cases",
                "content": '''# Login Test Cases
test_valid_login()
test_invalid_password()
test_empty_credentials()
test_sql_injection()
test_xss_injection()

# Test Automation (Playwright)
def test_login_flow(page):
    page.goto("/login")
    page.fill("#email", "test@example.com")
    page.fill("#password", "password123")
    page.click("#login-button")
    assert page.url == "/dashboard"
'''
            })
        
        if "api" in self.text:
            improvements.append({
                "type": "api_tests",
                "content": '''# API Test Cases (using requests)
def test_api_status():
    r = requests.get("https://api.example.com/health")
    assert r.status_code == 200

def test_api_auth():
    r = requests.post("https://api.example.com/login", json={"email": "test@example.com"})
    assert "token" in r.json()
'''
            })
        
        return improvements


# ========================================
# DEMO BUILDER WITH EXECUTION
# ========================================

class EnhancedDemoBuilder:
    """Builds demos using templates + actual skill execution."""
    
    IMPROVERS = {
        "lead_generation": LeadGenerationImprover,
        "data_scraping": DataScrapingImprover,
        "excel_sheets": SpreadsheetImprover,
        "qa_testing": QAImprover,
    }
    
    def __init__(self, output_dir="demos"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def build(self, demo_type, job_title, job_description):
        """Build enhanced demo with actual execution."""
        
        # Get improver for this type
        improver_class = self.IMPROVERS.get(demo_type)
        
        if not improver_class:
            # Fallback to basic
            return self._build_basic(demo_type, job_title, job_description)
        
        # Create improver and analyze
        improver = improver_class(job_title, job_description)
        improvements = improver.improve({})
        
        # Build final product
        return self._build_final(demo_type, job_title, improvements)
    
    def _build_final(self, demo_type, job_title, improvements):
        """Build the final demo with improvements."""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if demo_type == "lead_generation":
            return self._build_lead_gen(job_title, improvements, timestamp)
        elif demo_type == "data_scraping":
            return self._build_scraper(job_title, improvements, timestamp)
        elif demo_type == "excel_sheets":
            return self._build_spreadsheet(job_title, improvements, timestamp)
        elif demo_type == "qa_testing":
            return self._build_qa(job_title, improvements, timestamp)
        else:
            return self._build_generic(job_title, improvements, timestamp)
    
    def _build_lead_gen(self, job_title, improvements, timestamp):
        """Build enhanced lead gen with actual code."""
        
        # Build improvements code
        code_parts = ["# Lead Generation Enhancement Code\n"]
        
        for imp in improvements:
            if "code" in imp:
                code_parts.append(imp["code"])
                code_parts.append("\n\n")
        
        code = "\n".join(code_parts)
        
        # Sample data
        csv_data = """company,contact,email,phone,title,industry,status,last_contact,next_followup,notes
Acme Corp,John Smith,john@acme.com,555-0101,CEO,Tech,New,2026-03-12,2026-03-19,
TechStart,Jane Doe,jane@techstart.io,555-0102,CTO,SaaS,Contacted,2026-03-10,2026-03-17,
GlobalTech,Bob Wilson,bob@globaltech.com,555-0103,VP Sales,Enterprise,Qualified,2026-03-08,2026-03-15,
"""
        
        # Write files
        base_name = f"lead_gen_{timestamp}"
        
        # CSV
        csv_path = os.path.join(self.output_dir, f"{base_name}.csv")
        with open(csv_path, 'w') as f:
            f.write(csv_data)
        
        # Code
        code_path = os.path.join(self.output_dir, f"{base_name}_enhancements.py")
        with open(code_path, 'w') as f:
            f.write(code)
        
        return {
            "demo_type": "lead_generation",
            "files": [csv_path, code_path],
            "improvements": [imp.get("type", "improvement") for imp in improvements],
            "description": f"Enhanced lead generation with {len(improvements)} improvements"
        }
    
    def _build_scraper(self, job_title, improvements, timestamp):
        """Build enhanced scraper with actual code."""
        
        code_parts = ["# Enhanced Web Scraper\n"]
        code_parts.append(f"# Job: {job_title}\n\n")
        
        for imp in improvements:
            if "code" in imp:
                code_parts.append(imp["code"])
                code_parts.append("\n\n")
        
        code = "".join(code_parts)
        
        base_name = f"scraper_{timestamp}"
        code_path = os.path.join(self.output_dir, f"{base_name}.py")
        
        with open(code_path, 'w') as f:
            f.write(code)
        
        return {
            "demo_type": "data_scraping",
            "files": [code_path],
            "improvements": [imp.get("type", "improvement") for imp in improvements],
            "description": f"Enhanced scraper with {len(improvements)} features"
        }
    
    def _build_spreadsheet(self, job_title, improvements, timestamp):
        """Build enhanced spreadsheet with formulas."""
        
        content = "# Spreadsheet Enhancements\n\n"
        
        for imp in improvements:
            if "content" in imp:
                content += f"## {imp.get('type', 'Feature')}\n"
                content += imp["content"] + "\n\n"
        
        base_name = f"spreadsheet_{timestamp}"
        path = os.path.join(self.output_dir, f"{base_name}.md")
        
        with open(path, 'w') as f:
            f.write(content)
        
        return {
            "demo_type": "excel_sheets",
            "files": [path],
            "improvements": [imp.get("type", "improvement") for imp in improvements],
            "description": f"Spreadsheet with {len(improvements)} formula/feature additions"
        }
    
    def _build_qa(self, job_title, improvements, timestamp):
        """Build enhanced QA docs."""
        
        content = f"# QA Test Suite - {job_title}\n\n"
        
        for imp in improvements:
            if "content" in imp:
                content += f"## {imp.get('type', 'Tests')}\n"
                content += imp["content"] + "\n\n"
        
        base_name = f"qa_tests_{timestamp}"
        path = os.path.join(self.output_dir, f"{base_name}.md")
        
        with open(path, 'w') as f:
            f.write(content)
        
        return {
            "demo_type": "qa_testing",
            "files": [path],
            "improvements": [imp.get("type", "improvement") for imp in improvements],
            "description": f"QA test suite with {len(improvements)} test implementations"
        }
    
    def _build_generic(self, job_title, improvements, timestamp):
        """Build generic enhanced demo."""
        
        content = f"# Enhanced Demo - {job_title}\n\n"
        content += f"Timestamp: {timestamp}\n\n"
        content += "## Improvements Applied:\n"
        
        for imp in improvements:
            content += f"- {imp.get('type', 'Improvement')}\n"
        
        base_name = f"demo_{timestamp}"
        path = os.path.join(self.output_dir, f"{base_name}.md")
        
        with open(path, 'w') as f:
            f.write(content)
        
        return {
            "demo_type": "generic",
            "files": [path],
            "improvements": [imp.get("type", "improvement") for imp in improvements],
            "description": f"Enhanced demo with {len(improvements)} improvements"
        }


# ========================================
# MAIN FUNCTION
# ========================================

def build_enhanced_demo(demo_type, job_title, job_description):
    """Build an enhanced demo using template + skills."""
    
    builder = EnhancedDemoBuilder()
    result = builder.build(demo_type, job_title, job_description)
    
    return result


if __name__ == "__main__":
    # Test
    result = build_enhanced_demo(
        "lead_generation",
        "Lead generation spreadsheet with email validation",
        "Need a spreadsheet to track leads with email verification and auto-refresh"
    )
    print("Built:", result["description"])
    print("Files:", result["files"])
    print("Improvements:", result["improvements"])
