
# Upwork Proposal Skill - ULTIMATE Version
# With portfolio, proof/results, client research, and variations

import os
import subprocess
import tempfile
import random
import requests

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
        ],
        "proof": [
            "I've generated 10,000+ verified leads for SaaS clients",
            "My average lead verification rate is 85%",
            "Clients see 40% increase in outreach response rates"
        ],
        "quick_win": "I can start with a free audit of your current list"
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
        ],
        "proof": [
            "Extracted data from 500+ websites without blocks",
            "Average delivery is 50k+ records per project",
            "99.5% data accuracy rate across projects"
        ],
        "quick_win": "I can show you a sample scraper for your top site today"
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
        ],
        "proof": [
            "Completed 200+ research projects for startups",
            "Average research saves clients 20+ hours weekly",
            "Clients use my research to secure funding"
        ],
        "quick_win": "I can deliver a research outline within 2 hours"
    },
    "webhook_automation": {
        "name": "Webhook and Automation",
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
        ],
        "proof": [
            "Built 150+ automation workflows for clients",
            "Clients save average 10 hours per week per automation",
            "99.9% workflow uptime across all my setups"
        ],
        "quick_win": "I can map out your automation flow today - free"
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
        ],
        "proof": [
            "Average 25% response rate on my outreach",
            "Generated $2M+ in pipeline for clients",
            "Clients see results within first week"
        ],
        "quick_win": "I can write 3 personalized outreach templates today"
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
        ],
        "proof": [
            "Built 300+ custom spreadsheets and dashboards",
            "Average automation saves clients 5+ hours weekly",
            "99% client satisfaction on delivery"
        ],
        "quick_win": "I can fix your top 3 formula errors today - free"
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
        ],
        "proof": [
            "Supported 50+ busy executives and entrepreneurs",
            "Clients reclaim 15+ hours per week",
            "Average client relationship is 12+ months"
        ],
        "quick_win": "I can start with your most time-consuming task today"
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
        ],
        "proof": [
            "Set up 100+ Notion workspaces for clients",
            "Clients average 50% time savings on organization",
            "Features include advanced automations"
        ],
        "quick_win": "I can share a template for your use case today"
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
        ],
        "proof": [
            "Found 5000+ bugs before production",
            "Average 95% bug detection rate",
            "Clients see 60% reduction in post-launch issues"
        ],
        "quick_win": "I can create a test plan for your project today"
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
        ],
        "proof": [
            "Built 200+ email sequences for clients",
            "Average 35% open rate (industry avg is 21%)",
            "Clients see 3x increase in conversions"
        ],
        "quick_win": "I can audit your current sequence for free"
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
        ],
        "proof": [
            "Grew client accounts by 10k+ followers avg",
            "50%+ engagement rate on managed accounts",
            "Clients see results within first month"
        ],
        "quick_win": "I can create a content calendar this week"
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
        ],
        "proof": [
            "Repurposed 1000+ content pieces for clients",
            "Clients get 5x more mileage from each content",
            "Average 200% increase in content reach"
        ],
        "quick_win": "I can repurpose 1 piece as a sample today"
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
        ],
        "proof": [
            "Processed 10,000+ PDF files for clients",
            "100% accuracy on OCR conversions",
            "Same-day delivery on 90% of projects"
        ],
        "quick_win": "I can convert 1 file as sample today"
    }
}

# =======================
# DEEP PERSONALIZATION ENGINE
# =======================

# Pain points and solutions by category
PAIN_SOLUTIONS = {
    "lead_generation": {
        "time consuming": "I can build automated systems to generate leads while you focus on closing deals",
        "not qualified": "I verify every contact with email/phone validation",
        "messy data": "I clean and organize all data in a structured format",
        "expensive": "My efficient process saves you 40% vs traditional methods",
        "low response": "I personalize outreach to increase response rates"
    },
    "data_scraping": {
        "getting blocked": "I implement proxy rotation and polite rate limiting",
        "data not accurate": "I validate and cross-reference data for accuracy",
        "hard to use": "I deliver in clean CSV/JSON formats you can use immediately",
        "slow": "I optimize scrapers for maximum speed without triggering blocks"
    },
    "excel_sheets": {
        "slow": "I build automated formulas that update instantly",
        "errors": "I add data validation to prevent mistakes",
        "hard to understand": "I create intuitive dashboards with clear visuals",
        "manual": "I add Google Apps Script to automate repetitive tasks"
    },
    "webhook_automation": {
        "complicated": "I simplify complex workflows into easy steps",
        "not working": "I thoroughly test every trigger and action",
        "expensive": "I use free tools like Make.com to minimize costs",
        "integration": "I connect any two apps regardless of available integrations"
    },
    "cold_outreach": {
        "no responses": "My personalized approach gets 3x more replies",
        "getting marked spam": "I use warm-up accounts and proper sending volumes",
        "time consuming": "I automate follow-ups so you don't have to manual check"
    },
    "virtual_assistant": {
        "disorganized": "I create systems to keep everything structured",
        "missed tasks": "I set up reminders and automated workflows",
        "communication issues": "I provide detailed daily summaries"
    },
    "notion_setup": {
        "overwhelming": "I simplify your workflow into easy steps",
        "not organized": "I create custom databases that make sense",
        "not using": "I build templates you'll actually want to use daily"
    },
    "qa_testing": {
        "bugs": "I find bugs before users do",
        "not enough testing": "I create comprehensive test plans",
        "regression": "I automate tests to catch future issues"
    },
    "email_automation": {
        "low open rates": "I optimize subject lines and send times",
        "not converting": "I A/B test to find what works",
        "complicated": "I build simple flows that anyone can manage"
    },
    "social_media": {
        "no time": "I handle everything so you can focus on business",
        "not growing": "I use proven strategies to grow your following",
        "inconsistent": "I schedule content in advance for consistency"
    },
    "content_repurposing": {
        "not enough content": "I maximize every piece of content you have",
        "wrong format": "I adapt content for each platform's requirements",
        "time consuming": "I have systems to repurpose quickly"
    },
    "pdf_services": {
        "wrong format": "I convert to any format you need",
        "not searchable": "I add OCR so you can search everything",
        "can't edit": "I create fully editable versions"
    },
    "research_assistant": {
        "no time": "I do the research so you can make decisions",
        "overwhelmed": "I synthesize vast info into actionable insights",
        "incomplete": "I provide comprehensive reports with sources"
    }
}

# Custom proof statements by industry
INDUSTRY_PROOF = {
    "saas": [
        "I've helped 15+ SaaS companies build their outbound pipeline",
        "My lead generation has contributed to $5M+ in pipeline for SaaS clients",
        "I understand the SaaS sales cycle and create targeted lists"
    ],
    "ecommerce": [
        "I've scraped 100+ e-commerce sites for pricing intelligence",
        "My data helps e-commerce clients make pricing decisions daily",
        "I understand e-commerce data needs - product, price, inventory"
    ],
    "healthcare": [
        "I understand HIPAA considerations in healthcare data",
        "I've worked with 10+ healthcare companies on data projects",
        "I know how to handle sensitive medical data properly"
    ],
    "finance": [
        "I understand financial data accuracy is critical",
        "I've helped fintech companies scrape and validate market data",
        "I know how to handle sensitive financial information"
    ],
    "real estate": [
        "I've extracted data from 200+ real estate listing sites",
        "I understand real estate data - listings, agent, pricing",
        "I know how to handle the volume of real estate data"
    ],
    "education": [
        "I've helped 20+ edtech companies with content and research",
        "I understand the education market and buyer personas",
        "I've created content that drives enrollments"
    ]
}

# Opening templates - highly personalized
PERSONALIZED_OPENINGS = {
    "lead_generation": [
        "I saw you're looking to build a prospect list - I've generated thousands of leads for businesses like yours",
        "Your need for targeted leads caught my attention - I've helped companies scale their outreach",
        "Building a quality lead list is tough - I've done this for 50+ companies"
    ],
    "data_scraping": [
        "I noticed you need data extracted - I've scraped hundreds of sites and know how to handle the challenges",
        "Your data extraction needs are exactly what I specialize in",
        "Getting clean data from websites is harder than it looks - I've mastered this"
    ],
    "excel_sheets": [
        "I saw your spreadsheet challenges - I fix and build Excel/Sheets solutions daily",
        "Your need for better spreadsheets is something I solve weekly for clients",
        "Turning messy data into useful sheets is my bread and butter"
    ],
    "webhook_automation": [
        "I noticed you need automation - I've built 150+ workflows for clients",
        "Your desire to automate sounds exactly like what I help with daily",
        "Connecting your apps shouldn't be complicated - I've done it hundreds of times"
    ],
    "cold_outreach": [
        "I saw you're looking to improve outreach - I've helped 30+ clients increase response rates",
        "Your outreach challenges are exactly what I specialize in",
        "Getting replies from cold outreach is hard - I've cracked the code"
    ]
}

# Default openings for categories not listed
DEFAULT_OPENINGS = [
    "I saw your project and it's exactly the type of work I do regularly",
    "Your posting caught my attention - I've helped many clients with similar needs",
    "I understand what you're looking for - this is my specialty"
]


def deep_analyze_job(job_description, category):
    """Deep analysis of job for personalization."""
    text = job_description.lower()
    
    analysis = {
        "specific_pain": None,
        "industry": None,
        "company_size": "Unknown",
        "timeline": None,
        "budget": None,
        "tools_mentioned": [],
        "custom_opening": None,
        "personalized_proof": None
    }
    
    # Detect specific pain points
    pain_points = ["time consuming", "not qualified", "messy", "expensive", "slow", 
                   "errors", "hard", "complicated", "not working", "getting blocked",
                   "low response", "no results", "overwhelmed", "disorganized"]
    
    for pain in pain_points:
        if pain in text:
            analysis["specific_pain"] = pain
            break
    
    # Detect industry
    industries = {
        'saas': ['saas', 'software', 'b2b', 'app', 'subscription'],
        'ecommerce': ['ecommerce', 'shopify', 'store', 'retail', 'amazon'],
        'healthcare': ['health', 'medical', 'doctor', 'healthcare', 'patient'],
        'finance': ['finance', 'fintech', 'banking', 'investment', 'trading'],
        'real estate': ['real estate', 'property', 'realtor', 'listing'],
        'education': ['education', 'course', 'learning', 'training', 'edtech']
    }
    
    for ind, keywords in industries.items():
        if any(k in text for k in keywords):
            analysis["industry"] = ind
            break
    
    # Detect company size
    if any(x in text for x in ['enterprise', 'large', 'corporation', '500+', 'big']):
        analysis["company_size"] = "Enterprise"
    elif any(x in text for x in ['startup', 'small', 'growing', 'new', 'founder']):
        analysis["company_size"] = "Startup/Small"
    
    # Detect timeline
    if any(x in text for x in ['urgent', 'asap', 'immediately', 'emergency']):
        analysis["timeline"] = "urgent"
    elif any(x in text for x in ['this week', 'quickly']):
        analysis["timeline"] = "this week"
    elif any(x in text for x in ['flexible', 'whenever', 'no rush']):
        analysis["timeline"] = "flexible"
    
    # Detect tools mentioned
    all_tools = ['python', 'excel', 'google sheets', 'zapier', 'make', 'selenium', 
                 'beautifulsoup', 'scrapy', 'mailchimp', 'hubspot', 'salesforce',
                 'shopify', 'wordpress', 'notion', 'airtable']
    for tool in all_tools:
        if tool in text:
            analysis["tools_mentioned"].append(tool)
    
    # Generate personalized opening
    if category in PERSONALIZED_OPENINGS:
        analysis["custom_opening"] = random.choice(PERSONALIZED_OPENINGS[category])
    else:
        analysis["custom_opening"] = random.choice(DEFAULT_OPENINGS)
    
    # Generate personalized proof based on industry
    if analysis["industry"] and analysis["industry"] in INDUSTRY_PROOF:
        analysis["personalized_proof"] = random.choice(INDUSTRY_PROOF[analysis["industry"]])
    
    return analysis


def build_personalized_approach(category, pain_point, tools_mentioned):
    """Build customized approach based on job specifics."""
    approach = []
    
    # Get base approaches
    base = CATEGORY_TEMPLATES.get(category, CATEGORY_TEMPLATES["research_assistant"])
    
    # If pain point identified, add solution
    if pain_point and category in PAIN_SOLUTIONS:
        solution = PAIN_SOLUTIONS[category].get(pain_point)
        if solution:
            approach.append(solution)
    
    # Add tool-specific approaches
    for tool in tools_mentioned[:2]:
        if tool in ['python', 'beautifulsoup', 'scrapy']:
            approach.append("Using Python and modern libraries for reliable results")
        elif tool in ['excel', 'google sheets']:
            approach.append("Building clean, automated spreadsheets in Excel/Google Sheets")
        elif tool in ['zapier', 'make']:
            approach.append(f"Setting up {tool.title()} for seamless automation")
        elif tool in ['selenium']:
            approach.append("Using Selenium for complex automation scenarios")
    
    # Fill remaining with base approaches
    for a in base["approach"]:
        if len(approach) >= 3:
            break
        if a not in approach:
            approach.append(a)
    
    return approach[:3]


def generate_truly_personalized_proposal(job_description, job_title="", client_name="", 
                                        hourly_rate=25, profile_name="Your Freelancer",
                                        variation=1, humanize=True):
    """Generate a TRULY personalized proposal using deep analysis."""
    
    # Step 1: Deep analysis
    category = detect_category(job_description)
    analysis = deep_analyze_job(job_description, category)
    
    # Step 2: Get template
    template = CATEGORY_TEMPLATES.get(category, CATEGORY_TEMPLATES["research_assistant"])
    
    # Step 3: Calculate pricing
    difficulty = 0.6 if len(job_description) > 300 else 0.4 if len(job_description) > 100 else 0.2
    pricing = calculate_pricing(difficulty, hourly_rate)
    
    # Step 4: Build personalized approach
    approach = build_personalized_approach(category, analysis["specific_pain"], 
                                           analysis["tools_mentioned"])
    
    # Step 5: Select proof (prioritize industry-specific)
    if analysis["personalized_proof"]:
        proof = analysis["personalized_proof"]
    else:
        proof = random.choice(template["proof"])
    
    # Step 6: Get quick win
    quick_win = template["quick_win"]
    
    # Step 7: Get screening question
    screening = random.choice(template["screening"])
    
    # Step 8: Get portfolio
    portfolio = get_portfolio_items(category)
    
    # Step 9: Build the personalized proposal
    custom_opening = analysis["custom_opening"] or template["name"]
    
    if variation == 1:  # Professional
        proposal = f"""Hi {client_name or 'there'},

{custom_opening}. {proof}.

Here's my approach for your project:
{chr(10).join('* ' + a for a in approach)}

Timeline: {round(pricing['hours'] / 8)} days
Investment: ${pricing['total']} (milestone-based)

{screening}

{quick_win}

Best,
{profile_name}"""
    
    elif variation == 2:  # Results-focused
        proposal = f"""Hi {client_name or 'there'},

{analysis['custom_opening']}

I've helped companies with exactly this:
{chr(10).join('* ' + a for a in [proof, quick_win])}

Deliverable in {round(pricing['hours'] / 8)} days for ${pricing['total']}

Question: {screening}

{profile_name}"""
    
    else:  # Friendly
        proposal = f"""Hey {client_name or 'there'},

{analysis['custom_opening']} - {proof}

What I'll do:
{chr(10).join('* ' + a for a in approach)}

${pricing['total']} | {round(pricing['hours'] / 8)} days

{screening}

- {profile_name}"""
    
    # Step 10: Humanize if enabled
    if humanize:
        proposal = humanize_proposal(proposal)
    
    return {
        "category": category,
        "template": template["name"],
        "proposal": proposal,
        "pricing": pricing,
        "analysis": analysis,
        "approach": approach,
        "proof_used": proof,
        "quick_win": quick_win,
        "portfolio": portfolio,
        "variation": variation,
        "humanized": humanize
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

# Portfolio items - ADD YOUR ACTUAL LINKS HERE
PORTFOLIO = {
    "lead_generation": [
        {"title": "B2B SaaS Lead List", "description": "5,000 verified leads", "link": "YOUR_LINK_HERE"},
        {"title": "Healthcare Prospect Database", "description": "2,000 medical device leads", "link": "YOUR_LINK_HERE"}
    ],
    "data_scraping": [
        {"title": "E-commerce Price Monitor", "description": "50 sites, daily updates", "link": "YOUR_LINK_HERE"},
        {"title": "Real Estate Data Extraction", "description": "10k property listings", "link": "YOUR_LINK_HERE"}
    ],
    "research_assistant": [
        {"title": "Competitor Analysis Report", "description": "50-page market analysis", "link": "YOUR_LINK_HERE"},
        {"title": "Industry Trends Report", "description": "Emerging tech analysis", "link": "YOUR_LINK_HERE"}
    ],
    "webhook_automation": [
        {"title": "CRM-Email Automation", "description": "HubSpot + Gmail integration", "link": "YOUR_LINK_HERE"},
        {"title": "Shopify Order Notifications", "description": "Real-time order alerts", "link": "YOUR_LINK_HERE"}
    ],
    "excel_sheets": [
        {"title": "Financial Dashboard", "description": "Real-time P&L tracking", "link": "YOUR_LINK_HERE"},
        {"title": "Inventory Management System", "description": "Auto-updating stock tracker", "link": "YOUR_LINK_HERE"}
    ],
    "cold_outreach": [
        {"title": "LinkedIn Outreach Campaign", "description": "500 personalized messages", "link": "YOUR_LINK_HERE"},
        {"title": "Email Sequence", "description": "5-email follow-up sequence", "link": "YOUR_LINK_HERE"}
    ],
    "virtual_assistant": [
        {"title": "Executive Support Package", "description": "Calendar + email management", "link": "YOUR_LINK_HERE"},
        {"title": "Data Entry Project", "description": "10k records organized", "link": "YOUR_LINK_HERE"}
    ],
    "notion_setup": [
        {"title": "Project Management System", "description": "Full workspace setup", "link": "YOUR_LINK_HERE"},
        {"title": "Content Calendar", "description": "Editorial workflow", "link": "YOUR_LINK_HERE"}
    ],
    "qa_testing": [
        {"title": "Web App Test Report", "description": "100+ test cases", "link": "YOUR_LINK_HERE"},
        {"title": "Mobile App Testing", "description": "iOS + Android", "link": "YOUR_LINK_HERE"}
    ],
    "email_automation": [
        {"title": "Welcome Sequence", "description": "7-email nurture", "link": "YOUR_LINK_HERE"},
        {"title": "Cart Abandonment Flow", "description": "3-email recovery", "link": "YOUR_LINK_HERE"}
    ],
    "social_media": [
        {"title": "Instagram Growth", "description": "10k followers in 3 months", "link": "YOUR_LINK_HERE"},
        {"title": "LinkedIn Content Plan", "description": "30-day content calendar", "link": "YOUR_LINK_HERE"}
    ],
    "content_repurposing": [
        {"title": "Video to Blog", "description": "10 videos converted", "link": "YOUR_LINK_HERE"},
        {"title": "Podcast Show Notes", "description": "20 episodes transcribed", "link": "YOUR_LINK_HERE"}
    ],
    "pdf_services": [
        {"title": "Form Creation", "description": "50-page fillable form", "link": "YOUR_LINK_HERE"},
        {"title": "OCR Project", "description": "100 scanned docs digitized", "link": "YOUR_LINK_HERE"}
    ]
}


def get_client_research(job_description):
    """Research the client based on job description."""
    research = {
        "company_size": "Unknown",
        "industry": "Unknown",
        "pain_points": [],
        "budget_range": "Not specified"
    }
    
    text = job_description.lower()
    
    # Detect company size
    if any(x in text for x in ['enterprise', 'large', 'corporation', '500+']):
        research['company_size'] = "Enterprise (500+)"
    elif any(x in text for x in ['mid-size', 'growing', '50-500']):
        research['company_size'] = "Mid-size (50-500)"
    elif any(x in text for x in ['startup', 'small', 'new', 'founder']):
        research['company_size'] = "Startup/Small (1-50)"
    
    # Detect industry
    industries = {
        'saas': ['saas', 'software', 'b2b', 'app'],
        'ecommerce': ['e-commerce', 'ecommerce', 'shopify', 'store'],
        'healthcare': ['health', 'medical', 'healthcare', 'doctor'],
        'finance': ['finance', 'fintech', 'banking', 'investment'],
        'real estate': ['real estate', 'property', 'realtor'],
        'education': ['education', 'course', 'learning', 'training']
    }
    for ind, keywords in industries.items():
        if any(k in text for k in keywords):
            research['industry'] = ind.title()
            break
    
    # Detect pain points
    pain_keywords = {
        'time': ['time consuming', 'takes too long', 'hours'],
        'quality': ['poor quality', 'messy', 'disorganized'],
        'cost': ['expensive', 'cost too much', 'budget'],
        'automation': ['manual', 'repetitive', 'automate']
    }
    for pain, keywords in pain_keywords.items():
        if any(k in text for k in keywords):
            research['pain_points'].append(pain)
    
    return research


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
            {"title": "Discovery and Plan", "percent": 30, "amount": round(total * 0.3)},
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


def get_portfolio_items(category, max_items=2):
    """Get relevant portfolio items for a category."""
    items = PORTFOLIO.get(category, [])
    return random.sample(items, min(len(items), max_items)) if items else []


def generate_proposal(job_description, job_title="", client_name="", hourly_rate=25, 
                     profile_name="Your Freelancer", variation=1):
    """Generate a proposal using the ULTIMATE hybrid template approach."""
    
    # Step 1: Research client
    research = get_client_research(job_description)
    
    # Step 2: Detect category
    category = detect_category(job_description)
    template = CATEGORY_TEMPLATES.get(category, CATEGORY_TEMPLATES["research_assistant"])
    
    # Step 3: Calculate difficulty
    difficulty = 0.6 if len(job_description) > 300 else 0.4 if len(job_description) > 100 else 0.2
    
    # Step 4: Calculate pricing
    pricing = calculate_pricing(difficulty, hourly_rate)
    
    # Step 5: Get proof statements
    proof = random.choice(template["proof"])
    
    # Step 6: Get quick win
    quick_win = template["quick_win"]
    
    # Step 7: Get screening question
    screening_question = random.choice(template["screening"])
    
    # Step 8: Get portfolio items
    portfolio = get_portfolio_items(category)
    
    # Step 9: Extract personalization
    key_phrase = job_description[:100].split('.')[0][:60]
    
    # Step 10: Build proposal with variation
    if variation == 1:
        # Standard professional
        proposal = f"""Hi {client_name or 'there'},

I noticed you mentioned "{key_phrase}". {proof}.

My approach:
{chr(10).join('* ' + a for a in template['approach'])}

Tools I'll use: {', '.join(template['tools'][:4])}

Timeline: {round(pricing['hours'] / 8)} business days
Investment: ${pricing['total']} (paid via milestones)

{screening_question}

{quick_win}

Best,
{profile_name}"""
    
    elif variation == 2:
        # Results-focused
        proposal = f"""Hi {client_name or 'there'},

Your project about "{key_phrase}" caught my attention. {proof}.

Here's how I'll help:
{chr(10).join('* ' + a for a in template['approach'])}

Delivery: {round(pricing['hours'] / 8)} days | ${pricing['total']}

{quick_win}. Happy to share relevant samples.

Question: {screening_question}

Talk soon,
{profile_name}"""
    
    else:
        # Friendly casual
        proposal = f"""Hey {client_name or 'there'},

Saw your post about "{key_phrase}" - I'd love to help with this!

Quick background: {proof}

What I'll do:
{chr(10).join('* ' + a for a in template['approach'])}

Budget: ${pricing['total']} | Timeline: ~{round(pricing['hours'] / 8)} days

{screening_question}

Let me know if you want to chat!
{profile_name}"""
    
    return {
        "category": category,
        "template": template["name"],
        "proposal": proposal,
        "pricing": pricing,
        "difficulty": difficulty,
        "screening_question": screening_question,
        "proof_used": proof,
        "quick_win": quick_win,
        "portfolio": portfolio,
        "research": research,
        "variation": variation
    }


# =======================
# HUMANIZE INTEGRATION
# =======================

def get_humanizer_path():
    """Get the path to the humanize-ai-text transform script."""
    possible_paths = [
        os.path.join(os.path.dirname(__file__), '..', 'humanize-ai-text', 'scripts', 'transform.py'),
        os.path.join(os.path.dirname(__file__), 'humanize-ai-text', 'scripts', 'transform.py'),
        'skills/humanize-ai-text/scripts/transform.py',
        'humanize-ai-text/scripts/transform.py'
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return possible_paths[0]


def humanize_proposal(proposal_text):
    """Humanize a proposal using the humanize-ai-text skill."""
    try:
        script_path = get_humanizer_path()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(proposal_text)
            temp_input = f.name
        
        temp_output = temp_input.replace('.txt', '_human.txt')
        
        result = subprocess.run(
            ['python', script_path, temp_input, '-o', temp_output, '-q'],
            capture_output=True,
            timeout=30,
            text=True
        )
        
        if os.path.exists(temp_output):
            with open(temp_output, 'r', encoding='utf-8') as f:
                humanized = f.read()
            
            try:
                os.remove(temp_input)
                os.remove(temp_output)
            except:
                pass
            
            return humanized.strip()
        
        try:
            os.remove(temp_input)
        except:
            pass
            
        return proposal_text
        
    except Exception as e:
        print(f"Humanize error: {e}")
        return proposal_text


def generate_ultimate_proposal(job_description, job_title="", client_name="", hourly_rate=25, 
                              profile_name="Your Freelancer", humanize=True, variation=None):
    """Generate the ultimate proposal with all enhancements.
    
    Args:
        job_description: The job description text
        job_title: Title of the job
        client_name: Name of the client
        hourly_rate: Your hourly rate
        profile_name: Your name
        humanize: Whether to humanize the proposal
        variation: 1 (professional), 2 (results), 3 (friendly)
    
    Returns:
        Dictionary with proposal and all metadata
    """
    # Random variation if not specified
    if variation is None:
        variation = random.randint(1, 3)
    
    # Step 1: Generate base proposal with all enhancements
    result = generate_proposal(
        job_description, 
        job_title, 
        client_name, 
        hourly_rate, 
        profile_name,
        variation
    )
    
    # Step 2: Humanize if enabled
    if humanize:
        result['proposal'] = humanize_proposal(result['proposal'])
        result['humanized'] = True
    else:
        result['humanized'] = False
    
    return result


if __name__ == "__main__":
    # Test
    test_job = "Need help with lead generation for B2B SaaS companies. Looking for someone to build prospect list with verified emails."
    result = generate_ultimate_proposal(test_job, "Lead Generation Job", "Client", humanize=False)
    print(f"Category: {result['category']}")
    print(f"Template: {result['template']}")
    print(f"Variation: {result['variation']}")
    print(f"Proof: {result['proof_used']}")
    print(f"Quick Win: {result['quick_win']}")
    print(f"Portfolio: {len(result['portfolio'])} items")
    print(f"\nProposal:\n{result['proposal']}")
    print(f"\nPricing: ${result['pricing']['total']}")
