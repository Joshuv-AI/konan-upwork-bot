/**
 * Upwork Proposal Skill - Hybrid Version
 * Combines our 13 templates with AI enhancement
 */

const CATEGORY_TEMPLATES = {
  lead_generation: {
    name: "Lead Generation",
    tools: ["Python", "LinkedIn Sales Navigator", "Apollo.io", "ZoomInfo", "Google Sheets", "Airtable"],
    approach: [
      "Build targeted prospect list based on your criteria",
      "Verify and enrich contact data (email, phone, LinkedIn)",
      "Deliver clean, organized spreadsheet ready for outreach"
    ],
    screening: [
      "What's your target industry or ideal customer profile?",
      "Do you have existing leads to filter from?",
      "What's your goal - cold outreach or existing contacts?"
    ]
  },
  data_scraping: {
    name: "Data Scraping",
    tools: ["Python", "BeautifulSoup", "Scrapy", "Selenium", "Playwright", "Proxy rotation"],
    approach: [
      "Build custom scraper tailored to your target sites",
      "Handle anti-bot measures and rate limiting",
      "Deliver structured data in your preferred format"
    ],
    screening: [
      "What specific sites do you need data from?",
      "What data fields are you looking for?",
      "Do you need ongoing updates or one-time extraction?"
    ]
  },
  research_assistant: {
    name: "Research Assistant",
    tools: ["Market research", "Competitive analysis", "Data synthesis", "Google", "Industry databases"],
    approach: [
      "Conduct thorough research on your topic",
      "Compile findings into actionable report",
      "Provide sources and next steps"
    ],
    screening: [
      "What's the specific topic or question?",
      "What format do you prefer - report, spreadsheet, presentation?",
      "Any specific sources or data you want included?"
    ]
  },
  webhook_automation: {
    name: "Webhook & Automation",
    tools: ["Zapier", "Make.com", "Webhooks", "API integrations", "IFTTT"],
    approach: [
      "Design automation workflow for your process",
      "Set up triggers and actions",
      "Test and document the automation"
    ],
    screening: [
      "What apps or services need to connect?",
      "What's the trigger and desired outcome?",
      "How often does this need to run?"
    ]
  },
  cold_outreach: {
    name: "Cold Outreach",
    tools: ["Email outreach", "LinkedIn DMs", "Copywriting", "Personalization", "Follow-ups"],
    approach: [
      "Research and personalize for each prospect",
      "Write compelling copy that converts",
      "Set up sequence with follow-ups"
    ],
    screening: [
      "Who is your ideal customer?",
      "What's your value proposition?",
      "What platforms - email, LinkedIn, or both?"
    ]
  },
  excel_sheets: {
    name: "Excel / Google Sheets",
    tools: ["Google Sheets", "Excel", "VBA", "Apps Script", "Formulas", "Dashboards"],
    approach: [
      "Build or clean up your spreadsheet",
      "Add formulas, automation, and formulas",
      "Create dashboard for easy monitoring"
    ],
    screening: [
      "Do you have an existing spreadsheet to improve?",
      "What specific functions or features do you need?",
      "Will this be ongoing or one-time?"
    ]
  },
  virtual_assistant: {
    name: "Virtual Assistant",
    tools: ["Calendar management", "Email management", "Research", "Data entry", "Scheduling"],
    approach: [
      "Handle administrative tasks efficiently",
      "Keep your schedule and inbox organized",
      "Research and compile information as needed"
    ],
    screening: [
      "What tasks take most of your time?",
      "How do you prefer to communicate and report?",
      "What's your availability for ongoing support?"
    ]
  },
  notion_setup: {
    name: "Notion Setup",
    tools: ["Notion", "Databases", "Templates", "Automations", "API integrations"],
    approach: [
      "Set up Notion workspace tailored to your workflow",
      "Create templates and databases",
      "Train you on how to use and maintain"
    ],
    screening: [
      "What's your current workflow or challenge?",
      "What features do you need - databases, calendars, docs?",
      "Will this be personal or team workspace?"
    ]
  },
  qa_testing: {
    name: "QA Testing",
    tools: ["Manual testing", "Test cases", "Bug reports", "Regression testing", "Cross-browser"],
    approach: [
      "Create test plan and test cases",
      "Execute thorough testing",
      "Document bugs and provide detailed reports"
    ],
    screening: [
      "What's the application or feature to test?",
      "Do you have existing test cases?",
      "What types of testing - functional, UI, performance?"
    ]
  },
  email_automation: {
    name: "Email Automation",
    tools: ["Mailchimp", "ConvertKit", "Klaviyo", "Sequences", "Template design"],
    approach: [
      "Design email sequence for your goal",
      "Set up automation triggers",
      "Optimize for engagement"
    ],
    screening: [
      "What's the goal - welcome series, sales, nurture?",
      "What platform do you use?",
      "Do you have existing templates or need new?"
    ]
  },
  social_media: {
    name: "Social Media Management",
    tools: ["Content creation", "Scheduling", "Engagement", "Analytics", "Multiple platforms"],
    approach: [
      "Create and schedule content",
      "Engage with your audience",
      "Report on performance"
    ],
    screening: [
      "Which platforms - Instagram, LinkedIn, Twitter, TikTok?",
      "How many posts per week?",
      "Do you provide content or need ideas?"
    ]
  },
  content_repurposing: {
    name: "Content Repurposing",
    tools: ["Video editing", "Blog writing", "Social posts", "Transcription", "Summarization"],
    approach: [
      "Transform existing content into multiple formats",
      "Maximize reach from each piece",
      "Adapt for each platform"
    ],
    screening: [
      "What content do you have - video, blog, podcast?",
      "What formats do you want created?",
      "Any specific brand guidelines to follow?"
    ]
  },
  pdf_services: {
    name: "PDF Services",
    tools: ["PDF editing", "OCR", "Form creation", "Conversion", "Extraction"],
    approach: [
      "Convert, edit, or extract from PDFs",
      "Create fillable forms if needed",
      "Ensure quality and formatting"
    ],
    screening: [
      "What's the current format and desired output?",
      "How many files need processing?",
      "Any specific formatting requirements?"
    ]
  }
};

function detectCategory(jobDescription) {
  const text = jobDescription.toLowerCase();
  
  const categoryKeywords = {
    lead_generation: ['lead', 'prospect', 'b2b', 'contact list', 'email list', 'outreach list'],
    data_scraping: ['scrape', 'extract', 'data collection', 'web crawl', 'python'],
    research_assistant: ['research', 'market research', 'analysis', 'investigation'],
    webhook_automation: ['zapier', 'make.com', 'automation', 'webhook', 'integrat'],
    cold_outreach: ['cold email', 'cold outreach', 'email campaign', 'linkedin'],
    excel_sheets: ['excel', 'spreadsheet', 'google sheets', 'formula', 'dashboard'],
    virtual_assistant: ['virtual assistant', 'admin', 'calendar', 'scheduling', 'support'],
    notion_setup: ['notion', 'workspace', 'database', 'template'],
    qa_testing: ['qa', 'testing', 'test case', 'bug', 'quality assurance'],
    email_automation: ['email automation', 'mailchimp', 'klaviyo', 'convertkit', 'sequence'],
    social_media: ['social media', 'instagram', 'tiktok', 'linkedin', 'content'],
    content_repurposing: ['repurpose', 'video edit', 'transcribe', 'blog post'],
    pdf_services: ['pdf', 'ocr', 'convert', 'edit pdf', 'form']
  };
  
  let bestMatch = null;
  let bestScore = 0;
  
  for (const [category, keywords] of Object.entries(categoryKeywords)) {
    const score = keywords.filter(k => text.includes(k)).length;
    if (score > bestScore) {
      bestScore = score;
      bestMatch = category;
    }
  }
  
  return bestMatch;
}

function calculatePricing(difficulty, hourlyRate = 25) {
  let hours;
  if (difficulty <= 0.3) hours = 8;
  else if (difficulty <= 0.7) hours = 24;
  else hours = 80;
  
  const total = Math.round(hourlyRate * hours);
  
  const milestones = hours < 20 ? [
    { title: 'Discovery & Plan', percent: 30, amount: Math.round(total * 0.3) },
    { title: 'Implementation', percent: 50, amount: Math.round(total * 0.5) },
    { title: 'Delivery', percent: 20, amount: Math.round(total * 0.2) }
  ] : [
    { title: 'Discovery', percent: 20, amount: Math.round(total * 0.2) },
    { title: 'Core Work', percent: 50, amount: Math.round(total * 0.5) },
    { title: 'Polish', percent: 20, amount: Math.round(total * 0.2) },
    { title: 'Handover', percent: 10, amount: Math.round(total * 0.1) }
  ];
  
  return { hours, total, milestones };
}

async function generateProposal({ job, profile = {}, hourlyRate = 25 }) {
  // Step 1: Detect category
  const category = detectCategory(job.description || job.job_description);
  const template = CATEGORY_TEMPLATES[category] || CATEGORY_TEMPLATES.research_assistant;
  
  // Step 2: Calculate difficulty
  const text = (job.description || job.job_description || '').toLowerCase();
  const difficulty = text.length > 300 ? 0.6 : text.length > 100 ? 0.4 : 0.2;
  
  // Step 3: Calculate pricing
  const pricing = calculatePricing(difficulty, hourlyRate);
  
  // Step 4: Get screening question
  const screeningQuestion = template.screening[Math.floor(Math.random() * template.screening.length)];
  
  // Step 5: Build proposal
  const clientName = job.client_name || 'there';
  const jobTitle = job.title || job.job_title || 'project';
  
  // Extract key phrase from job for personalization
  const keyPhrase = text.slice(0, 100).split('.').slice(0,1).join('.').slice(0, 60);
  
  const proposal = `Hi ${clientName},

I noticed you mentioned "${keyPhrase}". I've helped clients with similar ${template.name.toLowerCase()} projects.

My approach:
${template.approach.map(a => '• ' + a).join('\n')}

Tools I'll use: ${template.tools.slice(0, 4).join(', ')}

Timeline: ${Math.ceil(pricing.hours / 8)} business days
Investment: $${pricing.total} (paid via milestones)

${screeningQuestion}

Looking forward to hearing from you!

Best,
${profile.name || 'Your Freelancer'}`;

  return {
    category,
    template: template.name,
    proposal,
    pricing,
    difficulty,
    screeningQuestion
  };
}

module.exports = {
  generateProposal,
  detectCategory,
  calculatePricing,
  CATEGORY_TEMPLATES
};
