from datetime import date

from flask import Flask, render_template, request

from priority_engine import (
    rank_courses,
    allocate_study_hours
)

from schedule_engine import build_study_schedule
from nudge_engine import build_plan_nudges


app = Flask(__name__)


def _short_date(value):
    """Format a date without a leading zero on the day."""

    return value.strftime("%a, %b %d").replace(" 0", " ")


@app.route("/", methods=["GET", "POST"])
def home():
    ranked_courses = []
    study_schedule = None
    nudges = []

    total_hours = None
    max_daily_hours = None
    study_style = "steady"
    grading_mode = "points"
    error_message = None
    planning_date = date.today()

    if request.method == "POST":
        try:
            course_names = request.form.getlist(
                "course_name"
            )

            assessment_names = request.form.getlist(
                "assessment_name"
            )

            current_grades = request.form.getlist(
                "current_grade"
            )

            target_grades = request.form.getlist(
                "target_grade"
            )

            assessment_weights = request.form.getlist(
                "assessment_weight"
            )

            exam_dates = request.form.getlist(
                "exam_date"
            )

            confidence_levels = request.form.getlist(
                "confidence"
            )

            credit_hours = request.form.getlist(
                "credit_hours"
            )

            total_hours = float(
                request.form["total_hours"]
            )

            max_daily_hours = float(
                request.form["max_daily_hours"]
            )

            study_style = request.form.get(
                "study_style",
                "steady"
            )

            grading_mode = request.form.get(
                "grading_mode",
                "points"
            )

            submitted_today = request.form.get(
                "today_date",
                ""
            )

            if submitted_today:
                planning_date = date.fromisoformat(
                    submitted_today
                )

            if grading_mode not in {
                "points",
                "percentage"
            }:
                raise ValueError(
                    "Choose a valid grading mode."
                )

            if total_hours <= 0:
                raise ValueError(
                    "Total study hours must be positive."
                )

            if max_daily_hours <= 0:
                raise ValueError(
                    "Daily study limit must be positive."
                )

            weekly_capacity = max_daily_hours * 7

            if total_hours > weekly_capacity:
                raise ValueError(
                    f"With a {max_daily_hours:g}-hour daily limit, "
                    f"you can study at most {weekly_capacity:g} "
                    "hours this week."
                )

            courses = []

            for values in zip(
                course_names,
                assessment_names,
                current_grades,
                target_grades,
                assessment_weights,
                exam_dates,
                confidence_levels,
                credit_hours
            ):
                (
                    name,
                    assessment_name,
                    current,
                    target,
                    weight,
                    exam_date_value,
                    confidence,
                    credits
                ) = values

                if not name.strip():
                    raise ValueError(
                        "Every course needs a name."
                    )

                if not assessment_name.strip():
                    raise ValueError(
                        "Every course needs an upcoming exam."
                    )

                exam_date = date.fromisoformat(
                    exam_date_value
                )

                if exam_date < planning_date:
                    raise ValueError(
                        "Exam dates cannot be in the past."
                    )

                current_value = float(current)
                target_value = float(target)
                weight_value = float(weight)

                if not 0 < weight_value <= 100:
                    raise ValueError(
                        "Exam weight must be between 0 and 100."
                    )

                if not 0 <= current_value <= 100:
                    raise ValueError(
                        "Current grade must be between 0 and 100."
                    )

                if not 0 <= target_value <= 100:
                    raise ValueError(
                        "Desired grade must be between 0 and 100."
                    )

                completed_points_available = (
                    100 - weight_value
                )

                if (
                    grading_mode == "points"
                    and current_value
                    > completed_points_available
                ):
                    raise ValueError(
                        f"For {name.strip()}, points earned so far "
                        f"cannot exceed "
                        f"{completed_points_available:g} because "
                        f"the exam is worth {weight_value:g}%."
                    )

                days = (exam_date - planning_date).days

                course = {
                    "name": name.strip(),
                    "assessment_name": assessment_name.strip(),
                    "current_grade": current_value,
                    "target_grade": target_value,
                    "assessment_weight": weight_value,
                    "grading_mode": grading_mode,
                    "exam_date": exam_date,
                    "exam_date_iso": exam_date.isoformat(),
                    "exam_date_label": _short_date(exam_date),
                    "days_remaining": days,
                    "confidence": int(confidence),
                    "credit_hours": float(credits)
                }

                courses.append(course)

            if not courses:
                raise ValueError(
                    "Add at least one course."
                )

            ranked_courses = rank_courses(courses)

            ranked_courses = allocate_study_hours(
                ranked_courses,
                total_hours
            )

            study_schedule = build_study_schedule(
                allocated_courses=ranked_courses,
                max_daily_hours=max_daily_hours,
                start_date=planning_date,
                schedule_days=7,
                study_style=study_style
            )

            nudges = build_plan_nudges(
                ranked_courses=ranked_courses,
                study_schedule=study_schedule,
                limit=3
            )

        except (ValueError, KeyError, RuntimeError) as error:
            error_message = str(error)

            ranked_courses = []
            study_schedule = None
            nudges = []

    return render_template(
        "index.html",
        ranked_courses=ranked_courses,
        study_schedule=study_schedule,
        nudges=nudges,
        total_hours=total_hours,
        max_daily_hours=max_daily_hours,
        study_style=study_style,
        grading_mode=grading_mode,
        today_iso=planning_date.isoformat(),
        error_message=error_message
    )


if __name__ == "__main__":
    app.run(debug=True)