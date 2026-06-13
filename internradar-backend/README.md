# InternRadar Backend

InternRadar is an ATS aggregation backend for **India-focused internship discovery**. Instead of maintaining brittle company-by-company scrapers, it integrates with Applicant Tracking Systems and normalised manual portals so one connector covers many companies.

> **Scope**: Only genuine internships located in India are stored and surfaced. Remote-only roles and full-time / contract / senior positions are excluded at the connector and service layers.

## Architecture

```text
Scheduler (APScheduler)
  -> ATS Connector Manager
  -> Greenhouse / Lever / Ashby / Workday / SmartRecruiters / Manual Sources
  -> Two-phase Internship Filter  (keyword inclusion + non-internship exclusion)
  -> India Location Filter        (30+ cities + ISO code + word-boundary regex)
  -> Rule-Based Classification    (18 categories)
  -> Deduplication                (SHA-256 fingerprint, MongoDB unique index)
  -> MongoDB
  -> Notification Engine          (Telegram / Email / Discord / WhatsApp)
```

## Filters Applied at Every Stage

### Internship-only (two phases)
**Phase 1 — must contain**: `intern`, `internship`, `summer intern`, `winter intern`, `trainee`, `apprentice`

**Phase 2 — must NOT contain in title**: `full-time`, `senior`, `staff`, `lead`, `principal`, `director`, `manager`, `contract`, `freelance`, `part-time`, `permanent`, `experienced`

### India-only
Location is matched against 30+ canonical tokens (city names, aliases, ISO `IN`) using word-boundary regex. Non-matching internships are dropped at the connector's `normalize()` step and again as a safety net in `InternshipService.insert_if_new()`.

## Normalised Internship Shape

```json
{
  "external_id": "unique-id",
  "source": "greenhouse",
  "company": "Razorpay",
  "title": "Software Engineering Intern",
  "location": "Bangalore, India",
  "remote": false,
  "employment_type": "Internship",
  "url": "https://example.com/job",
  "description": "...",
  "posted_at": "...",
  "skills": [],
  "tags": [],
  "category": "Software Engineering"
}
```

## Project Structure

```text
app/
  connectors/
    base_connector.py          # INTERNSHIP_KEYWORDS, NON_INTERNSHIP_KEYWORDS,
                               # INDIA_LOCATION_TOKENS, is_internship(), is_india_location()
    greenhouse_connector.py    # 35+ Indian + global companies
    lever_connector.py         # 35+ Indian companies
    ashby_connector.py         # 35+ Indian deep-tech / fintech companies
    workday_connector.py       # 18 Workday career-site endpoints (TCS, Wipro, HCL …)
    smartrecruiters_connector.py  # 20 Indian conglomerates
    manual_source_connector.py    # YAML-driven scraper
  classification/
    internship_classifier.py   # 18 categories, specific-first ordering
  config/
    sources.yaml               # 30+ manual sources: Internshala, IITs, NITs,
                               # BITS, ISRO, DRDO, NIC, CSIR, research labs
  discovery/
  models/
  notifications/
    providers/                 # Telegram, Email, Discord, WhatsApp
  routers/
    internships.py             # + /location/{location}, /source/{source}
  scheduler/
  search/
  services/
    internship_service.py      # India safety-net, by_location(), by_source()
  utils/
tests/                         # 76 tests — 100 % pass
```

## Internship Categories (18)

| Category | Example Titles |
|---|---|
| Machine Learning | ML Intern, Deep Learning Intern, LLM Research Intern |
| Data Science | Data Scientist Intern, Predictive Modelling Intern |
| Data Analytics | Data Analyst Intern, BI Intern, SQL Analytics Intern |
| Cybersecurity | Security Intern, Penetration Testing Intern |
| Embedded & Hardware | Embedded Software Intern, VLSI Design Intern, FPGA Intern |
| Cloud & DevOps | Cloud Intern, DevOps Intern, SRE Intern |
| Mobile Development | Android Intern, Flutter Intern, iOS Intern |
| UI/UX | UI/UX Design Intern, Product Design Intern |
| Research | Research Intern, AI Research Intern |
| Software Engineering | Software Engineering Intern, Backend Intern |
| Product | Product Management Intern, Growth Intern |
| Business Analytics | Business Analyst Intern, Strategy Intern |
| Finance | Finance Intern, Investment Banking Intern |
| Marketing | Digital Marketing Intern, SEO Intern |
| Operations | Operations Intern, Supply Chain Intern |
| Human Resources | HR Intern, Talent Acquisition Intern |
| Legal & Compliance | Legal Intern, Compliance Intern |
| Content & Writing | Content Writing Intern, Technical Writing Intern |

## Installation

```powershell
cd "C:\Users\Lakshya Arora\Documents\InternRadar\internradar-backend"
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Environment Variables

Copy the example file:

```powershell
copy .env.example .env
```

Required:

```env
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
DB_NAME=internradar
```

Optional (notification channels — unconfigured providers skip safely):

```env
BOT_TOKEN=
CHAT_ID=
SCRAPER_INTERVAL_MINUTES=30
SMTP_HOST=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
EMAIL_FROM=
EMAIL_TO=
DISCORD_WEBHOOK_URL=
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_WHATSAPP_FROM=
TWILIO_WHATSAPP_TO=
```

## Running The API

```powershell
python -m uvicorn app.main:app --reload
```

Open:

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/internships/latest`

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Service liveness check |
| GET | `/companies` | List active companies |
| GET | `/companies/{id}` | Get company by id |
| GET | `/internships` | Paginated internships (`page`, `page_size`) |
| GET | `/internships/latest` | Latest internships (`limit`) |
| GET | `/internships/search` | Filter by `title`, `company`, `location`, `category`, `source`, `remote`, `posted_after` |
| GET | `/internships/category/{category}` | By category (see 18 categories above) |
| GET | `/internships/location/{location}` | By Indian city/region, e.g. `Bangalore`, `NCR` |
| GET | `/internships/source/{source}` | By ATS source: `greenhouse`, `lever`, `ashby`, `workday`, `smartrecruiters`, `manual` |
| GET | `/internships/company/{company}` | By company name (case-insensitive) |
| GET | `/internships/remote` | Remote internships (returns empty — remote excluded by policy) |

## Adding A New ATS Connector

1. Create `app/connectors/new_provider_connector.py`.
2. Subclass `BaseConnector`.
3. Implement `discover_companies`, `fetch_jobs`, and `normalize`.
4. Inside `normalize`, call `self.is_internship(title, description)` and `self.is_india_location(location)` before `self.build_internship(...)`.
5. Add the connector to `InternshipScheduler.connectors`.

## Adding Indian Companies to Existing Connectors

Each connector file has a top-level list constant (`GREENHOUSE_BOARD_TOKENS`, `LEVER_COMPANY_SLUGS`, etc.). Add the company's ATS slug/token to the relevant list — no other changes needed.

## Adding Manual Sources

Edit `app/config/sources.yaml`:

```yaml
sources:
  - name: IIIT Hyderabad
    type: iit_portal
    url: https://www.iiit.ac.in/
    selector: a
    location: Hyderabad, India
    refresh_interval: 60
```

Every source **must** include a `location` field that resolves to an Indian city. Sources without a valid India location are silently skipped.

## Deduplication

InternRadar generates a SHA-256 fingerprint from:

```text
company | title | location | source
```

MongoDB enforces uniqueness on `fingerprint`, so duplicate notification sends are avoided.

## Tests

```powershell
python -m pytest
```

76 tests covering: internship keyword detection, non-internship exclusion, India location matching (30+ cases), all 18 classifier categories, category priority ordering, deduplication, India safety net at service layer, scheduler India/non-India filtering, search filter construction, notification provider no-ops, and API health.
