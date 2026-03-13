# Excel / Google Sheets Template

## Category Keywords
- excel
- google sheets
- spreadsheet
- dashboard
- formulas
- vba
- apps script
- data model
- workbook
- sheet automation
- spreadsheet template
- financial model
- budget tracker
- project tracker

---

## SHORT VERSION (For Upwork Proposal - ~150 words)

Hi,

I build enterprise-grade spreadsheets and dashboards that turn messy data into reliable decision systems.

Based on your posting, I can create [CUSTOMIZE: financial model/dashboard/tracker] in [CUSTOMIZE: Excel/Google Sheets] with [CUSTOMIZE: automation/integration].

**My approach:**
1. Define requirements, data sources, and KPIs
2. Build clean data architecture (raw → cleaned → calculated → presentation)
3. Implement advanced formulas (XLOOKUP, LAMBDA, QUERY)
4. Add automation via Apps Script/VBA
5. Create visual dashboards with charts and conditional formatting
6. Document everything with handoff guides

**Why me:**
- [CUSTOMIZE: expertise, e.g., "5+ years building enterprise spreadsheets"]
- [CUSTOMIZE: features, e.g., "include error handling, testing, version control"]
- [CUSTOMIZE: support, e.g., "30-day support included"]

I deliver a pilot sheet within 2-3 days so you can verify before full build.

Quick question: What's the main business question this spreadsheet needs to answer?

Best,
[Your Name]

---

## LONG VERSION (For After Hired)

### Service Tiers

**Pilot / Audit** - $30-60/hr equivalent
- Single sheet or prototype
- Audit report with recommendations
- Sample automation demo
- Turnaround: 2-3 days

**Standard Build**
- Multi-sheet workbook
- Data imports and validation
- Formulas and calculations
- Basic dashboard
- Documentation
- Turnaround: 5-10 days

**Enterprise System**
- Modular workbook architecture
- Role-based access sheets
- BI-ready data extracts
- Advanced automation
- Real-time data connections
- Monitoring and SLAs
- Training and handoff
- Turnaround: 14-30 days

### Deliverables

**Core:**
- Clean workbook (Excel .xlsx or Google Sheets)
- Named ranges throughout
- Version history enabled
- Data ingestion layer (imports, APIs)
- Normalized data tables
- Calculation layer (transparent formulas)
- Dashboard with charts and pivot tables
- Exports (CSV, JSON, PDF)

**Advanced:**
- Automation scripts (Apps Script / VBA / Python)
- Integration with other tools
- Unit tests and validation sheets
- Error handling and IFERROR wrappers
- Real-time data connections

**Documentation:**
- Field map and data dictionary
- Change log
- How-to guide
- Rollback steps
- Video walkthrough

### Use Cases

**Finance:**
- P&L models
- Cash flow forecasts
- Budget tracking
- Scenario analysis
- Investment models
- Commission calculations

**Operations:**
- Project management
- Resource allocation
- Inventory tracking
- Supply chain monitors
- Workflow automation

**Sales:**
- CRM dashboards
- Quota tracking
- Territory assignment
- Pipeline management
- Commission calculators

**Marketing:**
- Budget pacing
- Attribution modeling
- Campaign tracking
- ROI dashboards
- Lead scoring

**Analytics:**
- KPI dashboards
- Data visualization
- Executive summaries
- Automated reporting

### Process / Milestones

1. **Intake** - Define owners, outputs, update frequency, success metrics
2. **Data Plumbing** - Connect sources, APIs, sample data ingest
3. **Schema Design** - Normalize tables, define keys and relationships
4. **Formula Build** - Create calculations with transparency (no hidden cells)
5. **Automation** - Script triggers, scheduled imports, error handling
6. **Dashboard** - Visual summaries, filters, conditional formatting
7. **Testing** - Edge cases, large data stress tests, formula audit
8. **Security** - Protected ranges, access controls, PII masking
9. **Handoff** - Documentation, training session, walkthrough

### Architecture Patterns

**Sheet Structure:**
- Raw Data → Cleaned → Calculated → Presentation
- Separation of concerns (no mixing layers)

**Formula Best Practices:**
- Named ranges (no hardcoded cells)
- Structured references
- INDEX/MATCH over VLOOKUP
- XLOOKUP for complex lookups
- LAMBDA for custom functions
- QUERY for SQL-like filtering
- FILTER and SORT for dynamic ranges
- REGEXMATCH and REGEXEXTRACT for text

**Performance:**
- Avoid volatile functions where possible
- Use helper columns for complex calcs
- Query function over array formulas for large data
- Import ranges efficiently (IMPORTRANGE caching)
- Chunked updates for 100k+ rows

### Integrations & Platforms

**Primary:**
- Google Sheets (Apps Script)
- Microsoft Excel (VBA, Power Query)

**Data:**
- Airtable
- BigQuery
- PostgreSQL
- REST APIs

**Automation:**
- Zapier
- Make (Integromat)
- Google Apps Script
- Python scripts

**BI:**
- Looker Studio
- Power BI
- Tableau

### Automation & Reliability

**Scheduled Automation:**
- Time-driven triggers
- On-edit triggers
- Import automation
- Export automation

**Error Handling:**
- IFERROR wrappers
- Data validation rules
- Acceptance thresholds (row counts, null rates)
- Alerting (email/Slack) for schema drift
- Transaction logs
- Rollback capability

**Testing:**
- Formula auditing
- Unit test sheets
- Sample data reconciliation
- Stress tests (5x volume)
- User acceptance checklist

### Security & Compliance

**Access Control:**
- Principle of least privilege
- Protected ranges
- Sheet-level permissions
- Service account controls

**Data Protection:**
- OAuth for connectors
- Encrypted tokens
- PII masking in samples
- Retention policies

**Enterprise:**
- NDA support
- SOC/ISO alignment notes
- Audit trail
- Version control

### Advanced Formulas (Expert Level)

**Lookup Functions:**
- XLOOKUP (modern replacement for VLOOKUP)
- INDEX/MATCH combinations
- FILTER + SORT
- QUERY (SQL-like in Sheets)

**Text Processing:**
- REGEXMATCH, REGEXEXTRACT, REGEXREPLACE
- TEXTJOIN, CONCATENATE
- SPLIT

**Array Formulas:**
- ARRAYFORMULA
- LAMBDA (custom functions)
- MAP, REDUCE, SCAN

**Time & Date:**
- NETWORKDAYS, WORKDAY
- TIMEDURATION
- EOMONTH, EDATE

**Financial:**
- NPV, IRR, PMT
- XNPV, XIRR

### Scripting & Development

**Google Apps Script:**
- Custom functions
- Triggers (time-driven, on-edit)
- Web apps
- API integrations
- MailApp for alerts

**VBA Macros:**
- Automated reports
- User forms
- Data processing
- Template generation

**Python + Sheets API:**
- Bulk data operations
- Advanced analytics
- ML model integration

### Collaboration Features

- Comment threads and mentions
- Approval workflows (using CHECKBOX + conditional formatting)
- Protected ranges with exceptions
- Version history and named versions
- Suggesting mode
- Email notifications for changes

### Version Control

**For Spreadsheets:**
- Named versions (Sheets native)
- Date-stamped backup copies
- Change log sheet
- Git integration (sheets-git for enterprise)

**Best Practices:**
- Commit before major changes
- Branch for experimental features
- Merge via copy-paste values
- Document all changes in log

### Performance & Scale

**Handling Large Data:**
- QUERY function over array formulas
- IMPORTRANGE optimization (cache results)
- Separate calculation sheets
- Aggregate tables for dashboards

**Optimization Tips:**
- Minimize volatile functions (NOW, TODAY, RAND)
- Use helper columns strategically
- Pre-calculate aggregations
- Cache API results

### QA Checklist

- [ ] Formula audit (no #REF!, #N/A unless intended)
- [ ] Named ranges intact after changes
- [ ] Sample reconciliation vs source
- [ ] Stress test with 5x data volume
- [ ] Error handling on all API calls
- [ ] Protected ranges for key formulas
- [ ] Documentation complete
- [ ] Client sign-off

### Documentation & Training

**Deliver:**
- One-page system diagram
- Field map / data dictionary
- Operations guide (refresh, backup, rollback)
- Annotated workbook comments
- Video walkthrough (20-30 min)
- Live handover session (30-60 min)

### Pricing Models

**Fixed Project:**
- $200-500 (pilot/audit)
- $500-2000 (standard build)
- $2000-10000 (enterprise system)

**Hourly:**
- $30-75/hour based on complexity

**Retainer:**
- $200-1000/month for updates and monitoring

**Add-Ons:**
- BI dashboard exports (+$300-800)
- Advanced automation (+$200-500)
- Custom scripts (+$300-1000)
- Training session (+$100-200)
- Priority support (+50%)

### Why Choose Me (Differentiation)

1. **Enterprise Architecture** - Modular, scalable structure, not just formulas
2. **Formula Expertise** - XLOOKUP, LAMBDA, QUERY - modern, efficient approaches
3. **Testing & Validation** - Every build includes error handling and QA
4. **Documentation** - Complete handoff, not just "here's the file"
5. **Support** - 30-day guarantee on all builds

### Turnaround Times

| Tier | Turnaround | Best For |
|------|------------|----------|
| Pilot | 2-3 days | Testing, audits |
| Standard | 5-10 days | Most projects |
| Enterprise | 14-30 days | Complex systems |

### Onboarding Questions

- What business question needs answering?
- What data sources are involved?
- Update frequency (real-time/daily/weekly)?
- Who will use this (technical/non-technical)?
- Any compliance requirements?
- Current spreadsheet challenges?
- Deadline?
- Budget range?

### Value-Adds

- Free pilot sheet (10 rows)
- 30-day bug fixes
- 48-hour revision turnaround
- One-click refresh script
- Monitoring dashboard
- Money-back guarantee if pilot fails

### FAQ

**Q: Can you work with our existing messy spreadsheet?**
A: Yes - I often start with cleanup and audit. I'll identify issues and either fix or rebuild based on complexity.

**Q: How do you handle large datasets (50k+ rows)?**
A: I use QUERY functions, separate calculation layers, and caching strategies to maintain performance. For very large data, I recommend BigQuery or Airtable backend.

**Q: Can you add real-time data?**
A: Yes - Google Sheets can connect to APIs, =GOOGLEFINANCE, IMPORTRANGE, or webhooks for live data.

**Q: What about version control?**
A: I enable native version history, create date-stamped backups, and maintain a change log sheet for audit trails.

**Q: Do you offer training?**
A: Yes - every build includes a 30-60 minute walkthrough and written documentation.

### Upwork Optimization Tips

- Attach sanitized sample (5-10 rows)
- Show before/after screenshots
- Include video demo (30-60 sec)
- Highlight enterprise features
- Offer pilot at low price
- Fast response time
- Keywords: financial model, dashboard, automation, Google Apps Script, VBA
