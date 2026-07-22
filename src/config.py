"""
Report + distribution configuration.

Nothing in this file is a real credential or a real recipient. It exists to
show how the distribution step would be configured in production, per the
documented (but not executed) SMTP flow in email_distribution.py.
"""
from dataclasses import dataclass, field


@dataclass
class SMTPConfig:
    host: str = "smtp.example.com"
    port: int = 587
    use_tls: bool = True
    username_env_var: str = "REPORT_SMTP_USERNAME"   # read from env, never hardcoded
    password_env_var: str = "REPORT_SMTP_PASSWORD"   # read from env, never hardcoded


@dataclass
class DistributionConfig:
    sender_address: str = "reports@example.com"
    # Placeholder distribution list. In production this would be pulled from a
    # CRM/Salesforce report or a distribution-list table, not hardcoded here.
    recipients: list[str] = field(
        default_factory=lambda: [
            "sales-leadership@example.com",
            "regional-managers@example.com",
        ]
    )
    subject_template: str = "Weekly Sales Report - {period}"


SMTP_CONFIG = SMTPConfig()
DISTRIBUTION_CONFIG = DistributionConfig()
