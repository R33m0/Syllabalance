from datetime import date

from flask import Flask, render_template, request

from priority_engine import (
    rank_courses,
    allocate_study_hours
)

from schedule_engine import build_study_schedule
from nudge_engine import build_plan_nudges


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():
    ranked_courses = []
    study_schedule = None
    nudges = []

    total_hours = None
    max_daily_hours = None
    study_style = "steady"
    grade_mode = "points"
    error_message = None

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

            grade_mode = request.form.get(
                "grade_mode",
                "points"
            )

            if grade_mode not in ("points", "percent"):
                grade_mode = "points"

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
                    "hours this week. Lower your total hours or "
                    "raise the daily limit."
                )

            today = date.today()

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
                    exam_date_text,
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

                try:
                    exam_date = date.fromisoformat(exam_date_text)
                except ValueError:
                    raise ValueError(
                        f"Choose an exam date for {name.strip()}."
                    )

                days = (exam_date - today).days

                if days < 1:
                    raise ValueError(
                        f"{name.strip()}'s exam date must be "
                        "after today."
                    )

                current_value = float(current)
                weight_value = float(weight)

                if grade_mode == "points":
                    available_points = 100 - weight_value

                    current_average = (
                        current_value / available_points * 100
                        if available_points > 0
                        else 0.0
                    )
                else:
                    current_average = current_value

                course = {
                    "name": name.strip(),
                    "assessment_name": assessment_name.strip(),
                    "current_grade": current_value,
                    "current_average": round(current_average, 1),
                    "grade_mode": grade_mode,
                    "target_grade": float(target),
                    "assessment_weight": weight_value,
                    "exam_date": exam_date.isoformat(),
                    "exam_date_label": (
                        f"{exam_date:%a}, {exam_date:%b} "
                        f"{exam_date.day}"
                    ),
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
        grade_mode=grade_mode,
        error_message=error_message
    )


if __name__ == "__main__":
    app.run(debug=True)