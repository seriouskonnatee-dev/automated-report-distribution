"""
Documented email-distribution step.

IMPORTANT: This module intentionally does NOT send real email. `send_report()`
is a stub that logs what it *would* do and returns without opening a network
connection. This repo is a portfolio artifact; wiring it to a real SMTP server
and a real recipient list is left as a deliberate, documented manual step so
that cloning this repo can never accidentally spam anyone.

Real production wiring would look like:

    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.application import MIMEApplication
    import os

    def send_report(html_path, pdf_path, config):
        msg = MIMEMultipart("mixed")
        msg["Subject"] = config.subject_template.format(period=...)
        msg["From"] = config.sender_address
        msg["To"] = ", ".join(config.recipients)
        msg.attach(MIMEText(html_path.read_text(), "html"))
        with open(pdf_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=pdf_path.name)
        part["Content-Disposition"] = f'attachment; filename="{pdf_path.name}"'
        msg.attach(part)

        username = os.environ[config_smtp.username_env_var]
        password = os.environ[config_smtp.password_env_var]
        with smtplib.SMTP(config_smtp.host, config_smtp.port) as server:
            if config_smtp.use_tls:
                server.starttls()
            server.login(username, password)
            server.sendmail(config.sender_address, config.recipients, msg.as_string())

Credentials would come from environment variables / GitHub Actions secrets
(REPORT_SMTP_USERNAME, REPORT_SMTP_PASSWORD) — never committed to the repo.
"""
from __future__ import annotations

import logging
from pathlib import Path

from config import DISTRIBUTION_CONFIG, SMTPConfig

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def send_report(html_path: Path, pdf_path: Path, period: str, smtp_config: SMTPConfig | None = None) -> bool:
    """
    Stub distribution function. Logs the send that *would* happen and returns
    False (no send performed). See module docstring for the real SMTP wiring.
    """
    smtp_config = smtp_config or SMTPConfig()
    subject = DISTRIBUTION_CONFIG.subject_template.format(period=period)

    logger.info("STUB: would send email")
    logger.info("  from:    %s", DISTRIBUTION_CONFIG.sender_address)
    logger.info("  to:      %s", ", ".join(DISTRIBUTION_CONFIG.recipients))
    logger.info("  subject: %s", subject)
    logger.info("  attachments: %s, %s", html_path.name, pdf_path.name)
    logger.info("  smtp host: %s:%s (TLS=%s)", smtp_config.host, smtp_config.port, smtp_config.use_tls)
    logger.info("No email was actually sent (this is a documented stub).")
    return False


if __name__ == "__main__":
    # Demonstrates the stub against the most recently generated report, if any.
    reports_dir = Path(__file__).resolve().parent.parent / "reports"
    html_files = sorted(reports_dir.glob("sample_report_*.html"))
    pdf_files = sorted(reports_dir.glob("sample_report_*.pdf"))
    if html_files and pdf_files:
        send_report(html_files[-1], pdf_files[-1], period="demo period")
    else:
        logger.info("No generated report found. Run src/build_report.py first.")
