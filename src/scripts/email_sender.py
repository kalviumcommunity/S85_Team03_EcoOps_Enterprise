import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_report_email(report_text, recipient):
    """Send analytics report via email."""

    smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))

    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_PASSWORD")

    # Check credentials
    if not sender_email or not sender_password:
        print("Email credentials not configured. Skipping send.")
        return False

    # Create email
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient
    msg["Subject"] = "Weekly Analytics Report"

    msg.attach(MIMEText(report_text, "plain"))

    try:
        # Connect to SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)

        # Secure connection
        server.starttls()

        # Login
        server.login(sender_email, sender_password)

        # Send email
        server.send_message(msg)

        # Close connection
        server.quit()

        print("Report sent successfully.")
        return True

    except Exception as e:
        print("Email send failed: " + str(e))
        return False