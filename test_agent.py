
import requests

API_URL = "http://127.0.0.1:8000/agent/chat"

tests = [
    "List the active jobs in the database.",
    "Show all applicants for job ID 1.",
    "Rank the top 5 candidates for job ID 1 by their evaluation scores, from highest to lowest.",
]

for question in tests:
    print("\n" + "=" * 60)
    print("QUESTION:", question)

    try:
        response = requests.post(
            API_URL,
            json={"message": question},
            timeout=120,
        )

        print("STATUS:", response.status_code)

        if response.ok:
            data = response.json()
            print("RESPONSE:")
            print(data.get("response", data))
            print("THREAD ID:", data.get("thread_id"))
        else:
            print("ERROR:", response.text)

    except requests.RequestException as exc:
        print("REQUEST FAILED:", exc)
