"""
Usage:
  To send an email with multiple recipients:
    python script.py --from sender@example.com --to recipient1@example.com,recipient2@example.com --subject "Test Subject" --text "This is a test email" --server smtp.example.com --username yourusername --password yourpassword

  To send an email with recipients from a file:
    python script.py --from sender@example.com --tofile /path/to/email_file.txt --subject "Test Subject" --text "This is a test email" --server smtp.example.com --username yourusername --password yourpassword

  Optional: Add '--attachment /path/to/attachment' to include an attachment.
"""
import smtplib
import argparse
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

def send_mail(send_from, recipient, subject, text, server, username, password, files=None):
    print(f"Creating email message for {recipient}...")

    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = recipient
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(text))

    if files:
        for f in files:
            print(f"Attaching file: {f}")
            with open(f, "rb") as fil:
                part = MIMEApplication(fil.read(), Name=basename(f))
            part['Content-Disposition'] = f'attachment; filename="{basename(f)}"'
            msg.attach(part)

    try:
        smtp = smtplib.SMTP(server)
        print("Connecting to SMTP server...")
        smtp.login(username, password)
        print("SMTP server authentication successful.")
    except smtplib.SMTPAuthenticationError:
        print("Error: Authentication failed. Check your username/password.")
        return
    except Exception as e:
        print(f"Error connecting to SMTP server: {e}")
        return

    try:
        print(f"Sending email to {recipient}...")
        smtp.sendmail(send_from, [recipient], msg.as_string())
        print(f"Email sent successfully to {recipient}.")
    except Exception as e:
        print(f"Error sending email to {recipient}: {e}")

    smtp.close()

def load_emails_from_file(file_path):
    print(f"Loading email addresses from {file_path}")
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send email via SMTP")
    parser.add_argument("--from", dest="send_from", required=True, help="Sender email address")
    parser.add_argument("--to", help="Recipient email address(es), comma-separated")
    parser.add_argument("--tofile", help="Path to a file with recipient email addresses, one per line")
    parser.add_argument("--subject", required=True, help="Email subject")
    parser.add_argument("--text", required=True, help="Email content")
    parser.add_argument("--server", required=True, help="SMTP server address")
    parser.add_argument("--username", required=True, help="SMTP server username")
    parser.add_argument("--password", required=True, help="SMTP server password")
    parser.add_argument("--attachment", help="Path to the attachment file")

    args = parser.parse_args()

    if args.to:
        recipients = args.to.split(',')
    elif args.tofile:
        recipients = load_emails_from_file(args.tofile)
    else:
        parser.error("--to or --tofile must be provided")

    files = [args.attachment] if args.attachment else None

    for recipient in recipients:
        send_mail(
            send_from=args.send_from,
            recipient=recipient,
            subject=args.subject,
            text=args.text,
            server=args.server,
            username=args.username,
            password=args.password,
            files=files
        )

