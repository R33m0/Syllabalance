from flask import Flask, render_template, request

from priority_engine import (
    rank_courses,
    allocate_study_hours
)

from schedule_engine import build_study_schedule


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():
    ranked_courses = []
    study_schedule = None

    total_hours = None
    max_daily_hours = None
    error_message = None

    if request.method == "POST":
        try:
            course_names = request.form.getlist(
                "course_name"
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

            days_remaining = request.form.getlist(
                "days_remaining"
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

            if total_hours <= 0:
                raise ValueError(
                    "Total study hours must be positive."
                )

            if max_daily_hours <= 0:
                raise ValueError(
                    "Daily study limit must be positive."
                )

            courses = []

            for values in zip(
                course_names,
                current_grades,
                target_grades,
                assessment_weights,
                days_remaining,
                confidence_levels,
                credit_hours
            ):
                (
                    name,
                    current,
                    target,
                    weight,
                    days,
                    confidence,
                    credits
                ) = values

                if not name.strip():
                    raise ValueError(
                        "Every course needs a name."
                    )

                course = {
                    "name": name.strip(),
                    "current_grade": float(current),
                    "target_grade": float(target),
                    "assessment_weight": float(weight),
                    "days_remaining": int(days),
                    "confidence": int(confidence),
                    "credit_hours": int(credits)
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
                schedule_days=7
            )

        except (ValueError, KeyError, RuntimeError) as error:
            error_message = str(error)

            ranked_courses = []
            study_schedule = None

    return render_template(
        "index.html",
        ranked_courses=ranked_courses,
        study_schedule=study_schedule,
        total_hours=total_hours,
        max_daily_hours=max_daily_hours,
        error_message=error_message
    )


if __name__ == "__main__":
    app.run(debug=True)