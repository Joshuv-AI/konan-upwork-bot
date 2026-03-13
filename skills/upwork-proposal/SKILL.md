---
name: upwork-proposal
description: Generate winning Upwork proposals using hybrid approach - combines our 13 category templates with AI enhancement for personalization. Use when generating proposals for Upwork jobs - handles scoring, template selection, pricing, milestones, and final polish.
---

# Upwork Proposal Generator

This skill generates professional Upwork proposals using a hybrid approach:
- **Base structure** from our 13 category templates
- **AI enhancement** for job-specific personalization
- **Scoring algorithm** to filter low-quality jobs
- **Pricing calculation** based on difficulty and hourly rate
- **Milestone generation** for secure payments

## When to Use

Trigger on:
- "generate proposal for Upwork job"
- "write Upwork proposal"
- "create job application"
- "make proposal for freelance job"
- Any request to write a proposal for Upwork/freelance work

---

## Step 1: Job Analysis

For each job, analyze:

### Required Information
- Job title
- Job description
- Client info (spend, rating, payment verified)
- Budget (if fixed) or implied budget
- Required skills mentioned
- Timeline mentioned

### Scoring (0-100)
Calculate match score:

```
keyword_score = keyword_match / total_keywords (weight: 50%)
skill_match = skills_matched / skills_required (weight: 20%)
client_quality = payment_verified(30%) + hire_rate(30%) + spend(20%) (weight: 20%)
budget_fit = job_budget / your_min_budget (weight: 10%)
```

### Threshold
- **Skip if score < 70%** - Not worth applying
- **Apply if score >= 70%** - Worth submitting
- **Strong apply if score >= 85%** - High chance of success

---

## Step 2: Template Selection

Select the appropriate base template based on job category:

### Our 13 Templates

1. **lead_generation** - B2B lead generation, prospect lists
2. **data_scraping** - Web scraping, data extraction
3. **research_assistant** - Market research, analysis
4. **webhook_automation** - Zapier, Make, webhooks
5. **cold_outreach** - Email outreach, cold DM
6. **excel_sheets** - Spreadsheets, dashboards, formulas
7. **virtual_assistant** - Admin support, scheduling
8. **notion_setup** - Notion setup, organization
9. **qa_testing** - Quality assurance, testing
10. **email_automation** - Email sequences, Mailchimp
11. **social_media** - Social media management
12. **content_repurposing** - Content transformation
13. **pdf_services** - PDF editing, OCR

### Template Structure

Each template has:
- **Opening** - Personalized to job
- **Approach** - 3 bullets of what you'll do
- **Tools/Methods** - Specific technologies
- **Timeline** - Estimated delivery
- **Pricing** - Based on calculation
- **CTA** - Call to action

---

## Step 3: Enhance with AI

Take the base template and enhance with:

### Personalization
- Reference specific phrases from job description
- Mention specific tools/technologies they need
- Address their stated problem directly

### Pricing Calculation
```
difficulty = estimated_hours_from_job_size

if difficulty <= 0.3: hours = 8
if difficulty <= 0.7: hours = 24  
if difficulty > 0.7: hours = 80

total = hourly_rate × hours
```

### Milestone Structure
- **Small jobs (<20hrs):** 3 milestones (30/50/20)
- **Large jobs (20+hrs):** 4 milestones (20/50/20/10)

---

## Step 4: Generate Final Proposal

### Output Format

```
Hi [Client Name],

[Personalized opening - reference job details]

My approach:
• [Specific approach 1 - tailored to their needs]
• [Specific approach 2 - addresses their pain points]
• [Specific approach 3 - shows understanding]

[Timeline and pricing]

Screening question: [Relevant question about their project]

Best,
[Your name]
```

### Quality Checks
- ✅ 120-220 words
- ✅ No generic filler
- ✅ Specific tools mentioned
- ✅ Clear timeline
- ✅ Milestone structure
- ✅ Strong CTA

---

## Integration with Bot

This skill works with the Upwork bot:
1. Bot scans jobs via RSS
2. Bot calculates match score
3. Bot selects template
4. Skill enhances with AI
5. Bot submits proposal
6. Discord alerts sent

---

## Example Flow

**Job:** "Need someone to scrape product data from 50 e-commerce sites"

**Score:** 82% (high match)
**Template:** data_scraping

**Enhancement:**
- Add specific scraping tools: Python, BeautifulSoup, Scrapy
- Mention rate limiting and politeness
- Add proxy rotation if needed
- Calculate pricing: 40hrs × $25 = $1000
- Add screening question about target sites

**Final Proposal:**
```
Hi there,

I noticed you need to scrape product data from 50 e-commerce sites. 
I've built similar web scraping solutions for e-commerce pricing 
monitoring - extracting product names, prices, and availability.

My approach:
• Build a scalable scraper with Python + BeautifulSoup (handles 50+ sites)
• Implement proxy rotation to avoid blocks and ensure reliability
• Deliver structured CSV/JSON output ready for your analysis

Timeline: 5-7 days for complete dataset
Investment: $1,000 (structured as milestones)

Do you have a preferred format for the output data?

Best,
[Your name]
```
