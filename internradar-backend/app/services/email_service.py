"""Email notification service."""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from app.config import Settings

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).parent.parent / "email_templates"


def _render(template_name: str, context: dict) -> str:
    path = TEMPLATES_DIR / template_name
    if not path.exists():
        return ""
    html = path.read_text()
    for key, value in context.items():
        html = html.replace(f"{{{{{key}}}}}", str(value))
    return html


def send_email(settings: Settings, to: str, subject: str, html: str) -> bool:
    if not all([settings.smtp_host, settings.smtp_username, settings.smtp_password, settings.email_from]):
        logger.warning("SMTP not configured — skipping email to %s", to)
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.email_from
        msg["To"] = to
        msg.attach(MIMEText(html, "html"))
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(settings.smtp_username, settings.smtp_password)
            server.sendmail(settings.email_from, [to], msg.as_string())
        logger.info("Email sent to %s: %s", to, subject)
        return True
    except Exception as exc:
        logger.error("Failed to send email to %s: %s", to, exc)
        return False


def send_internship_alert(settings: Settings, to: str, internships: list[dict]) -> bool:
    if not internships:
        return False
    cards = ""
    for i in internships[:10]:
        cards += f"""
        <div style="border:1px solid #e5e7eb;border-radius:8px;padding:16px;margin-bottom:12px;">
          <div style="font-weight:600;font-size:16px;color:#111827;">{i.get('title', '')}</div>
          <div style="color:#6b7280;margin-top:4px;">{i.get('company', '')} · {i.get('location', '')}</div>
          <a href="{i.get('url', '#')}" style="display:inline-block;margin-top:8px;padding:6px 14px;background:#6366f1;color:#fff;border-radius:6px;text-decoration:none;font-size:13px;">Apply Now</a>
        </div>"""
    html = _render("internship_alert.html", {"cards": cards, "count": len(internships)})
    if not html:
        html = f"<h2>New Internship Matches</h2>{cards}"
    return send_email(settings, to, f"🎯 {len(internships)} New Internship Match(es) Found", html)
