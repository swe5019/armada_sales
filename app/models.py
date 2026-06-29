from datetime import datetime
from . import db

PIPELINE_STAGES = [
    "New",
    "Researching",
    "Contacted",
    "Engaged",
    "Replied",
    "Warm Lead",
    "Meeting Set",
    "Customer",
    "Lost",
]

SIGNAL_TYPES = [
    "Known contract/renewal date",
    "RFP or bid announcement",
    "Logistics/supply-chain leadership change",
    "Hiring logistics/warehouse roles",
    "News mention (expansion, complaint, outage)",
    "Other",
]


class Industry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    companies = db.relationship("Company", backref="industry", lazy=True)


class Competitor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    notes = db.Column(db.Text)


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    website = db.Column(db.String(300))
    industry_id = db.Column(db.Integer, db.ForeignKey("industry.id"))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    employee_count = db.Column(db.String(50))
    current_provider_id = db.Column(db.Integer, db.ForeignKey("competitor.id"))
    stage = db.Column(db.String(50), default="New")
    fit_notes = db.Column(db.Text)
    source = db.Column(db.String(120))  # e.g. "Apollo", "CSV import", "Manual"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    current_provider = db.relationship("Competitor")
    contacts = db.relationship("Contact", backref="company", cascade="all, delete-orphan", lazy=True)
    signals = db.relationship("Signal", backref="company", cascade="all, delete-orphan", lazy=True)
    outreach = db.relationship("Outreach", backref="company", cascade="all, delete-orphan", lazy=True)


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    title = db.Column(db.String(150))
    email = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    linkedin_url = db.Column(db.String(300))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    outreach = db.relationship("Outreach", backref="contact", cascade="all, delete-orphan", lazy=True)


class Signal(db.Model):
    """Evidence that a competitor relationship may be ending/up for review."""
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)
    competitor_id = db.Column(db.Integer, db.ForeignKey("competitor.id"))
    signal_type = db.Column(db.String(100))
    expected_date = db.Column(db.Date)  # known/estimated renewal or expiration date
    confidence = db.Column(db.String(20), default="Medium")  # Low/Medium/High
    source_url = db.Column(db.String(500))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    competitor = db.relationship("Competitor")


class EmailTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    subject = db.Column(db.String(300), nullable=False)
    body = db.Column(db.Text, nullable=False)


class Outreach(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey("contact.id"), nullable=False)
    subject = db.Column(db.String(300))
    body = db.Column(db.Text)
    status = db.Column(db.String(30), default="Draft")  # Draft/Sent/Opened/Replied/Bounced
    sent_at = db.Column(db.DateTime)
    next_follow_up = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
