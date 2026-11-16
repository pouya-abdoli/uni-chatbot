from models import (
    Base,
    Course,
    CourseInstructor,
    CourseRequirement,
    Instructor,
    SessionLocal,
    engine,
)
import pandas as pd
import sys


def read(sheet):
    """Load one Excel sheet as strings, trim cells, drop empty rows."""
    df = pd.read_excel("data/curriculum.xlsx", sheet_name=sheet, dtype=str)
    df = df.apply(lambda col: col.str.strip())
    df = df.replace(r"^\s*$", None, regex=True)
    return df.dropna(how="all")


# Rebuild schema (destroys all existing data)
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
db = SessionLocal()

# Lookup maps: Excel code/name -> DB integer id
course_id, instructor_id = {}, {}

# course_id = {
#     "4628171999": 1,   # Information Management Systems
#     "4628156372": 2,   # Internship
# }
# instructor_id = {
#     "Dr. Ahmadi": 1,
#     "Dr. Rezaei": 2,
# }

# Insert courses -> course_id["4628156372"]=1
for course_row in read("courses").itertuples():
    course = Course(
        code=course_row.code,
        title=course_row.title,
        credits=int(course_row.credits),
        semester=int(course_row.semester),
        description=course_row.description,
    )
    db.add(course)
    db.flush()
    course_id[course_row.code] = course.id

# Insert instructors -> instructor_id["Dr. Ahmadi"]=1
for instructor_row in read("instructors").itertuples():
    instructor = Instructor(name=instructor_row.name)
    db.add(instructor)
    db.flush()
    instructor_id[instructor_row.name] = instructor.id

# Link courses <-> instructors
# db.merge(CourseInstructor(course_id=3, instructor_id=7)) -> (3, 7)
for course_instructor_pair in read("course_instructors").itertuples():
    # Validate references before inserting
    if course_instructor_pair.course_code not in course_id:
        sys.exit(
            f"course_instructors: unknown course code {course_instructor_pair.course_code}"
        )
    if course_instructor_pair.instructor_name not in instructor_id:
        sys.exit(
            f"course_instructors: unknown instructor name {course_instructor_pair.instructor_name}"
        )

    # insert if new, skip if already exists
    db.merge(
        CourseInstructor(
            course_id=course_id[course_instructor_pair.course_code],
            instructor_id=instructor_id[course_instructor_pair.instructor_name],
        )
    )

# Insert each requirement row (course -> related course, prereq or coreq).
for requirement_row_pair in read("course_requirements").itertuples():
    for course_code in (
        requirement_row_pair.course_code,
        requirement_row_pair.related_course_code,
    ):
        if course_code not in course_id:
            sys.exit(f"course_requirements: unknown course code {course_code}")

    # Insert the requirement: course_code REQUIRES related_course_code.
    db.add(
        CourseRequirement(
            course_id=course_id[requirement_row_pair.course_code],
            related_course_id=course_id[requirement_row_pair.related_course_code],
            type=requirement_row_pair.type,
        )
    )

db.commit()
db.close()
print(f"Done: {len(course_id)} courses\n {len(instructor_id)} instructors")
