# Armada Sales — Cold Outreach & Pipeline Tracker

A small Flask app to track prospects, contacts, competitor-contract signals,
and cold email outreach for Armada Supply Chain Solutions (freight,
warehousing, redistribution) targeting manufacturers, retailers, food &
beverage, distributors, importers, and consumer products companies.

## What this does

- **Pipeline tracking**: companies move through stages (New → Researching →
  Contacted → Engaged → Replied → Warm Lead → Meeting Set → Customer / Lost).
- **Contacts** per company with email/phone/LinkedIn.
- **Competitor signals**: log evidence that a company's relationship with a
  competitor (C.H. Robinson, XPO, J.B. Hunt, Ryder, DHL Supply Chain, GXO,
  Lineage, Americold, NFI, Kenco, etc. — pre-seeded, editable) may be up for
  review: a known renewal date, an RFP/bid posting, a leadership change, a
  hiring spike for logistics/warehouse roles, or a news mention. The
  dashboard surfaces anything due in the next 90 days.
- **Email templates** with merge fields (`{{first_name}}`, `{{company_name}}`,
  `{{industry}}`, `{{competitor_name}}`) and a per-contact composer that logs
  status (Draft/Sent/Opened/Replied/Bounced) and next follow-up date.
- **CSV import** for lead lists you already have or source elsewhere.
- **Apollo.io search** (optional) to pull real companies by industry keyword
  directly into your pipeline.
- **SMTP send** (optional) to send straight from the app via a Gmail app
  password, or just mark emails sent if you send manually from your own inbox.

## Why there's no built-in "list of leads"

There is no public database of private commercial contract expiration dates
between companies and their freight/warehousing providers — that information
isn't published anywhere I can query for you. Real prospecting in this space
comes from a few legitimate channels:

- **Apollo.io / similar B2B databases** — real companies + verified contacts,
  filterable by industry and size. Wired up via `APOLLO_API_KEY`.
- **Your own lists** — trade show contacts, LinkedIn Sales Navigator exports,
  referrals — import via CSV (`sample_leads.csv` shows the expected columns).
- **Public signals you log yourself** — RFP/bid boards, local business news,
  LinkedIn "open to work"/hiring posts for logistics roles, leadership
  changes, press releases about expansions. The Signals feature exists to
  capture these as you find them, with a date + confidence + source link.

## Deploying to a real URL (Render.com, free tier)

1. Push this repo to GitHub (already done if you're reading this from the repo).
2. Go to https://render.com, sign up/log in, click **New > Blueprint**, and
   connect this GitHub repo. Render will detect `render.yaml` and configure
   the service automatically.
3. On the env var setup screen, fill in `APOLLO_API_KEY` / `SMTP_USERNAME` /
   `SMTP_PASSWORD` if you have them (all optional — leave blank to skip).
4. Click **Apply**. After the build finishes you'll get a URL like
   `https://armada-sales.onrender.com` you can open from any device.

**Two things to know about the free tier:**
- The service spins down after ~15 min idle and takes ~30-60s to wake up on
  the next visit — fine for solo use, just expect a short delay sometimes.
- The free tier's disk is **not persistent across deploys** — your SQLite
  database (companies/contacts/signals) can reset when you push a new commit
  or redeploy. For a few dozen leads that's a minor annoyance (just re-run
  `seed_initial_prospects.py`); if that becomes a problem, upgrade to a paid
  Render plan with a persistent disk (~$7/mo) or swap SQLite for Render's
  free Postgres add-on — ask me and I'll wire it up.

## Starter prospects (already loaded)

`seed_initial_prospects.py` loads 3 real, web-researched companies with
verified public signals as a starting pipeline:

- **Border States** (Fargo, ND) — opening its largest-ever distribution
  center (300,000+ sq ft) fall 2026; named contacts Tony Serati (VP Supply
  Chain Strategy) and James Sipe (EVP Supply Chain).
- **Supply Technologies** (Independence, OH) — new 375,000 sq ft US
  distribution center opening July 2026.
- **ofi / Olam Food Ingredients** — new 574,000 sq ft East Coast DC opened
  Feb 2026 in East Greenwich Township, NJ.

Contact emails for the latter two aren't public — use Apollo.io or LinkedIn
to find the right person once you've confirmed the company is worth pursuing.
Run it after first `python run.py` creates the database:

```bash
python seed_initial_prospects.py
```

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in keys you have; all are optional except SECRET_KEY
python run.py
```

Visit http://127.0.0.1:5000

The first run creates `armada_sales.db` (SQLite) and seeds industries,
known competitors, and starter email templates.

### Optional: Apollo.io prospect search

Get a free-tier key at apollo.io, set `APOLLO_API_KEY` in `.env`, then use
"Find Prospects" in the nav to search by industry keyword and add real
companies straight into your pipeline.

### Optional: send email from the app

Generate a Gmail "app password" at
https://myaccount.google.com/apppasswords, set `SMTP_USERNAME` and
`SMTP_PASSWORD` in `.env`. Otherwise, draft in the app and send manually from
your own inbox, then click "mark as sent" to keep tracking accurate.

## Project layout

```
app/
  models.py        Company, Contact, Signal, Outreach, EmailTemplate, Industry, Competitor
  routes.py         All views
  integrations.py   Apollo.io search + SMTP send (both optional/pluggable)
  seed.py           Seeds industries, competitors, starter templates
  templates/        Jinja HTML
run.py              Entrypoint
sample_leads.csv    CSV import template
```
