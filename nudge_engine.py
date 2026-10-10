def _day_word(days):
    return "day" if days == 1 else "days"


def _today_hours_for(course, study_schedule):
    if not study_schedule:
        return 0.0

    today = next(
        (
            day
            for day in study_schedule.get("days", [])
            if day.get("day_index") == 0
        ),
        None
    )

    if not today:
        return 0.0

    return round(
        sum(
            session["hours"]
            for session in today.get("sessions", [])
            if session["course_name"] == course["name"]
            and session.get("assessment_name")
            == course.get("assessment_name")
        ),
        1
    )


def _display_grade(value):
    number = round(float(value), 1)

    if number.is_integer():
        return str(int(number))

    return str(number)


def build_plan_nudges(
    ranked_courses,
    study_schedule=None,
    limit=3
):
    """Build a small urgency-ranked set of plan-based nudges."""

    if limit <= 0 or not ranked_courses:
        return []

    candidates = []

    unscheduled_by_course = {}

    if study_schedule:
        for item in study_schedule.get("unscheduled", []):
            key = (
                item["course_name"],
                item.get("assessment_name")
            )

            unscheduled_by_course[key] = item["hours"]

    for course in ranked_courses:
        course_name = course["name"]
        exam_name = course.get(
            "assessment_name",
            "exam"
        )
        days = int(course["days_remaining"])
        day_word = _day_word(days)
        planned_hours = round(
            float(course.get("recommended_hours", 0)),
            1
        )
        today_hours = _today_hours_for(
            course,
            study_schedule
        )

        unscheduled_hours = unscheduled_by_course.get(
            (course_name, course.get("assessment_name"))
        )

        if unscheduled_hours:
            candidates.append({
                "priority": 140 - min(days, 20),
                "course_name": course_name,
                "kind": "capacity",
                "short": (
                    f"{course_name} has {unscheduled_hours:g} hours "
                    f"that do not fit before {exam_name}."
                ),
                "detailed": (
                    f"{exam_name} for {course_name} has "
                    f"{unscheduled_hours:g} unscheduled hours because "
                    "the available daily capacity is too low before "
                    "the exam. Increase available time or reduce the "
                    "planned workload."
                )
            })
            continue

        if course.get("feasibility_status") == "not_possible":
            maximum = _display_grade(
                course["maximum_achievable_grade"]
            )

            candidates.append({
                "priority": 125 - min(days, 20),
                "course_name": course_name,
                "kind": "target",
                "short": (
                    f"{course_name}'s target is not reachable "
                    "through this exam."
                ),
                "detailed": (
                    f"Even with 100 out of 100 on {exam_name}, "
                    f"{course_name}'s highest possible overall grade "
                    f"is {maximum} out of 100. Consider adjusting the "
                    f"target to {maximum}."
                )
            })
            continue

        if days <= 3:
            if today_hours > 0:
                action = (
                    f"Start with today's {today_hours:g}-hour session."
                )
            else:
                action = "Protect some study time today."

            candidates.append({
                "priority": 110 - days,
                "course_name": course_name,
                "kind": "urgent",
                "short": (
                    f"{course_name}'s {exam_name} is in "
                    f"{days} {day_word}. "
                    f"{action}"
                ),
                "detailed": (
                    f"{exam_name} for {course_name} is in "
                    f"{days} {day_word}, with {planned_hours:g} "
                    f"study hours planned. {action}"
                )
            })
            continue

        if course.get("feasibility_status") == "high_risk":
            required = _display_grade(
                course["required_grade"]
            )

            candidates.append({
                "priority": 85 - min(days, 20),
                "course_name": course_name,
                "kind": "risk",
                "short": (
                    f"{course_name} needs a strong result on "
                    f"{exam_name}."
                ),
                "detailed": (
                    f"{course_name} needs about {required} out of 100 "
                    f"on {exam_name} to reach the target. Keep its "
                    f"{planned_hours:g} planned hours protected."
                )
            })

    top_course = ranked_courses[0]

    secured_course = next(
        (
            course
            for course in ranked_courses[1:]
            if course.get("feasibility_status") == "secured"
        ),
        None
    )

    if secured_course:
        candidates.append({
            "priority": 72,
            "course_name": secured_course["name"],
            "kind": "rebalance",
            "short": (
                f"{secured_course['name']} is already at target. "
                f"Keep {top_course['name']} first."
            ),
            "detailed": (
                f"{secured_course['name']}'s target is already "
                f"secured, while {top_course['name']} has the higher "
                "combined urgency and grade impact. Extra time would "
                f"help {top_course['name']} more."
            )
        })

    if not candidates:
        exam_name = top_course.get(
            "assessment_name",
            "exam"
        )
        days = int(top_course["days_remaining"])

        candidates.append({
            "priority": 50,
            "course_name": top_course["name"],
            "kind": "priority",
            "short": (
                f"{top_course['name']} is your first priority "
                "this week."
            ),
            "detailed": (
                f"{top_course['name']} ranks first because "
                f"{exam_name} is in {days} {_day_word(days)} and its "
                "grade impact is stronger than the other exams."
            )
        })

    candidates.sort(
        key=lambda nudge: nudge["priority"],
        reverse=True
    )

    selected = []
    seen_courses = set()

    for candidate in candidates:
        course_name = candidate["course_name"]

        if course_name in seen_courses:
            continue

        selected.append(candidate)
        seen_courses.add(course_name)

        if len(selected) == limit:
            break

    return selected
