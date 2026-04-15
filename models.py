# =============================================================================
# models.py — Database Models & Helpers
# Job Applicant Shortlisting System
# =============================================================================

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')


def get_db():
    """Return a new SQLite connection with row_factory set to dict-like rows."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # Rows behave like dicts
    return conn


def init_db():
    """Create tables if they don't exist and seed demo data if empty."""
    conn = get_db()
    cur  = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            name            TEXT    NOT NULL,
            skills          TEXT    NOT NULL,
            experience      REAL    NOT NULL DEFAULT 0,
            expected_salary REAL    NOT NULL DEFAULT 0,
            score           REAL    NOT NULL DEFAULT 0,
            created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()

    # Seed with demo candidates if table is empty
    cur.execute('SELECT COUNT(*) as cnt FROM candidates')
    if cur.fetchone()['cnt'] == 0:
        _seed_demo_data(cur, conn)

    conn.close()


def _seed_demo_data(cur, conn):
    """Insert realistic demo candidates so the app looks populated on first run."""
    demo = [
        ("Alice Johnson",   "Python, Django, REST API, PostgreSQL, Docker",  7,  95000,  0),
        ("Bob Martinez",    "JavaScript, React, Node.js, MongoDB, AWS",       5,  85000,  0),
        ("Carol White",     "Java, Spring Boot, Microservices, Kubernetes",   9, 110000,  0),
        ("David Kim",       "Python, Machine Learning, TensorFlow, SQL",      4,  78000,  0),
        ("Emma Davis",      "React, TypeScript, GraphQL, CSS, Redux",         3,  68000,  0),
        ("Frank Wilson",    "DevOps, CI/CD, Terraform, Ansible, Linux",       8, 105000,  0),
        ("Grace Lee",       "Data Science, R, Python, Tableau, Excel",        6,  90000,  0),
        ("Henry Brown",     "PHP, Laravel, MySQL, Vue.js, REST API",          2,  55000,  0),
        ("Iris Chen",       "Go, gRPC, Redis, Kafka, Microservices",          7,  98000,  0),
        ("Jack Thompson",   "Android, Kotlin, Java, Firebase, REST API",      5,  80000,  0),
        ("Karen Moore",     "iOS, Swift, SwiftUI, Objective-C, CoreData",     6,  88000,  0),
        ("Leo Garcia",      "C++, Embedded Systems, RTOS, Python",            10,115000,  0),
    ]

    from algorithms import calculate_score
    rows = []
    for name, skills, exp, salary, _ in demo:
        score = calculate_score(exp, skills, salary)
        rows.append((name, skills, exp, salary, score))

    cur.executemany(
        'INSERT INTO candidates (name, skills, experience, expected_salary, score) VALUES (?,?,?,?,?)',
        rows
    )
    conn.commit()


# ─────────────────────────────────────────────────────────────────────────────
# CRUD helpers
# ─────────────────────────────────────────────────────────────────────────────

def add_candidate(name, skills, experience, expected_salary, score):
    """Insert a new candidate and return the new row id."""
    conn = get_db()
    cur  = conn.cursor()
    cur.execute(
        'INSERT INTO candidates (name, skills, experience, expected_salary, score) VALUES (?,?,?,?,?)',
        (name, skills, experience, expected_salary, score)
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def get_all_candidates():
    """Return all candidates as a list of plain dicts."""
    conn = get_db()
    cur  = conn.cursor()
    cur.execute('SELECT * FROM candidates ORDER BY score DESC')
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows


def get_candidate_by_id(candidate_id):
    conn = get_db()
    cur  = conn.cursor()
    cur.execute('SELECT * FROM candidates WHERE id = ?', (candidate_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def delete_candidate(candidate_id):
    conn = get_db()
    cur  = conn.cursor()
    cur.execute('DELETE FROM candidates WHERE id = ?', (candidate_id,))
    conn.commit()
    affected = cur.rowcount
    conn.close()
    return affected > 0


def update_candidate(candidate_id, name, skills, experience, expected_salary, score):
    conn = get_db()
    cur  = conn.cursor()
    cur.execute(
        '''UPDATE candidates
           SET name=?, skills=?, experience=?, expected_salary=?, score=?
           WHERE id=?''',
        (name, skills, experience, expected_salary, score, candidate_id)
    )
    conn.commit()
    affected = cur.rowcount
    conn.close()
    return affected > 0
