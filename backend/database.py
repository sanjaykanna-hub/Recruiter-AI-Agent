import sqlite3

import json

import hashlib

import os


import re


from datetime import datetime

from pathlib import Path





# ============================================================

# DATABASE CONFIGURATION

# ============================================================



BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"

DB_PATH = DATA_DIR / "recruiter_ai.db"



DATA_DIR.mkdir(parents=True, exist_ok=True)





# ============================================================

# CONNECTION

# ============================================================



def get_connection():

    conn = sqlite3.connect(DB_PATH)

    conn.row_factory = sqlite3.Row

    return conn





# ============================================================

# DATABASE INITIALIZATION

# ============================================================



def init_database():

    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute("""

        CREATE TABLE IF NOT EXISTS jobs (

            job_id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT NOT NULL,

            description TEXT NOT NULL,

            status TEXT DEFAULT 'Active',

            created_at TEXT NOT NULL,

            minimum_score REAL DEFAULT 70,

            required_skills TEXT DEFAULT '',

            preferred_skills TEXT DEFAULT ''

        )

    """)



    cursor.execute("""

        CREATE TABLE IF NOT EXISTS candidates (

            candidate_id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            email TEXT NOT NULL,

            resume_filename TEXT NOT NULL,

            resume_path TEXT NOT NULL,

            uploaded_at TEXT NOT NULL

        )

    """)



    cursor.execute("""

        CREATE TABLE IF NOT EXISTS applications (

            application_id INTEGER PRIMARY KEY AUTOINCREMENT,

            job_id INTEGER NOT NULL,

            candidate_id INTEGER NOT NULL,

            status TEXT NOT NULL,

            overall_score REAL DEFAULT 0,

            created_at TEXT NOT NULL,

            FOREIGN KEY(job_id) REFERENCES jobs(job_id),

            FOREIGN KEY(candidate_id) REFERENCES candidates(candidate_id)

        )

    """)



    cursor.execute("""

        CREATE TABLE IF NOT EXISTS evaluations (

            evaluation_id INTEGER PRIMARY KEY AUTOINCREMENT,

            application_id INTEGER NOT NULL,

            required_skill_score REAL DEFAULT 0,

            preferred_skill_score REAL DEFAULT 0,

            overall_skill_score REAL DEFAULT 0,

            keyword_score REAL DEFAULT 0,

            evidence_score REAL DEFAULT 0,

            hybrid_skill_score REAL DEFAULT 0,

            experience_score REAL DEFAULT 0,

            education_score REAL DEFAULT 0,

            final_score REAL DEFAULT 0,

            matched_skills TEXT,

            missing_skills TEXT,

            evidence TEXT,

            full_result TEXT,

            FOREIGN KEY(application_id) REFERENCES applications(application_id)

        )

    """)



    cursor.execute("""

        CREATE TABLE IF NOT EXISTS interviews (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            application_id INTEGER NOT NULL,

            interview_date TEXT NOT NULL,

            interview_time TEXT NOT NULL,

            interview_type TEXT NOT NULL,

            interviewer TEXT NOT NULL,

            meeting_link TEXT DEFAULT '',

            notes TEXT DEFAULT '',

            status TEXT DEFAULT 'Scheduled',

            created_at TEXT DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(application_id) REFERENCES applications(application_id)

        )

    """)



    cursor.execute("""

        CREATE TABLE IF NOT EXISTS candidate_accounts (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            candidate_id INTEGER NOT NULL,

            name TEXT NOT NULL,

            email TEXT UNIQUE NOT NULL,

            password_hash TEXT NOT NULL,

            created_at TEXT NOT NULL,

            FOREIGN KEY(candidate_id) REFERENCES candidates(candidate_id)

        )

    """)



    cursor.execute("""

        CREATE TABLE IF NOT EXISTS notifications (

            notification_id INTEGER PRIMARY KEY AUTOINCREMENT,

            candidate_id INTEGER NOT NULL,

            application_id INTEGER,

            title TEXT NOT NULL,

            message TEXT NOT NULL,

            notification_type TEXT DEFAULT 'General',

            is_read INTEGER DEFAULT 0,

            created_at TEXT NOT NULL,

            FOREIGN KEY(candidate_id) REFERENCES candidates(candidate_id)

        )

    """)



    cursor.execute("""

        CREATE TABLE IF NOT EXISTS feedback (

            feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,

            candidate_id INTEGER,

            candidate_email TEXT NOT NULL,

            category TEXT DEFAULT 'General',

            message TEXT NOT NULL,

            created_at TEXT NOT NULL

        )

    """)



    cursor.execute("""

        CREATE TABLE IF NOT EXISTS agent_actions (

            action_id INTEGER PRIMARY KEY AUTOINCREMENT,

            application_id INTEGER,

            candidate_id INTEGER,

            job_id INTEGER,

            action_type TEXT NOT NULL,

            action_result TEXT,

            reasoning TEXT,

            created_at TEXT NOT NULL

        )

    """)



    conn.commit()

    conn.close()





# Ensure the database tables exist when this module is imported.

init_database()





# ============================================================

# HELPERS

# ============================================================



def _json_load(value, default=None):

    if default is None:

        default = []



    if value is None:

        return default



    if isinstance(value, (list, dict)):

        return value



    try:

        return json.loads(value)

    except (TypeError, ValueError, json.JSONDecodeError):

        return default





def _json_dump(value):

    try:

        return json.dumps(value, ensure_ascii=False)

    except (TypeError, ValueError):

        return json.dumps(str(value))





def _hash_password(password):

    # Compatibility helper. For a production app, use a password-hashing

    # algorithm such as Werkzeug's generate_password_hash/check_password_hash.

    return hashlib.sha256(password.encode("utf-8")).hexdigest()





def _row_to_dict(row):

    return dict(row) if row is not None else None





# ============================================================

# JOB FUNCTIONS

# ============================================================



def create_job(

    title,

    description,

    minimum_score=70,

    required_skills=None,

    preferred_skills=None

):

    conn = get_connection()

    try:

        cursor = conn.cursor()

        cursor.execute("""

            INSERT INTO jobs (

                title, description, status, created_at,

                minimum_score, required_skills, preferred_skills

            )

            VALUES (?, ?, 'Active', ?, ?, ?, ?)

        """, (

            title,

            description,

            datetime.now().isoformat(),

            minimum_score,

            _json_dump(required_skills or []),

            _json_dump(preferred_skills or [])

        ))

        job_id = cursor.lastrowid

        conn.commit()

        return job_id

    finally:

        conn.close()





def get_jobs(active_only=False):

    conn = get_connection()

    try:

        cursor = conn.cursor()

        if active_only:

            cursor.execute("""

                SELECT * FROM jobs

                WHERE status = 'Active'

                ORDER BY job_id DESC

            """)

        else:

            cursor.execute("SELECT * FROM jobs ORDER BY job_id DESC")



        results = []

        for row in cursor.fetchall():

            item = dict(row)

            item["id"] = item["job_id"]

            item["required_skills"] = _json_load(item.get("required_skills"), [])

            item["preferred_skills"] = _json_load(item.get("preferred_skills"), [])

            results.append(item)

        return results

    finally:

        conn.close()





def get_job(job_id):

    conn = get_connection()

    try:

        cursor = conn.cursor()

        cursor.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,))

        row = cursor.fetchone()

        if not row:

            return None



        item = dict(row)

        item["id"] = item["job_id"]

        item["required_skills"] = _json_load(item.get("required_skills"), [])

        item["preferred_skills"] = _json_load(item.get("preferred_skills"), [])

        return item

    finally:

        conn.close()





def update_job_criteria(

    job_id,

    minimum_score=None,

    required_skills=None,

    preferred_skills=None

):

    updates = []

    values = []



    if minimum_score is not None:

        updates.append("minimum_score = ?")

        values.append(minimum_score)



    if required_skills is not None:

        updates.append("required_skills = ?")

        values.append(_json_dump(required_skills))



    if preferred_skills is not None:

        updates.append("preferred_skills = ?")

        values.append(_json_dump(preferred_skills))



    if not updates:

        return True



    values.append(job_id)

    conn = get_connection()

    try:

        conn.execute(

            f"UPDATE jobs SET {', '.join(updates)} WHERE job_id = ?",

            values

        )

        conn.commit()

        return True

    finally:

        conn.close()





# ============================================================

# CANDIDATE FUNCTIONS

# ============================================================



def create_candidate(name, email, resume_filename, resume_path):

    conn = get_connection()

    try:

        cursor = conn.cursor()

        cursor.execute("""

            INSERT INTO candidates (

                name, email, resume_filename, resume_path, uploaded_at

            )

            VALUES (?, ?, ?, ?, ?)

        """, (

            name, email, resume_filename, resume_path,

            datetime.now().isoformat()

        ))

        candidate_id = cursor.lastrowid

        conn.commit()

        return candidate_id

    finally:

        conn.close()





def get_candidate(candidate_id):

    conn = get_connection()

    try:

        cursor = conn.cursor()

        cursor.execute(

            "SELECT * FROM candidates WHERE candidate_id = ?",

            (candidate_id,)

        )

        return _row_to_dict(cursor.fetchone())

    finally:

        conn.close()





def get_candidate_by_email(email):

    conn = get_connection()

    try:

        cursor = conn.cursor()

        cursor.execute("""

            SELECT * FROM candidates

            WHERE LOWER(email) = LOWER(?)

            LIMIT 1

        """, (email,))

        return _row_to_dict(cursor.fetchone())

    finally:

        conn.close()





def update_candidate_resume(candidate_id, resume_filename, resume_path):

    conn = get_connection()

    try:

        conn.execute("""

            UPDATE candidates

            SET resume_filename = ?, resume_path = ?, uploaded_at = ?

            WHERE candidate_id = ?

        """, (

            resume_filename,

            resume_path,

            datetime.now().isoformat(),

            candidate_id

        ))

        conn.commit()

        return True

    finally:

        conn.close()





# ============================================================

# APPLICATION FUNCTIONS

# ============================================================



def create_application(

    job_id,

    candidate_id,

    status="Under Review",

    overall_score=0,

    **kwargs

):

    """

    Create an application. Accepts overall_score because the candidate

    portal passes it. Extra keyword arguments are tolerated for compatibility

    with earlier versions of the UI.

    """

    conn = get_connection()

    try:

        cursor = conn.cursor()



        cursor.execute("""

            SELECT application_id

            FROM applications

            WHERE job_id = ? AND candidate_id = ?

            LIMIT 1

        """, (job_id, candidate_id))



        existing = cursor.fetchone()

        if existing:

            return existing["application_id"]



        cursor.execute("""

            INSERT INTO applications (

                job_id, candidate_id, status, overall_score, created_at

            )

            VALUES (?, ?, ?, ?, ?)

        """, (

            job_id,

            candidate_id,

            status,

            float(overall_score or 0),

            datetime.now().isoformat()

        ))



        application_id = cursor.lastrowid

        conn.commit()

        return application_id

    except Exception:

        conn.rollback()

        raise

    finally:

        conn.close()





def _application_to_dict(row):

    data = dict(row)



    data["id"] = data["application_id"]

    data["name"] = data.get("candidate_name") or "Unknown Candidate"

    data["email"] = data.get("candidate_email") or ""

    data["status"] = data.get("status") or "Under Review"



    app_score = float(data.get("application_overall_score") or 0)

    final = data.get("final_score")

    final_score = float(final if final is not None else app_score)



    score_fields = [

        "required_skill_score",

        "preferred_skill_score",

        "overall_skill_score",

        "keyword_score",

        "evidence_score",

        "hybrid_skill_score",

        "experience_score",

        "education_score"

    ]

    for field in score_fields:

        data[field] = float(data.get(field) or 0)



    data["final_score"] = final_score

    data["final_candidate_score"] = final_score

    data["score"] = final_score

    data["overall_score"] = final_score



    data["matched_skills"] = _json_load(data.get("matched_skills"), [])

    data["missing_skills"] = _json_load(data.get("missing_skills"), [])

    data["matched_required_skills"] = data["matched_skills"]

    data["missing_required_skills"] = data["missing_skills"]

    data["evidence"] = _json_load(data.get("evidence"), [])



    full_result = data.get("full_result")

    if isinstance(full_result, str):

        full_result = _json_load(full_result, {})

    if not isinstance(full_result, dict):

        full_result = {}

    data["evaluation_json"] = full_result



    if "application_created_at" in data:

        data["created_at"] = data.get("application_created_at")



    return data





_APPLICATION_SELECT = """

    SELECT

        a.application_id,

        a.job_id,

        a.candidate_id,

        a.status,

        a.overall_score AS application_overall_score,

        a.created_at AS application_created_at,

        c.name AS candidate_name,

        c.email AS candidate_email,

        c.resume_filename,

        c.resume_path,

        c.uploaded_at,

        e.evaluation_id,

        e.required_skill_score,

        e.preferred_skill_score,

        e.overall_skill_score,

        e.keyword_score,

        e.evidence_score,

        e.hybrid_skill_score,

        e.experience_score,

        e.education_score,

        e.final_score,

        e.matched_skills,

        e.missing_skills,

        e.evidence,

        e.full_result

    FROM applications a

    INNER JOIN candidates c ON a.candidate_id = c.candidate_id

    LEFT JOIN evaluations e ON e.evaluation_id = (

        SELECT MAX(e2.evaluation_id)

        FROM evaluations e2

        WHERE e2.application_id = a.application_id

    )

"""





def get_applications_for_job(job_id):

    conn = get_connection()

    try:

        cursor = conn.cursor()

        cursor.execute(

            _APPLICATION_SELECT + """

                WHERE a.job_id = ?

                ORDER BY COALESCE(e.final_score, a.overall_score, 0) DESC,

                         a.application_id DESC

            """,

            (job_id,)

        )

        return [_application_to_dict(row) for row in cursor.fetchall()]

    finally:

        conn.close()





def get_application(application_id):

    conn = get_connection()

    try:

        cursor = conn.cursor()

        cursor.execute(

            _APPLICATION_SELECT + """

                WHERE a.application_id = ?

                LIMIT 1

            """,

            (application_id,)

        )

        row = cursor.fetchone()

        return _application_to_dict(row) if row else None

    finally:

        conn.close()





# ============================================================

# EVALUATION FUNCTIONS

# ============================================================



def save_evaluation(application_id, result):

    result = result or {}



    def score(key, fallback=None):

        value = result.get(key, fallback)

        try:

            return float(value or 0)

        except (TypeError, ValueError):

            return 0.0



    final_score = score(

        "final_score",

        result.get("final_candidate_score", 0)

    )



    matched = result.get(

        "matched_skills",

        result.get("matched_required_skills", [])

    )

    missing = result.get(

        "missing_skills",

        result.get("missing_required_skills", [])

    )

    evidence = result.get("evidence", [])



    values = (

        score("required_skill_score"),

        score("preferred_skill_score"),

        score("overall_skill_score"),

        score("keyword_score"),

        score("evidence_score", result.get("semantic_evidence_score", 0)),

        score("hybrid_skill_score"),

        score("experience_score"),

        score("education_score"),

        final_score,

        _json_dump(matched),

        _json_dump(missing),

        _json_dump(evidence),

        _json_dump(result)

    )



    conn = get_connection()

    try:

        cursor = conn.cursor()

        cursor.execute("""

            SELECT evaluation_id FROM evaluations

            WHERE application_id = ?

            ORDER BY evaluation_id DESC

            LIMIT 1

        """, (application_id,))

        existing = cursor.fetchone()



        if existing:

            cursor.execute("""

                UPDATE evaluations SET

                    required_skill_score = ?,

                    preferred_skill_score = ?,

                    overall_skill_score = ?,

                    keyword_score = ?,

                    evidence_score = ?,

                    hybrid_skill_score = ?,

                    experience_score = ?,

                    education_score = ?,

                    final_score = ?,

                    matched_skills = ?,

                    missing_skills = ?,

                    evidence = ?,

                    full_result = ?

                WHERE evaluation_id = ?

            """, values + (existing["evaluation_id"],))

        else:

            cursor.execute("""

                INSERT INTO evaluations (

                    application_id,

                    required_skill_score,

                    preferred_skill_score,

                    overall_skill_score,

                    keyword_score,

                    evidence_score,

                    hybrid_skill_score,

                    experience_score,

                    education_score,

                    final_score,

                    matched_skills,

                    missing_skills,

                    evidence,

                    full_result

                )

                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

            """, (application_id,) + values)



        cursor.execute("""

            UPDATE applications

            SET overall_score = ?

            WHERE application_id = ?

        """, (final_score, application_id))



        conn.commit()

        return True

    finally:

        conn.close()





# ============================================================

# APPLICATION STATUS AND NOTIFICATIONS

# ============================================================



def update_application_status(

    application_id,

    status,

    create_notification_record=True,

    **kwargs

):

    # Accept legacy call styles without shadowing the create_notification() function.

    if "create_notification" in kwargs:

        create_notification_record = kwargs["create_notification"]

    if "send_notification" in kwargs:

        create_notification_record = kwargs["send_notification"]

    conn = get_connection()

    try:

        cursor = conn.cursor()

        cursor.execute("""

            SELECT status, candidate_id

            FROM applications

            WHERE application_id = ?

        """, (application_id,))

        row = cursor.fetchone()



        if not row:

            return False



        old_status = row["status"]

        candidate_id = row["candidate_id"]



        cursor.execute("""

            UPDATE applications

            SET status = ?

            WHERE application_id = ?

        """, (status, application_id))

        conn.commit()

    finally:

        conn.close()



    if create_notification_record and old_status != status:

        messages = {

            "Shortlisted": "Congratulations! Your application has been shortlisted.",

            "Rejected": "Thank you for applying. Unfortunately, your application was not selected for the next stage.",

            "Interview Scheduled": "Your application has progressed to the interview stage.",

            "Selected": "Congratulations! You have been selected for the position.",

            "On Hold": "Your application is currently on hold while the review continues.",

            "Under Review": "Your application is currently under review."

        }

        create_notification(

            candidate_id=candidate_id,

            application_id=application_id,

            title=f"Application Status: {status}",

            message=messages.get(

                status,

                f"Your application status has been updated to {status}."

            ),

            notification_type="Application Status"

        )



    return True





# ============================================================

# CANDIDATE ACCOUNTS

# ============================================================



def create_candidate_account(name, email, password):

    conn = get_connection()

    try:

        cursor = conn.cursor()



        cursor.execute("""

            SELECT id FROM candidate_accounts

            WHERE LOWER(email) = LOWER(?)

            LIMIT 1

        """, (email,))

        if cursor.fetchone():

            return None



        cursor.execute("""

            SELECT candidate_id FROM candidates

            WHERE LOWER(email) = LOWER(?)

            LIMIT 1

        """, (email,))

        existing_candidate = cursor.fetchone()



        if existing_candidate:

            candidate_id = existing_candidate["candidate_id"]

        else:

            cursor.execute("""

                INSERT INTO candidates (

                    name, email, resume_filename, resume_path, uploaded_at

                )

                VALUES (?, ?, '', '', ?)

            """, (name, email, datetime.now().isoformat()))

            candidate_id = cursor.lastrowid



        cursor.execute("""

            INSERT INTO candidate_accounts (

                candidate_id, name, email, password_hash, created_at

            )

            VALUES (?, ?, ?, ?, ?)

        """, (

            candidate_id,

            name,

            email,

            _hash_password(password),

            datetime.now().isoformat()

        ))



        account_id = cursor.lastrowid

        conn.commit()

        return account_id

    finally:

        conn.close()





def authenticate_candidate(email, password):

    conn = get_connection()

    try:

        cursor = conn.cursor()

        cursor.execute("""

            SELECT * FROM candidate_accounts

            WHERE LOWER(email) = LOWER(?)

              AND password_hash = ?

            LIMIT 1

        """, (email, _hash_password(password)))

        return _row_to_dict(cursor.fetchone())

    finally:

        conn.close()





def get_candidate_applications(candidate_id):

    conn = get_connection()

    try:

        cursor = conn.cursor()

        cursor.execute("""

            SELECT

                a.application_id,

                a.job_id,

                a.candidate_id,

                a.status,

                a.overall_score,

                a.created_at,

                j.title AS job_title,

                j.description AS job_description,

                j.minimum_score,

                e.final_score,

                e.required_skill_score,

                e.preferred_skill_score,

                e.overall_skill_score,

                e.matched_skills,

                e.missing_skills,

                e.full_result

            FROM applications a

            INNER JOIN jobs j ON a.job_id = j.job_id

            LEFT JOIN evaluations e ON e.evaluation_id = (

                SELECT MAX(e2.evaluation_id)

                FROM evaluations e2

                WHERE e2.application_id = a.application_id

            )

            WHERE a.candidate_id = ?

            ORDER BY a.application_id DESC

        """, (candidate_id,))



        results = []

        for row in cursor.fetchall():

            item = dict(row)

            final = item.get("final_score")

            if final is None:

                final = item.get("overall_score") or 0

            item["final_score"] = float(final or 0)

            item["final_candidate_score"] = item["final_score"]

            item["matched_skills"] = _json_load(item.get("matched_skills"), [])

            item["missing_skills"] = _json_load(item.get("missing_skills"), [])

            results.append(item)



        return results

    finally:

        conn.close()





# ============================================================

# NOTIFICATIONS

# ============================================================



def create_notification(

    candidate_id,

    application_id,

    title,

    message,

    notification_type="General"

):

    conn = get_connection()

    try:

        cursor = conn.cursor()

        cursor.execute("""

            INSERT INTO notifications (

                candidate_id, application_id, title, message,

                notification_type, is_read, created_at

            )

            VALUES (?, ?, ?, ?, ?, 0, ?)

        """, (

            candidate_id,

            application_id,

            title,

            message,

            notification_type,

            datetime.now().isoformat()

        ))

        notification_id = cursor.lastrowid

        conn.commit()

        return notification_id

    finally:

        conn.close()





def get_candidate_notifications(candidate_id):

    conn = get_connection()

    try:

        cursor = conn.cursor()

        cursor.execute("""

            SELECT * FROM notifications

            WHERE candidate_id = ?

            ORDER BY notification_id DESC

        """, (candidate_id,))

        return [dict(row) for row in cursor.fetchall()]

    finally:

        conn.close()





def mark_notification_read(notification_id):

    conn = get_connection()

    try:

        conn.execute("""

            UPDATE notifications SET is_read = 1

            WHERE notification_id = ?

        """, (notification_id,))

        conn.commit()

        return True

    finally:

        conn.close()





# ============================================================

# FEEDBACK

# ============================================================



def save_feedback(candidate_id, candidate_email, category, message):

    conn = get_connection()

    try:

        cursor = conn.cursor()

        cursor.execute("""

            INSERT INTO feedback (

                candidate_id, candidate_email, category, message, created_at

            )

            VALUES (?, ?, ?, ?, ?)

        """, (

            candidate_id,

            candidate_email,

            category,

            message,

            datetime.now().isoformat()

        ))

        feedback_id = cursor.lastrowid

        conn.commit()

        return feedback_id

    finally:

        conn.close()





# ============================================================

# ============================================================
# EMAIL DELIVERY (GMAIL API OAUTH)
# ============================================================

def send_interview_email(
    candidate_email,
    candidate_name,
    job_title,
    interview_date,
    interview_time,
    interview_type,
    interviewer,
    meeting_link="",
    notes=""
):
    """Send an interview invitation through Gmail API OAuth."""
    import base64
    from email.message import EmailMessage

    if not candidate_email or not str(candidate_email).strip():
        print("Interview email not sent: candidate email address is missing.")
        return False

    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError:
        print(
            "Interview email not sent: install Gmail API libraries with "
            "`python -m pip install google-api-python-client "
            "google-auth-httplib2 google-auth-oauthlib`."
        )
        return False

    base_dir = Path(__file__).resolve().parent.parent
    credentials_file = base_dir / "credentials.json"
    token_file = base_dir / "token.json"
    scopes = ["https://www.googleapis.com/auth/gmail.send"]

    if not credentials_file.exists():
        print(f"Interview email not sent: {credentials_file} was not found.")
        return False

    try:
        creds = None
        if token_file.exists():
            try:
                creds = Credentials.from_authorized_user_file(
                    str(token_file), scopes
                )
            except (ValueError, OSError) as exc:
                print(f"Could not read Gmail token file: {exc}")
                return False

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(credentials_file), scopes
                )
                creds = flow.run_local_server(port=0)

            token_file.write_text(creds.to_json(), encoding="utf-8")

        service = build("gmail", "v1", credentials=creds)

        message = EmailMessage()
        message["To"] = str(candidate_email).strip()
        message["Subject"] = f"Interview Invitation: {job_title or 'Interview'}"
        message.set_content(
            f"Hello {candidate_name or 'Candidate'},\n\n"
            "Your interview has been scheduled. Details:\n\n"
            f"Job title: {job_title or 'Interview'}\n"
            f"Date: {interview_date or 'Not specified'}\n"
            f"Time: {interview_time or 'Not specified'}\n"
            f"Interview type: {interview_type or 'Not specified'}\n"
            f"Interviewer: {interviewer or 'Not specified'}\n"
            f"Meeting link: {meeting_link or 'Not provided'}\n"
            f"Notes: {notes or 'No additional notes'}\n\n"
            "Please be ready at the scheduled time.\n\n"
            "Best regards,\nRecruitment Team"
        )

        encoded_message = base64.urlsafe_b64encode(
            message.as_bytes()
        ).decode("utf-8")

        result = service.users().messages().send(
            userId="me", body={"raw": encoded_message}
        ).execute()

        if result.get("id"):
            print(
                f"Interview email accepted by Gmail API for {candidate_email}. "
                f"Message ID: {result['id']}"
            )
            return True

        print("Gmail API did not return a message ID; email status is unknown.")
        return False

    except Exception as exc:
        print(f"Interview email failed: {type(exc).__name__}: {exc}")
        return False


# INTERVIEW FUNCTIONS

# ============================================================


def _find_resume_email(evaluation_result):
    """Find a candidate email address in resume evaluation data."""
    import json
    import re

    if not evaluation_result:
        return None

    # Convert JSON strings into Python objects when possible.
    if isinstance(evaluation_result, str):
        try:
            evaluation_result = json.loads(evaluation_result)
        except (json.JSONDecodeError, TypeError):
            pass

    email_pattern = re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    )

    preferred_keys = {
        "email",
        "candidate_email",
        "contact_email",
        "personal_email",
        "resume_email",
    }

    # First, look for email fields in structured data.
    def find_in_data(data):
        if isinstance(data, dict):
            # Prefer fields explicitly identified as email addresses.
            for key, value in data.items():
                if str(key).strip().lower() in preferred_keys:
                    if isinstance(value, str):
                        match = email_pattern.search(value)
                        if match:
                            return match.group(0)

            # Search nested dictionaries and lists.
            for value in data.values():
                result = find_in_data(value)
                if result:
                    return result

        elif isinstance(data, list):
            for item in data:
                result = find_in_data(item)
                if result:
                    return result

        elif isinstance(data, str):
            match = email_pattern.search(data)
            if match:
                return match.group(0)

        return None

    return find_in_data(evaluation_result)


def create_interview(

    application_id,

    interview_date,

    interview_time,

    interview_type="Online",

    interviewer="",

    meeting_link="",

    notes="",

    status="Scheduled",

    **kwargs

):

    """Save an interview, create an in-app notification, and email the candidate."""

    conn = get_connection()

    try:

        cursor = conn.cursor()

        cursor.execute("""

            SELECT c.name AS candidate_name,

                   c.email AS account_email,

                   j.title AS job_title,

                   e.full_result AS evaluation_result

            FROM applications a

            JOIN candidates c ON a.candidate_id = c.candidate_id

            JOIN jobs j ON a.job_id = j.job_id

            LEFT JOIN evaluations e ON e.evaluation_id = (

                SELECT MAX(e2.evaluation_id)

                FROM evaluations e2

                WHERE e2.application_id = a.application_id

            )

            WHERE a.application_id = ?

        """, (application_id,))

        candidate = cursor.fetchone()

        if not candidate:

            raise ValueError(f"Application {application_id} was not found.")



        cursor.execute("""

            SELECT id FROM interviews

            WHERE application_id = ?

              AND interview_date = ?

              AND interview_time = ?

              AND interview_type = ?

              AND interviewer = ?

            LIMIT 1

        """, (

            application_id, str(interview_date), str(interview_time),

            interview_type, interviewer

        ))

        existing = cursor.fetchone()

        if existing:

            # Do not send duplicate emails just because the same record is re-opened.

            return existing["id"]



        cursor.execute("""

            INSERT INTO interviews (

                application_id, interview_date, interview_time,

                interview_type, interviewer, meeting_link, notes,

                status, created_at

            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)

        """, (

            application_id, str(interview_date), str(interview_time),

            interview_type or "Online", interviewer or "", meeting_link or "",

            notes or "", status or "Scheduled", datetime.now().isoformat()

        ))

        interview_id = cursor.lastrowid

        conn.commit()

        candidate_data = dict(candidate)

        resume_email = _find_resume_email(candidate_data.get("evaluation_result"))

        # Prefer the address extracted from the resume. If the parser did not save

        # one, use the candidate's registered account email as a safe fallback.

        candidate_data["candidate_email"] = resume_email or candidate_data.get("account_email") or ""

        if resume_email:

            print(f"Using resume-extracted email for interview invitation: {resume_email}")

        else:

            print(

                "No email address was found in the saved resume evaluation; "

                f"using registered account email: {candidate_data['candidate_email'] or '(missing)'}"

            )

    except Exception:

        conn.rollback()

        raise

    finally:

        conn.close()



    update_application_status(application_id, "Interview Scheduled")



    email_sent = send_interview_email(

        candidate_email=candidate_data.get("candidate_email"),

        candidate_name=candidate_data.get("candidate_name"),

        job_title=candidate_data.get("job_title"),

        interview_date=interview_date,

        interview_time=interview_time,

        interview_type=interview_type,

        interviewer=interviewer,

        meeting_link=meeting_link,

        notes=notes

    )

    if not email_sent:

        print(

            "Interview was saved, but the candidate email was not sent. "

            "Check Gmail OAuth credentials/token and the terminal error above."

        )

    return interview_id





def get_interviews_for_application(application_id):

    conn = get_connection()

    try:

        cursor = conn.cursor()

        cursor.execute("""

            SELECT * FROM interviews

            WHERE application_id = ?

            ORDER BY interview_date, interview_time

        """, (application_id,))

        return [dict(row) for row in cursor.fetchall()]

    finally:

        conn.close()





# ============================================================

# AGENT ACTION LOG

# ============================================================



def save_agent_action(

    application_id=None,

    candidate_id=None,

    job_id=None,

    action_type="",

    action_result=None,

    reasoning=""

):

    conn = get_connection()

    try:

        cursor = conn.cursor()

        if action_result is not None and not isinstance(action_result, str):

            action_result = _json_dump(action_result)



        cursor.execute("""

            INSERT INTO agent_actions (

                application_id, candidate_id, job_id, action_type,

                action_result, reasoning, created_at

            )

            VALUES (?, ?, ?, ?, ?, ?, ?)

        """, (

            application_id,

            candidate_id,

            job_id,

            action_type,

            action_result,

            reasoning,

            datetime.now().isoformat()

        ))

        action_id = cursor.lastrowid

        conn.commit()

        return action_id

    finally:

        conn.close()





def get_agent_actions(application_id=None):

    conn = get_connection()

    try:

        cursor = conn.cursor()

        if application_id is None:

            cursor.execute(

                "SELECT * FROM agent_actions ORDER BY action_id DESC"

            )

        else:

            cursor.execute("""

                SELECT * FROM agent_actions

                WHERE application_id = ?

                ORDER BY action_id DESC

            """, (application_id,))

        return [dict(row) for row in cursor.fetchall()]

    finally:

        conn.close()





# ============================================================

# DATABASE SELF-TEST

# ============================================================



def database_test():

    print("\nRecruiter AI Database Test")

    print("=" * 45)



    conn = get_connection()

    try:

        cursor = conn.cursor()

        cursor.execute("""

            SELECT name FROM sqlite_master

            WHERE type = 'table'

            ORDER BY name

        """)

        tables = {row["name"] for row in cursor.fetchall()}



        for table in [

            "applications",

            "candidates",

            "candidate_accounts",

            "evaluations",

            "feedback",

            "interviews",

            "jobs",

            "notifications",

            "agent_actions"

        ]:

            print(f"  {'✓' if table in tables else '✗'} {table}")

    finally:

        conn.close()



    print(f"\nJobs found: {len(get_jobs())}")

    print(f"Active jobs found: {len(get_jobs(active_only=True))}")

    print("\nDatabase test completed.")





if __name__ == "__main__":

    database_test()
