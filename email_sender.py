"""
Email Sender
------------
Sends generated report files as email attachments.

If you are using Gmail, create an App Password
(your regular account password will not work):
https://myaccount.google.com/apppasswords
"""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders


def send_report_email(file_paths: list, email_config: dict):

    if not email_config.get("enabled", False):
        print(
            "[EmailSender] Email delivery is disabled "
            "in the configuration. Skipping email delivery."
        )
        return

    sender = email_config["sender_email"]
    password = email_config["sender_password"]
    recipients = email_config["recipients"]
    subject = email_config.get(
        "subject",
        "Automated Report"
    )

    msg = MIMEMultipart()

    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject

    msg.attach(
        MIMEText(
            "Please find the automatically generated report "
            "attached to this email.",
            "plain"
        )
    )

    for path in file_paths:

        if not path or not os.path.exists(path):
            continue

        with open(path, "rb") as f:

            part = MIMEBase(
                "application",
                "octet-stream"
            )

            part.set_payload(
                f.read()
            )

        encoders.encode_base64(part)

        part.add_header(
            "Content-Disposition",
            f"attachment; filename={os.path.basename(path)}"
        )

        msg.attach(part)


    print(
        f"[EmailSender] Sending email to: {recipients}"
    )

    with smtplib.SMTP(
        email_config["smtp_server"],
        email_config["smtp_port"]
    ) as server:

        server.starttls()

        server.login(
            sender,
            password
        )

        server.sendmail(
            sender,
            recipients,
            msg.as_string()
        )


    print(
        "[EmailSender] Email sent successfully!"
    )
