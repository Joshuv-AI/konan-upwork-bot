# Upwork Proposal Skill - Python Version
# Integrates with upwork-api.py

CATEGORY_TEMPLATES = {
    "lead_generation": {
        "name": "Lead Generation",
        "tools": ["Python", "LinkedIn Sales Navigator", "Apollo.io", "Google Sheets", "Airtable"],
        "approach": [
            "Build targeted prospect list based on your criteria",
            "Verify and enrich contact data (email, phone, LinkedIn)",
            "Deliver clean, organized spreadsheet ready for outreach"
        ],
        "screening": [
            "What's your target industry or ideal customer profile?",
            "Do you have existing leads to filter from?",
            "What's your goal - cold outreach or existing contacts?"
        ]
    },
    "data_scraping": {
        "name": "Data Scraping",
        "tools": ["Python", "BeautifulSoup", "Scrapy", "Selenium", "Proxy rotation"],
        "approach": [
            "Build custom scraper tailored to your target sites",
            "Handle anti-bot measures and rate limiting",
            "Deliver structured data in your preferred format"
        ],
        "screening": [
            "What specific sites do you need data from?",
            "What data fields are you looking for?",
            "Do you need ongoing updates or one-time extraction?"
        ]
    },
    "research_assistant": {
        "name": "Research Assistant",
        "tools": ["Market research", "Competitive analysis", "Data synthesis", "Google"],
        "approach": [
            "Conduct thorough research on your topic",
            "Compile findings into actionable report",
            "Provide sources and next steps"
        ],
        "screening": [
            "What's the specific topic or question?",
            "What format do you prefer - report, spreadsheet?",
            "Any specific sources you want included?"
        ]
    },
    "webhook_automation": {
        "name": "Webhook & Automation",
        "tools": ["Zapier", "Make.com", "Webhooks", "API integrations"],
        "approach": [
            "Design automation workflow for your process",
            "Set up triggers and actions",
            "Test and document the automation"
        ],
        "screening": [
            "What apps or services need to connect?",
            "What's the trigger and desired outcome?",
            "How often does this need to run?"
        ]
    },
    "cold_outreach": {
        "name": "Cold Outreach",
        "tools": ["Email outreach", "LinkedIn DMs", "Copywriting", "Personalization"],
        "approach": [
            "Research and personalize for each prospect",
            "Write compelling copy that converts",
            "Set up sequence with follow-ups"
        ],
        "screening": [
            "Who is your ideal customer?",
            "What's your value proposition?",
            "What platforms - email, LinkedIn, or both?"
        ]
    },
    "excel_sheets": {
        "name": "Excel / Google Sheets",
        "tools": ["Google Sheets", "Excel", "VBA", "Apps Script", "Dashboards"],
        "approach": [
            "Build or clean up your spreadsheet",
            "Add formulas, automation, and functions",
            "Create dashboard for easy monitoring"
        ],
        "screening": [
            "Do you have an existing spreadsheet to improve?",
            "What specific functions or features do you need?",
            "Will this be ongoing or one-time?"
        ]
    },
    "virtual_assistant": {
        "name": "Virtual Assistant",
        "tools": ["Calendar management", "Email management", "Research", "Data entry"],
        "approach": [
            "Handle administrative tasks efficiently",
            "Keep your schedule and inbox organized",
            "Research and compile information as needed"
        ],
        "screening": [
            "What tasks take most of your time?",
            "How do you prefer to communicate and report?",
            "What's your availability for ongoing support?"
        ]
    },
    "notion_setup": {
        "name": "Notion Setup",
        "tools": ["Notion", "Databases", "Templates", "Automations"],
        "approach": [
            "Set up Notion workspace tailored to your workflow",
            "Create templates and databases",
            "Train you on how to use and maintain"
        ],
        "screening": [
            "What's your current workflow or challenge?",
            "What features do you need - databases, calendars, docs?",
            "Will this be personal or team workspace?"
        ]
    },
    "qa_testing": {
        "name": "QA Testing",
        "tools": ["Manual testing", "Test cases", "Bug reports", "Regression testing"],
        "approach": [
            "Create test plan and test cases",
            "Execute thorough testing",
            "Document bugs and provide detailed reports"
        ],
        "screening": [
            "What's the application or feature to test?",
            "Do you have existing test cases?",
            "What types of testing - functional, UI, performance?"
        ]
    },
    "email_automation": {
        "name": "Email Automation",
        "tools": ["Mailchimp", "ConvertKit", "Klaviyo", "Sequences", "Template design"],
        "approach": [
            "Design email sequence for your goal",
            "Set up automation triggers",
            "Optimize for engagement"
        ],
        "screening": [
            "What's the goal - welcome series, sales, nurture?",
            "What platform do you use?",
            "Do you have existing templates or need new?"
        ]
    },
    "social_media": {
        "name": "Social Media Management",
        "tools": ["Content creation", "Scheduling", "Engagement", "Analytics"],
        "approach": [
            "Create and schedule content",
            "Engage with your audience",
            "Report on performance"
        ],
        "screening": [
            "Which platforms - Instagram, LinkedIn, Twitter, TikTok?",
            "How many posts per week?",
            "Do you provide content or need ideas?"
        ]
    },
    "content_repurposing": {
        "name": "Content Repurposing",
        "tools": ["Video editing", "Blog writing", "Social posts", "Transcription"],
        "approach": [
            "Transform existing content into multiple formats",
            "Maximize reach from each piece",
            "Adapt for each platform"
        ],
        "screening": [
            "What content do you have - video, blog, podcast?",
            "What formats do you want created?",
            "Any specific brand guidelines to follow?"
        ]
    },
    "pdf_services": {
        "name": "PDF Services",
        "tools": ["PDF editing", "OCR", "Form creation", "Conversion"],
        "approach": [
            "Convert, edit, or extract from PDFs",
            "Create fillable forms if needed",
            "Ensure quality and formatting"
        ],
        "screening": [
            "What's the current format and desired output?",
            "How many files need processing?",
            "Any specific formatting requirements?"
        ]
    }
}

CATEGORY_KEYWORDS = {
    "lead_generation": ["lead", "prospect", "b2b", "contact list", "email list"],
    "data_scraping": ["scrape", "extract", "data collection", "web crawl", "python"],
    "research_assistant": ["research", "market research", "analysis", "investigation"],
    "webhook_automation": ["zapier", "make.com", "automation", "webhook", "integrat"],
    "cold_outreach": ["cold email", "cold outreach", "email campaign", "linkedin"],
    "excel_sheets": ["excel", "spreadsheet", "google sheets", "formula", "dashboard"],
    "virtual_assistant": ["virtual assistant", "admin", "calendar", "scheduling"],
    "notion_setup": ["notion", "workspace", "database", "template"],
    "qa_testing": ["qa", "testing", "test case", "bug", "quality assurance"],
    "email_automation": ["email automation", "mailchimp", "klaviyo", "convertkit"],
    "social_media": ["social media", "instagram", "tiktok", "linkedin", "content"],
    "content_repurposing": ["repurpose", "video edit", "transcribe", "blog post"],
    "pdf_services": ["pdf", "ocr", "convert", "edit pdf", "form"]
}


def detect_category(job_description):
    """Detect which category a job belongs to."""
    text = job_description.lower()
    
    best_match = None
    best_score = 0
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > best_score:
            best_score = score
            best_match = category
    
    return best_match


def calculate_pricing(difficulty, hourly_rate=25):
    """Calculate pricing based on difficulty."""
    if difficulty <= 0.3:
        hours = 8
    elif difficulty <= 0.7:
        hours = 24
    else:
        hours = 80
    
    total = round(hourly_rate * hours)
    
    if hours < 20:
        milestones = [
            {"title": "Discovery & Plan", "percent": 30, "amount": round(total * 0.3)},
            {"title": "Implementation", "percent": 50, "amount": round(total * 0.5)},
            {"title": "Delivery", "percent": 20, "amount": round(total * 0.2)}
        ]
    else:
        milestones = [
            {"title": "Discovery", "percent": 20, "amount": round(total * 0.2)},
            {"title": "Core Work", "percent": 50, "amount": round(total * 0.5)},
            {"title": "Polish", "percent": 20, "amount": round(total * 0.2)},
            {"title": "Handover", "percent": 10, "amount": round(total * 0.1)}
        ]
    
    return {"hours": hours, "total": total, "milestones": milestones}


def generate_proposal(job_description, job_title="", client_name="", hourly_rate=25, profile_name="Your Freelancer"):
    """Generate a proposal using the hybrid template approach."""
    
    # Detect category
    category = detect_category(job_description)
    template = CATEGORY_TEMPLATES.get(category, CATEGORY_TEMPLATES["research_assistant"])
    
    # Calculate difficulty
    difficulty = 0.6 if len(job_description) > 300 else 0.4 if len(job_description) > 100 else 0.2
    
    # Calculate pricing
    pricing = calculate_pricing(difficulty, hourly_rate)
    
    # Get screening question
    import random
    screening_question = random.choice(template["screening"])
    
    # Extract key phrase for personalization
    key_phrase = job_description[:100].split('.')[0][:60]
    
    # Build proposal
    proposal = f"""Hi {client_name or 'there'},

I noticed you mentioned "{key_phrase}". I've helped clients with similar {template['name'].lower()} projects.

My approach:
{chr(10).join('• ' + a for a in template['approach'])}

Tools I'll use: {', '.join(template['tools'][:4])}

Timeline: {round(pricing['hours'] / 8)} business days
Investment: ${pricing['total']} (paid via milestones)

{screening_question}

Looking forward to hearing from you!

Best,
{profile_name}"""
    
    return {
        "category": category,
        "template": template["name"],
        "proposal": proposal,
        "pricing": pricing,
        "difficulty": difficulty,
        "screening_question": screening_question
    }


if __name__ == "__main__":
    # Test
    test_job = "Need help with lead generation for B2B SaaS companies. Looking for someone to build prospect list with verified emails."
    result = generate_proposal(test_job, "Lead Generation Job", "Client")
    print(f"Category: {result['category']}")
    print(f"Template: {result['template']}")
    print(f"\nProposal:\n{result['proposal']}")
    print(f"\nPricing: ${result['pricing']['total']}")
