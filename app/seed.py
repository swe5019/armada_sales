from . import db
from .models import Industry, Competitor, EmailTemplate

INDUSTRIES = [
    "Manufacturers",
    "Retailers",
    "Food & Beverage",
    "Distributors",
    "Importers",
    "Consumer Products",
]

# Well-known public 3PL / freight / warehousing providers Armada commonly displaces or competes with.
COMPETITORS = [
    ("C.H. Robinson", "Freight brokerage / 3PL"),
    ("XPO Logistics", "LTL freight / brokerage"),
    ("J.B. Hunt", "Truckload / intermodal / dedicated"),
    ("Ryder Supply Chain Solutions", "Dedicated transportation & warehousing"),
    ("DHL Supply Chain", "Contract logistics / warehousing"),
    ("GXO Logistics", "Contract logistics / warehousing"),
    ("Lineage Logistics", "Cold storage / warehousing"),
    ("Americold", "Cold storage / warehousing"),
    ("NFI Industries", "Dedicated transportation / warehousing"),
    ("Kenco Logistics", "Warehousing / 3PL"),
    ("Saddle Creek Logistics Services", "3PL / fulfillment"),
    ("ODW Logistics", "Warehousing / fulfillment"),
    ("Werner Enterprises", "Truckload / logistics"),
    ("Schneider Logistics", "Truckload / brokerage / intermodal"),
]

DEFAULT_TEMPLATES = [
    {
        "name": "Cold Intro - Freight/Warehousing Fit",
        "subject": "Quick question about {{company_name}}'s freight & warehousing setup",
        "body": (
            "Hi {{first_name}},\n\n"
            "I work with {{industry}} companies like {{company_name}} on freight, warehousing, "
            "and redistribution — usually stepping in when teams are re-evaluating their current "
            "3PL setup or scaling into new regions.\n\n"
            "Is now a relevant time to compare notes on how you're currently handling freight and "
            "storage? Happy to share what's worked for similar {{industry}} companies, no pressure "
            "either way.\n\n"
            "Worth a quick 15-minute call?\n\n"
            "Best,\n{{your_name}}"
        ),
    },
    {
        "name": "Follow-up #1",
        "subject": "Re: {{company_name}} + freight/warehousing",
        "body": (
            "Hi {{first_name}},\n\n"
            "Following up on my note below — totally understand if the timing isn't right. "
            "If freight, storage, or redistribution costs are on your radar this quarter, I'd love "
            "15 minutes to see if there's a fit.\n\n"
            "Best,\n{{your_name}}"
        ),
    },
    {
        "name": "Renewal-window outreach",
        "subject": "Thinking ahead about your {{competitor_name}} contract",
        "body": (
            "Hi {{first_name}},\n\n"
            "Saw some signals suggesting {{company_name}} may be reviewing your logistics/warehousing "
            "setup soon. If a renewal or RFP is coming up, it might be worth benchmarking against "
            "Armada's freight, warehousing, and redistribution solutions before you sign anything.\n\n"
            "Open to a short call in the next couple weeks?\n\n"
            "Best,\n{{your_name}}"
        ),
    },
]


def seed_reference_data():
    if Industry.query.count() == 0:
        for name in INDUSTRIES:
            db.session.add(Industry(name=name))

    if Competitor.query.count() == 0:
        for name, notes in COMPETITORS:
            db.session.add(Competitor(name=name, notes=notes))

    if EmailTemplate.query.count() == 0:
        for t in DEFAULT_TEMPLATES:
            db.session.add(EmailTemplate(**t))

    db.session.commit()
