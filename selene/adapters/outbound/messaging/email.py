# adapters/external/email_service.py
import logging
from typing import List


class EmailNotificationAdapter:
    """Adapter for sending email notifications."""

    def __init__(self, smtp_host: str, smtp_port: int = 587):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self._logger = logging.getLogger(__name__)

    def send_completion_notification(
        self, recipients: List[str], mapping_results: dict, success_rate: float
    ) -> None:
        """Send mapping completion notification."""
        subject = f"selene Funds Mapping Complete - {success_rate:.1f}% Success Rate"

        body = f"""
        Mapping process completed successfully.

        Results Summary:
        - Total schemes processed: {mapping_results.get('total_schemes', 0)}
        - Total funds found: {mapping_results.get('total_funds', 0)}
        - Success rate: {success_rate:.2f}%

        Please review the detailed results in the output files.
        """

        self._send_email(recipients, subject, body)

    def _send_email(self, recipients: List[str], subject: str, body: str) -> None:
        """Send email using SMTP."""
        # Implementation depends on your email service
        self._logger.info("Email notification sent to %d recipients", len(recipients))
