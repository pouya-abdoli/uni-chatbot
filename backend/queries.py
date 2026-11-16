from sqlalchemy import text
from models import SessionLocal


def run(sql, **params):
    """Run one SQL query and return a list of dicts."""
    with SessionLocal() as db:
        result = db.execute(text(sql), params).mappings()

        rows = []
        for row in result:
            rows.append(dict(row))

        return rows


def verify_course_codes(*codes):
    """Return an error message if a course code does not exist."""
    for code in codes:
        if not run("SELECT 1 FROM courses WHERE code = :c", c=code):
            return {"error": f"course code {code} not found"}


def search_courses(word: str):
    """Find a course by name (or part of it) and return its CODE.

    CALL THIS FIRST whenever the user mentions a course by name.
    Returns every matching course with code, title and semester:
      - one result   -> use its code for the other tools
      - many results -> ask the user which one they mean
      - zero results -> the course does not exist
    """
    if not word or not word.strip():
        return []

    return run(
        """
        SELECT code, title, semester 
        FROM courses 
        WHERE title LIKE :w
        ORDER BY semester, id
    """,
        w=f"%{word.strip()}%",
    )


def course_info(code: str):
    """Credits, semester and description of one course. Needs a course code."""
    return (
        verify_course_codes(code)
        or run(
            "SELECT code, title, credits, semester, description "
            "FROM courses WHERE code = :c",
            c=code,
        )[0]
    )


def course_instructors(code: str):
    """Who teaches a course. Needs a course code."""
    return verify_course_codes(code) or run(
        """
        SELECT i.name FROM instructors i
        JOIN course_instructors ci ON ci.instructor_id = i.id
        JOIN courses c ON c.id = ci.course_id
        WHERE c.code = :c""",
        c=code,
    )


def prerequisites(code: str):
    """Direct prerequisites of a course (must be passed BEFORE it). Needs a course code."""
    return verify_course_codes(code) or run(
        """
        SELECT p.code, p.title FROM course_requirements r
        JOIN courses c ON c.id = r.course_id
        JOIN courses p ON p.id = r.related_course_id
        WHERE c.code = :c AND r.type = 'prereq'""",
        c=code,
    )


def corequisites(code: str):
    """Co-requisites of a course (taken in the SAME semester). Needs a course code.
    Each pair is stored once, so both directions are checked."""
    return verify_course_codes(code) or run(
        """
        SELECT p.code, p.title FROM course_requirements r
        JOIN courses c ON c.id = r.course_id
        JOIN courses p ON p.id = r.related_course_id
        WHERE c.code = :c AND r.type = 'coreq'
        UNION
        SELECT c.code, c.title FROM course_requirements r
        JOIN courses c ON c.id = r.course_id
        JOIN courses p ON p.id = r.related_course_id
        WHERE p.code = :c AND r.type = 'coreq'""",
        c=code,
    )


def required_by(code: str):
    """Which courses have this course as a prerequisite. Needs a course code."""
    return verify_course_codes(code) or run(
        """
        SELECT c.code, c.title FROM course_requirements r
        JOIN courses c ON c.id = r.course_id
        JOIN courses p ON p.id = r.related_course_id
        WHERE p.code = :c AND r.type = 'prereq'""",
        c=code,
    )


def can_take_together(code_a: str, code_b: str):
    """Can two courses be taken in the same semester? Needs BOTH course codes."""
    err = verify_course_codes(code_a, code_b)
    if err:
        return err
    rows = run(
        """
        SELECT r.type, c.title AS course, p.title AS requires
        FROM course_requirements r
        JOIN courses c ON c.id = r.course_id
        JOIN courses p ON p.id = r.related_course_id
        WHERE (c.code = :a AND p.code = :b)
           OR (c.code = :b AND p.code = :a)""",
        a=code_a,
        b=code_b,
    )
    if any(r["type"] == "coreq" for r in rows):
        return {"can_take_together": True, "reason": "they are co-requisites"}
    if rows:
        return {
            "can_take_together": False,
            "reason": f"'{rows[0]['course']}' has '{rows[0]['requires']}' as a prerequisite",
        }
    return {
        "can_take_together": None,
        "reason": "no prerequisite or co-requisite rule between them",
    }


def instructor_courses(name: str):
    """Courses taught by an instructor. `name` can be part of the name, like 'نقیب'."""
    return run(
        """
        SELECT i.name AS instructor, c.code, c.title, c.semester
        FROM courses c
        JOIN course_instructors ci ON ci.course_id = c.id
        JOIN instructors i ON i.id = ci.instructor_id
        WHERE i.name LIKE :n
        ORDER BY c.semester""",
        n=f"%{name}%",
    )


def list_courses(semester: int | None = None, min_credits: int | None = None):
    """List courses. Optional filters: only one semester, and/or at least min_credits credits."""
    return run(
        """
        SELECT code, title, credits, semester FROM courses
        WHERE (:s IS NULL OR semester = :s)
          AND (:m IS NULL OR credits >= :m)
        ORDER BY semester, id""",
        s=semester,
        m=min_credits,
    )


def count_courses(semester: int):
    """How many courses are in a semester."""
    return run("SELECT COUNT(*) AS count FROM courses WHERE semester = :s", s=semester)[
        0
    ]


def courses_without_prereq():
    """Courses that have no prerequisite."""
    return run("""
        SELECT code, title, semester FROM courses c
        WHERE NOT EXISTS (
            SELECT 1 FROM course_requirements r
            WHERE r.course_id = c.id AND r.type = 'prereq'
        )
        ORDER BY semester, id""")


def courses_with_prereq_and_coreq():
    """Courses that have both a prerequisite and a co-requisite."""
    return run("""
        SELECT code, title, semester FROM courses c
        WHERE EXISTS (SELECT 1 FROM course_requirements r
                      WHERE r.course_id = c.id AND r.type = 'prereq')
          AND EXISTS (SELECT 1 FROM course_requirements r
                      WHERE r.course_id = c.id AND r.type = 'coreq')""")


def coreq_pairs():
    """All pairs of co-requisite courses."""
    return run("""
        SELECT c.title AS course, p.title AS corequisite
        FROM course_requirements r
        JOIN courses c ON c.id = r.course_id
        JOIN courses p ON p.id = r.related_course_id
        WHERE r.type = 'coreq'
        ORDER BY c.semester""")


def prereq_pairs():
    """All pairs of prerequisite courses (Course -> Requires)."""
    return run("""
        SELECT c.title AS course, p.title AS prerequisite
        FROM course_requirements r
        JOIN courses c ON c.id = r.course_id
        JOIN courses p ON p.id = r.related_course_id
        WHERE r.type = 'prereq'
        ORDER BY c.semester""")
