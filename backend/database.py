import os
import sqlite3
import json
from datetime import datetime


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)

DB_PATH = os.path.join(
    DATA_DIR,
    "recruiter_ai.db"
)


os.makedirs(
    DATA_DIR,
    exist_ok=True
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():

    conn = sqlite3.connect(
        DB_PATH
    )

    conn.row_factory = sqlite3.Row

    return conn


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def init_database():

    conn = get_connection()

    cursor = conn.cursor()


    # --------------------------------------------------------
    # JOBS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (

            job_id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT NOT NULL,

            description TEXT NOT NULL,

            status TEXT DEFAULT 'Active',

            minimum_score REAL DEFAULT 70,

            required_skills TEXT DEFAULT '',

            preferred_skills TEXT DEFAULT '',

            created_at TEXT NOT NULL
        )
    """)


    # --------------------------------------------------------
    # CANDIDATES
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # APPLICATIONS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (

            application_id INTEGER PRIMARY KEY AUTOINCREMENT,

            job_id INTEGER NOT NULL,

            candidate_id INTEGER NOT NULL,

            status TEXT NOT NULL,

            overall_score REAL DEFAULT 0,

            created_at TEXT NOT NULL,

            FOREIGN KEY(job_id)
                REFERENCES jobs(job_id),

            FOREIGN KEY(candidate_id)
                REFERENCES candidates(candidate_id)
        )
    """)


    # --------------------------------------------------------
    # EVALUATIONS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evaluations (

            evaluation_id INTEGER PRIMARY KEY AUTOINCREMENT,

            application_id INTEGER NOT NULL UNIQUE,

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

            FOREIGN KEY(application_id)
                REFERENCES applications(application_id)
        )
    """)


    conn.commit()


    # ========================================================
    # DATABASE MIGRATION
    # ========================================================
    #
    # Existing databases created by the previous version may
    # not contain the new job criteria columns.
    #
    # ========================================================

    cursor.execute(
        "PRAGMA table_info(jobs)"
    )

    existing_columns = {
        row["name"]
        for row in cursor.fetchall()
    }


    if "minimum_score" not in existing_columns:

        cursor.execute("""
            ALTER TABLE jobs
            ADD COLUMN minimum_score REAL DEFAULT 70
        """)


    if "required_skills" not in existing_columns:

        cursor.execute("""
            ALTER TABLE jobs
            ADD COLUMN required_skills TEXT DEFAULT ''
        """)


    if "preferred_skills" not in existing_columns:

        cursor.execute("""
            ALTER TABLE jobs
            ADD COLUMN preferred_skills TEXT DEFAULT ''
        """)


    conn.commit()

    conn.close()


# ============================================================
# CREATE JOB
# ============================================================

def create_job(
    title,
    description,
    minimum_score=70,
    required_skills=None,
    preferred_skills=None
):

    if required_skills is None:
        required_skills = []

    if preferred_skills is None:
        preferred_skills = []


    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute("""
        INSERT INTO jobs
        (
            title,
            description,
            minimum_score,
            required_skills,
            preferred_skills,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (

        title,

        description,

        float(
            minimum_score
        ),

        json.dumps(
            required_skills
        ),

        json.dumps(
            preferred_skills
        ),

        datetime.now().isoformat()
    ))


    job_id = cursor.lastrowid


    conn.commit()

    conn.close()


    return job_id


# ============================================================
# GET JOBS
# ============================================================

def get_jobs(
    active_only=False
):

    conn = get_connection()


    if active_only:

        rows = conn.execute("""
            SELECT *
            FROM jobs
            WHERE status = 'Active'
            ORDER BY created_at DESC
        """).fetchall()

    else:

        rows = conn.execute("""
            SELECT *
            FROM jobs
            ORDER BY created_at DESC
        """).fetchall()


    conn.close()


    results = []


    for row in rows:

        item = dict(
            row
        )


        item[
            "required_skills"
        ] = parse_json_list(
            item.get(
                "required_skills"
            )
        )


        item[
            "preferred_skills"
        ] = parse_json_list(
            item.get(
                "preferred_skills"
            )
        )


        results.append(
            item
        )


    return results


# ============================================================
# GET SINGLE JOB
# ============================================================

def get_job(
    job_id
):

    conn = get_connection()


    row = conn.execute("""
        SELECT *
        FROM jobs
        WHERE job_id = ?
    """, (
        job_id,
    )).fetchone()


    conn.close()


    if not row:

        return None


    result = dict(
        row
    )


    result[
        "required_skills"
    ] = parse_json_list(
        result.get(
            "required_skills"
        )
    )


    result[
        "preferred_skills"
    ] = parse_json_list(
        result.get(
            "preferred_skills"
        )
    )


    return result


# ============================================================
# UPDATE JOB CRITERIA
# ============================================================

def update_job_criteria(
    job_id,
    minimum_score,
    required_skills,
    preferred_skills
):

    conn = get_connection()


    conn.execute("""
        UPDATE jobs
        SET
            minimum_score = ?,
            required_skills = ?,
            preferred_skills = ?
        WHERE job_id = ?
    """, (

        float(
            minimum_score
        ),

        json.dumps(
            required_skills
        ),

        json.dumps(
            preferred_skills
        ),

        job_id
    ))


    conn.commit()

    conn.close()


# ============================================================
# CREATE CANDIDATE
# ============================================================

def create_candidate(
    name,
    email,
    resume_filename,
    resume_path
):

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute("""
        INSERT INTO candidates
        (
            name,
            email,
            resume_filename,
            resume_path,
            uploaded_at
        )
        VALUES (?, ?, ?, ?, ?)
    """, (

        name,

        email,

        resume_filename,

        resume_path,

        datetime.now().isoformat()
    ))


    candidate_id = cursor.lastrowid


    conn.commit()

    conn.close()


    return candidate_id


# ============================================================
# CREATE APPLICATION
# ============================================================

def create_application(
    job_id,
    candidate_id,
    status,
    overall_score
):

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute("""
        INSERT INTO applications
        (
            job_id,
            candidate_id,
            status,
            overall_score,
            created_at
        )
        VALUES (?, ?, ?, ?, ?)
    """, (

        job_id,

        candidate_id,

        status,

        overall_score,

        datetime.now().isoformat()
    ))


    application_id = cursor.lastrowid


    conn.commit()

    conn.close()


    return application_id


# ============================================================
# JSON LIST HELPER
# ============================================================

def parse_json_list(
    value
):

    if not value:

        return []


    if isinstance(
        value,
        list
    ):

        return value


    try:

        result = json.loads(
            value
        )


        if isinstance(
            result,
            list
        ):

            return result


    except Exception:

        pass


    return []


# ============================================================
# SAVE EVALUATION
# ============================================================

def save_evaluation(
    application_id,
    result
):

    conn = get_connection()


    def get_value(
        data,
        keys,
        default=0
    ):

        if not isinstance(
            data,
            dict
        ):

            return default


        for key in keys:

            if key in data:

                return data[key]


        return default


    def get_list(
        data,
        keys
    ):

        value = get_value(
            data,
            keys,
            []
        )


        if isinstance(
            value,
            list
        ):

            return value


        if isinstance(
            value,
            str
        ):

            if value.strip():

                return [
                    value
                ]


        return []


    required = get_value(
        result,
        [
            "required_skill_score",
            "required_skills_score"
        ],
        0
    )


    preferred = get_value(
        result,
        [
            "preferred_skill_score",
            "preferred_skills_score"
        ],
        0
    )


    overall_skill = get_value(
        result,
        [
            "overall_skill_score"
        ],
        0
    )


    keyword = get_value(
        result,
        [
            "keyword_baseline",
            "keyword_score"
        ],
        0
    )


    evidence_score = get_value(
        result,
        [
            "verified_evidence_score",
            "evidence_score"
        ],
        0
    )


    hybrid = get_value(
        result,
        [
            "hybrid_skill_score"
        ],
        0
    )


    experience = get_value(
        result,
        [
            "experience_score"
        ],
        0
    )


    education = get_value(
        result,
        [
            "education_score"
        ],
        0
    )


    final_score = get_value(
        result,
        [
            "final_candidate_score",
            "final_score",
            "score"
        ],
        0
    )


    matched = get_list(
        result,
        [
            "matched_required_skills",
            "matched_skills"
        ]
    )


    missing = get_list(
        result,
        [
            "missing_required_skills",
            "missing_skills"
        ]
    )


    evidence_data = result.get(
        "evidence",
        result.get(
            "verified_evidence",
            []
        )
    )


    conn.execute("""
        INSERT OR REPLACE INTO evaluations
        (
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

        VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?
        )
    """, (

        application_id,

        required,

        preferred,

        overall_skill,

        keyword,

        evidence_score,

        hybrid,

        experience,

        education,

        final_score,

        json.dumps(
            matched,
            default=str
        ),

        json.dumps(
            missing,
            default=str
        ),

        json.dumps(
            evidence_data,
            default=str
        ),

        json.dumps(
            result,
            default=str
        )
    ))


    conn.execute("""
        UPDATE applications
        SET overall_score = ?
        WHERE application_id = ?
    """, (

        final_score,

        application_id
    ))


    conn.commit()

    conn.close()


# ============================================================
# GET APPLICATIONS FOR JOB
# ============================================================

def get_applications_for_job(
    job_id
):

    conn = get_connection()


    rows = conn.execute("""
        SELECT

            a.*,

            c.name,

            c.email,

            c.resume_filename,

            c.resume_path,

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

        JOIN candidates c
            ON a.candidate_id = c.candidate_id

        LEFT JOIN evaluations e
            ON a.application_id = e.application_id

        WHERE a.job_id = ?

        ORDER BY a.overall_score DESC
    """, (
        job_id,
    )).fetchall()


    conn.close()


    results = []


    for index, row in enumerate(
        rows,
        start=1
    ):

        item = dict(
            row
        )


        item[
            "rank"
        ] = index


        for field in [
            "matched_skills",
            "missing_skills",
            "evidence",
            "full_result"
        ]:

            if item.get(
                field
            ):

                try:

                    item[field] = json.loads(
                        item[field]
                    )

                except Exception:

                    pass


        results.append(
            item
        )


    return results


# ============================================================
# GET APPLICATION
# ============================================================

def get_application(
    application_id
):

    conn = get_connection()


    row = conn.execute("""
        SELECT

            a.*,

            c.name,

            c.email,

            c.resume_filename,

            c.resume_path,

            e.*

        FROM applications a

        JOIN candidates c
            ON a.candidate_id = c.candidate_id

        LEFT JOIN evaluations e
            ON a.application_id = e.application_id

        WHERE a.application_id = ?
    """, (
        application_id,
    )).fetchone()


    conn.close()


    if not row:

        return None


    result = dict(
        row
    )


    for field in [
        "matched_skills",
        "missing_skills",
        "evidence",
        "full_result"
    ]:

        if result.get(
            field
        ):

            try:

                result[field] = json.loads(
                    result[field]
                )

            except Exception:

                pass


    return result


# ============================================================
# UPDATE APPLICATION STATUS
# ============================================================

def update_application_status(
    application_id,
    status
):

    conn = get_connection()


    conn.execute("""
        UPDATE applications
        SET status = ?
        WHERE application_id = ?
    """, (

        status,

        application_id
    ))


    conn.commit()

    conn.close()


# ============================================================
# INITIALIZE
# ============================================================

init_database()