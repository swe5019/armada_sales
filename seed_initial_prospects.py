"""
One-time loader for the first batch of real, web-researched prospects.

These are genuine companies with verifiable public signals (new distribution
center openings, named supply-chain leadership) found via web search on
2026-06-29 - not fabricated. Run once against a fresh DB:

    python seed_initial_prospects.py

Re-running is safe to skip duplicates is NOT implemented - delete
armada_sales.db first if you want to re-seed from scratch.
"""
from datetime import date
from app import create_app, db
from app.models import Company, Contact, Signal, Industry

app = create_app()
with app.app_context():
    def get_industry(name):
        return Industry.query.filter_by(name=name).first()

    bs = Company(
        name="Border States",
        website="https://www.borderstates.com",
        industry_id=get_industry("Distributors").id,
        city="Fargo", state="ND",
        employee_count="3000+",
        stage="Researching",
        fit_notes=(
            "Opening its largest-ever distribution center (300,000+ sq ft) in the Upper Midwest, "
            "fall 2026, to serve 28 branch locations across ND/SD/MN/IA/WY/WI/MT/NE. New facility "
            "launch is a natural window to bid on inbound/outbound freight and redistribution to "
            "branches before incumbent carrier contracts are locked in."
        ),
        source="Web research",
    )
    db.session.add(bs)
    db.session.flush()
    db.session.add(Contact(
        company_id=bs.id, name="Tony Serati", title="VP Supply Chain Strategy and Optimization",
        notes="Named to this role 2024; owns warehousing/logistics strategy. Email not public - look up via LinkedIn/Apollo.",
    ))
    db.session.add(Contact(
        company_id=bs.id, name="James Sipe", title="Executive VP, Supply Chain",
        notes="Promoted to role April 2022; owns overall supply chain. Email not public - look up via LinkedIn/Apollo.",
    ))
    db.session.add(Signal(
        company_id=bs.id, signal_type="Known contract/renewal date",
        expected_date=date(2026, 9, 1), confidence="Medium",
        source_url="https://solutions.borderstates.com/news/border-states-announces-first-regional-distribution-center/",
        notes="New Upper Midwest DC (Fargo area) slated to open fall 2026 - largest facility in company history.",
    ))

    st = Company(
        name="Supply Technologies",
        website="https://www.supplytechnologies.com",
        industry_id=get_industry("Distributors").id,
        city="Independence", state="OH",
        employee_count="1000+",
        stage="New",
        fit_notes=(
            "Global supplier of assembly components/fasteners to OEMs, operates 70+ warehouses "
            "worldwide. New 375,000 sq ft US distribution center opening July 1, 2026, hiring "
            "starting early 2026 - a clear signal they're standing up new freight/warehousing "
            "relationships right now."
        ),
        source="Web research",
    )
    db.session.add(st)
    db.session.flush()
    db.session.add(Signal(
        company_id=st.id, signal_type="Known contract/renewal date",
        expected_date=date(2026, 7, 1), confidence="Medium",
        source_url="https://www.supplytechnologies.com/resources/blog/new-dayton-distribution-center-to-support-north-american-customers",
        notes="New 375,000 sq ft distribution center opening July 1, 2026 (serves US/Canada/Mexico). No named contact found yet.",
    ))

    ofi = Company(
        name="ofi (Olam Food Ingredients) - East Coast DC",
        website="https://www.ofi.com",
        industry_id=get_industry("Food & Beverage").id,
        city="East Greenwich Township", state="NJ",
        employee_count="ofi global: 10,000+ (new DC site smaller)",
        stage="New",
        fit_notes=(
            "Global food & beverage ingredients supplier. Just opened a new 574,000 sq ft East "
            "Coast distribution center in East Greenwich Township, NJ (ribbon cutting Feb 2026). "
            "New-facility ramp-up is a prime window to bid on outbound redistribution/freight "
            "before they settle into a single incumbent carrier."
        ),
        source="Web research",
    )
    db.session.add(ofi)
    db.session.flush()
    db.session.add(Signal(
        company_id=ofi.id, signal_type="News mention (expansion, complaint, outage)",
        expected_date=date(2026, 8, 1), confidence="Low",
        source_url="https://www.njeda.gov/njeda-welcomes-global-food-beverage-ingredients-and-solutions-company-ofi-to-south-jersey/",
        notes="New 574,000 sq ft East Coast DC opened Feb 2026 in East Greenwich Township, NJ. No named contact found yet.",
    ))

    db.session.commit()
    print(f"Seeded {Company.query.count()} companies, {Contact.query.count()} contacts, {Signal.query.count()} signals")
