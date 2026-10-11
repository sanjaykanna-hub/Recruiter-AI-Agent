
import os
import requests

API_KEY = os.getenv("RESEND_API_KEY")
FROM_EMAIL = os.getenv(
    "RESEND_FROM_EMAIL",
    "Recruitment <onboarding@resend.dev>"
)

# Resend's special test recipient: simulates delivery, not a real inbox.
TO_EMAIL = "delivered@resend.dev"

if not API_KEY:
    print("ERROR: RESEND_API_KEY is not configured.")
    raise SystemExit(1)

payload = {
    "from": FROM_EMAIL,
    "to": [TO_EMAIL],
    "subject": "Recruiter AI Agent - Email Test",
    "text": (
        "Hello!\n\n"
        "This is a test request from your Recruiter AI Agent.\n"
        "Resend test mode is being checked."
    ),
}

try:
    response = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=20,
    )

    print("HTTP Status:", response.status_code)
    print("Resend Response:", response.text)

    if response.status_code in (200, 201):
        print("SUCCESS: Resend accepted the test request.")
        print("This does not mean an actual email reached an inbox.")
    else:
        print("FAILED: Check the response above.")

except requests.RequestException as error:
    print("NETWORK ERROR:", error)
