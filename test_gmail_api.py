
import os
import base64
from email.message import EmailMessage

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(BASE_DIR, "credentials.json")
TOKEN_FILE = os.path.join(BASE_DIR, "token.json")


def get_gmail_service():
    if not os.path.exists(CREDENTIALS_FILE):
        raise FileNotFoundError(
            "credentials.json is missing from the project root."
        )

    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(
            TOKEN_FILE, SCOPES
        )

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w", encoding="utf-8") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def send_test_email(recipient):
    service = get_gmail_service()

    message = EmailMessage()
    message["To"] = recipient
    message["Subject"] = "Recruiter AI Agent - Gmail API Test"
    message.set_content(
        "Hello!\n\n"
        "This is a real test email from the Recruiter AI Agent.\n"
        "If you received this message, Gmail API OAuth is working."
    )

    encoded_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode("utf-8")

    result = service.users().messages().send(
        userId="me",
        body={"raw": encoded_message}
    ).execute()

    print("SUCCESS: Gmail API accepted the email.")
    print("Message ID:", result.get("id"))
    print("Check the recipient inbox and spam folder.")


if __name__ == "__main__":
    recipient = input(
        "Enter the recipient email address: "
    ).strip()

    if "@" not in recipient or not recipient:
        raise SystemExit("Please enter a valid email address.")

    try:
        send_test_email(recipient)
    except Exception as error:
        print("EMAIL TEST FAILED:", error)
