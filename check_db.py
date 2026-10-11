import sqlite3

conn = sqlite3.connect("data/recruiter_ai.db")
cursor = conn.cursor()

tables = [
    "jobs",
    "candidates",
    "applications",
    "evaluations",
    "interviews"
]

for table in tables:
    print("\n" + "=" * 50)
    print(table.upper())
    print("=" * 50)

    rows = cursor.execute(
        f"PRAGMA table_info({table})"
    ).fetchall()

    for row in rows:
        print(row)

conn.close()