import csv
import io
from datetime import datetime, timedelta

from flask import Blueprint, render_template, request, redirect, url_for, flash

from . import db
from .models import (
    Company, Contact, Industry, Competitor, Signal, Outreach, EmailTemplate,
    PIPELINE_STAGES, SIGNAL_TYPES,
)
from . import integrations

bp = Blueprint("main", __name__)


# ---------- Dashboard ----------

@bp.route("/")
def dashboard():
    stage_counts = {
        stage: Company.query.filter_by(stage=stage).count() for stage in PIPELINE_STAGES
    }
    horizon = datetime.utcnow().date() + timedelta(days=90)
    upcoming_signals = (
        Signal.query.filter(Signal.expected_date.isnot(None), Signal.expected_date <= horizon)
        .order_by(Signal.expected_date.asc())
        .all()
    )
    recent_outreach = Outreach.query.order_by(Outreach.created_at.desc()).limit(15).all()
    return render_template(
        "dashboard.html",
        stage_counts=stage_counts,
        stages=PIPELINE_STAGES,
        upcoming_signals=upcoming_signals,
        recent_outreach=recent_outreach,
    )


# ---------- Companies ----------

@bp.route("/companies")
def companies_list():
    q = Company.query
    industry_id = request.args.get("industry_id")
    stage = request.args.get("stage")
    if industry_id:
        q = q.filter_by(industry_id=industry_id)
    if stage:
        q = q.filter_by(stage=stage)
    companies = q.order_by(Company.created_at.desc()).all()
    return render_template(
        "companies_list.html",
        companies=companies,
        industries=Industry.query.all(),
        stages=PIPELINE_STAGES,
        selected_industry=industry_id,
        selected_stage=stage,
    )


@bp.route("/companies/new", methods=["GET", "POST"])
def company_new():
    if request.method == "POST":
        company = Company(
            name=request.form["name"],
            website=request.form.get("website"),
            industry_id=request.form.get("industry_id") or None,
            city=request.form.get("city"),
            state=request.form.get("state"),
            employee_count=request.form.get("employee_count"),
            current_provider_id=request.form.get("current_provider_id") or None,
            fit_notes=request.form.get("fit_notes"),
            source="Manual",
        )
        db.session.add(company)
        db.session.commit()
        flash(f"Added {company.name}", "success")
        return redirect(url_for("main.company_detail", company_id=company.id))
    return render_template(
        "company_form.html", industries=Industry.query.all(), competitors=Competitor.query.all(), company=None
    )


@bp.route("/companies/<int:company_id>")
def company_detail(company_id):
    company = Company.query.get_or_404(company_id)
    templates = EmailTemplate.query.all()
    return render_template(
        "company_detail.html",
        company=company,
        stages=PIPELINE_STAGES,
        signal_types=SIGNAL_TYPES,
        competitors=Competitor.query.all(),
        templates=templates,
    )


@bp.route("/companies/<int:company_id>/stage", methods=["POST"])
def company_update_stage(company_id):
    company = Company.query.get_or_404(company_id)
    company.stage = request.form["stage"]
    db.session.commit()
    return redirect(url_for("main.company_detail", company_id=company.id))


@bp.route("/companies/import", methods=["GET", "POST"])
def companies_import():
    if request.method == "POST":
        file = request.files.get("csv_file")
        if not file:
            flash("No file selected", "error")
            return redirect(url_for("main.companies_import"))

        stream = io.StringIO(file.stream.read().decode("utf-8-sig"))
        reader = csv.DictReader(stream)
        created = 0
        for row in reader:
            industry = None
            if row.get("industry"):
                industry = Industry.query.filter(Industry.name.ilike(row["industry"].strip())).first()
            company = Company(
                name=row.get("company_name", "").strip(),
                website=row.get("website", "").strip() or None,
                industry_id=industry.id if industry else None,
                city=row.get("city", "").strip() or None,
                state=row.get("state", "").strip() or None,
                employee_count=row.get("employee_count", "").strip() or None,
                fit_notes=row.get("notes", "").strip() or None,
                source="CSV import",
            )
            if not company.name:
                continue
            db.session.add(company)
            db.session.flush()

            if row.get("contact_name"):
                db.session.add(
                    Contact(
                        company_id=company.id,
                        name=row.get("contact_name", "").strip(),
                        title=row.get("contact_title", "").strip() or None,
                        email=row.get("contact_email", "").strip() or None,
                        phone=row.get("contact_phone", "").strip() or None,
                        linkedin_url=row.get("contact_linkedin", "").strip() or None,
                    )
                )
            created += 1
        db.session.commit()
        flash(f"Imported {created} companies", "success")
        return redirect(url_for("main.companies_list"))
    return render_template("companies_import.html")


# ---------- Contacts ----------

@bp.route("/companies/<int:company_id>/contacts/new", methods=["POST"])
def contact_new(company_id):
    company = Company.query.get_or_404(company_id)
    db.session.add(
        Contact(
            company_id=company.id,
            name=request.form["name"],
            title=request.form.get("title"),
            email=request.form.get("email"),
            phone=request.form.get("phone"),
            linkedin_url=request.form.get("linkedin_url"),
            notes=request.form.get("notes"),
        )
    )
    db.session.commit()
    return redirect(url_for("main.company_detail", company_id=company.id))


@bp.route("/contacts/<int:contact_id>/delete", methods=["POST"])
def contact_delete(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    company_id = contact.company_id
    db.session.delete(contact)
    db.session.commit()
    return redirect(url_for("main.company_detail", company_id=company_id))


# ---------- Signals (competitor contract / renewal intel) ----------

@bp.route("/companies/<int:company_id>/signals/new", methods=["POST"])
def signal_new(company_id):
    company = Company.query.get_or_404(company_id)
    expected_date = request.form.get("expected_date") or None
    db.session.add(
        Signal(
            company_id=company.id,
            competitor_id=request.form.get("competitor_id") or None,
            signal_type=request.form.get("signal_type"),
            expected_date=datetime.strptime(expected_date, "%Y-%m-%d").date() if expected_date else None,
            confidence=request.form.get("confidence", "Medium"),
            source_url=request.form.get("source_url"),
            notes=request.form.get("notes"),
        )
    )
    db.session.commit()
    return redirect(url_for("main.company_detail", company_id=company.id))


@bp.route("/signals/<int:signal_id>/delete", methods=["POST"])
def signal_delete(signal_id):
    signal = Signal.query.get_or_404(signal_id)
    company_id = signal.company_id
    db.session.delete(signal)
    db.session.commit()
    return redirect(url_for("main.company_detail", company_id=company_id))


# ---------- Prospect search (Apollo enrichment) ----------

@bp.route("/prospects/search", methods=["GET", "POST"])
def prospects_search():
    results = None
    error = None
    if request.method == "POST":
        try:
            results = integrations.apollo_search_companies(
                keywords=request.form.get("keywords", ""),
                locations=request.form.get("locations") or None,
            )
        except integrations.ApolloNotConfigured as e:
            error = str(e)
        except Exception as e:  # surface API errors instead of 500ing
            error = f"Apollo search failed: {e}"
    return render_template("prospects_search.html", results=results, error=error)


@bp.route("/prospects/add", methods=["POST"])
def prospects_add():
    company = Company(
        name=request.form["name"],
        website=request.form.get("website"),
        city=request.form.get("city"),
        state=request.form.get("state"),
        employee_count=request.form.get("employee_count"),
        source="Apollo",
    )
    db.session.add(company)
    db.session.commit()
    flash(f"Added {company.name} from Apollo search", "success")
    return redirect(url_for("main.company_detail", company_id=company.id))


# ---------- Outreach (email composer + tracking) ----------

def render_merge_fields(text, company, contact):
    first_name = contact.name.split(" ")[0] if contact.name else ""
    competitor_name = company.current_provider.name if company.current_provider else "your current provider"
    return (
        text.replace("{{first_name}}", first_name)
        .replace("{{company_name}}", company.name or "")
        .replace("{{industry}}", company.industry.name if company.industry else "your industry")
        .replace("{{competitor_name}}", competitor_name)
        .replace("{{your_name}}", "")
    )


@bp.route("/outreach/new", methods=["POST"])
def outreach_new():
    contact_id = request.form["contact_id"]
    contact = Contact.query.get_or_404(contact_id)
    template_id = request.form.get("template_id")
    subject, body = "", ""
    if template_id:
        template = EmailTemplate.query.get(template_id)
        subject = render_merge_fields(template.subject, contact.company, contact)
        body = render_merge_fields(template.body, contact.company, contact)
    outreach = Outreach(
        company_id=contact.company_id,
        contact_id=contact.id,
        subject=subject,
        body=body,
        status="Draft",
    )
    db.session.add(outreach)
    db.session.commit()
    return redirect(url_for("main.outreach_detail", outreach_id=outreach.id))


@bp.route("/outreach/<int:outreach_id>")
def outreach_detail(outreach_id):
    outreach = Outreach.query.get_or_404(outreach_id)
    return render_template("outreach_detail.html", outreach=outreach)


@bp.route("/outreach/<int:outreach_id>/edit", methods=["POST"])
def outreach_edit(outreach_id):
    outreach = Outreach.query.get_or_404(outreach_id)
    outreach.subject = request.form.get("subject")
    outreach.body = request.form.get("body")
    db.session.commit()
    return redirect(url_for("main.outreach_detail", outreach_id=outreach.id))


@bp.route("/outreach/<int:outreach_id>/send", methods=["POST"])
def outreach_send(outreach_id):
    outreach = Outreach.query.get_or_404(outreach_id)
    if not outreach.contact.email:
        flash("Contact has no email address on file", "error")
        return redirect(url_for("main.outreach_detail", outreach_id=outreach.id))
    try:
        integrations.send_email(outreach.contact.email, outreach.subject, outreach.body)
        outreach.status = "Sent"
        outreach.sent_at = datetime.utcnow()
        if outreach.company.stage in ("New", "Researching"):
            outreach.company.stage = "Contacted"
        db.session.commit()
        flash("Email sent", "success")
    except integrations.SmtpNotConfigured as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"Send failed: {e}", "error")
    return redirect(url_for("main.outreach_detail", outreach_id=outreach.id))


@bp.route("/outreach/<int:outreach_id>/mark-sent", methods=["POST"])
def outreach_mark_sent(outreach_id):
    """Use this if you send manually from your own email client instead of via SMTP."""
    outreach = Outreach.query.get_or_404(outreach_id)
    outreach.status = "Sent"
    outreach.sent_at = datetime.utcnow()
    if outreach.company.stage in ("New", "Researching"):
        outreach.company.stage = "Contacted"
    db.session.commit()
    return redirect(url_for("main.outreach_detail", outreach_id=outreach.id))


@bp.route("/outreach/<int:outreach_id>/status", methods=["POST"])
def outreach_update_status(outreach_id):
    outreach = Outreach.query.get_or_404(outreach_id)
    outreach.status = request.form["status"]
    follow_up = request.form.get("next_follow_up")
    outreach.next_follow_up = datetime.strptime(follow_up, "%Y-%m-%d").date() if follow_up else None
    if outreach.status == "Replied" and outreach.company.stage in ("Contacted", "Engaged"):
        outreach.company.stage = "Replied"
    db.session.commit()
    return redirect(url_for("main.outreach_detail", outreach_id=outreach.id))


# ---------- Email templates ----------

@bp.route("/templates")
def templates_list():
    return render_template("templates_list.html", templates=EmailTemplate.query.all())


@bp.route("/templates/new", methods=["POST"])
def template_new():
    db.session.add(
        EmailTemplate(
            name=request.form["name"],
            subject=request.form["subject"],
            body=request.form["body"],
        )
    )
    db.session.commit()
    return redirect(url_for("main.templates_list"))


@bp.route("/templates/<int:template_id>/delete", methods=["POST"])
def template_delete(template_id):
    template = EmailTemplate.query.get_or_404(template_id)
    db.session.delete(template)
    db.session.commit()
    return redirect(url_for("main.templates_list"))
