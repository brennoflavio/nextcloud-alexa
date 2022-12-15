import imaplib
import email
from email.header import decode_header
import webbrowser
import os
from typing import Tuple
from utils.text_utils import strip_links, strip_html
import html2text
from unidecode import unidecode
from fuzzywuzzy import process


def parse_email_string(email_bytes: bytes) -> Tuple[str, str, str, str]:
    msg = email.message_from_bytes(email_bytes)
    subject, encoding = decode_header(msg["Subject"])[0]

    if isinstance(subject, bytes):
        subject = subject.decode(encoding)

    from_email, encoding = decode_header(msg.get("From"))[0]
    if isinstance(from_email, bytes):
        from_email = from_email.decode(encoding)

    email_body = ""
    content_type = ""

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            try:
                body = part.get_payload(decode=True).decode()
                email_body = email_body + body
            except Exception:
                pass
    else:
        body = msg.get_payload(decode=True).decode()
        content_type = msg.get_content_type()
        email_body = email_body + body

    if "html" in content_type:
        email_body = strip_html(email_body)

    email_body = email_body.replace("\n", " ")
    email_body = unidecode(email_body)
    email_body = strip_links(email_body)

    email_body = "".join(
        [x for x in email_body if (x.isalnum() or x == " " or x in "!(),.:;?")]
    ).strip()

    while "  " in email_body:
        email_body = email_body.replace("  ", " ")

    return unidecode(subject), from_email, email_body, content_type


def get_emails(quantity: int) -> list:
    username = os.getenv("IMAP_USERNAME")
    password = os.getenv("IMAP_PASSWORD")
    imap_server = os.getenv("IMAP_SERVER")
    imap_port = int(os.getenv("IMAP_PORT"))

    imap = imaplib.IMAP4(imap_server, port=imap_port)
    imap.starttls()
    imap.login(username, password)

    status, messages = imap.select("INBOX")

    if status != "OK":
        return []

    messages = int(messages[0])

    final = []
    for i in range(messages, messages - quantity, -1):
        status, message = imap.fetch(str(i), "(RFC822)")

        if status != "OK":
            continue

        if message:
            message = message[0]
            if message:
                message = message[1]
                subject, from_email, email_body, content_type = parse_email_string(
                    message
                )

                final.append(
                    {
                        "subject": subject,
                        "from_email": from_email,
                        "email_body": email_body,
                        "content_type": content_type,
                    }
                )

    imap.close()
    imap.logout()

    return final


def get_emails_summary() -> str:
    emails = get_emails(5)
    if not emails:
        return "sem emails"

    if len(emails) >= 5:
        emails = emails[:5]

    emails_text = ", ".join([x.get("subject") for x in emails])

    return emails_text


def get_single_email(name: str) -> str:
    emails = get_emails(10)

    choices = [x.get("subject", "") for x in emails]
    extract = process.extractOne(name, choices)

    if extract:
        subject = extract[0]
        email = [x for x in emails if x.get("subject", "") == subject]

        if email:
            email = email[0].get("email_body")

            if len(email) >= 6000:
                email = email[:6000]

            return email

    return "Email não encontrado"


if __name__ == "__main__":
    from dotenv import load_dotenv
    import json

    load_dotenv()
    # print(json.dumps(get_emails(5), indent=4))
    print(get_single_email("avalie em 15 segundos"))
