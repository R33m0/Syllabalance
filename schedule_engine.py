from datetime import date, timedelta


def build_study_schedule(
    allocated_courses,
    max_daily_hours,
    start_date=None,
    schedule_days=7
):
    """
    Convert recommended course hours into a daily schedule.

    Courses with closer deadlines are scheduled first.
    Study sessions are placed before each assessment
    whenever possible.

    Returns the daily schedule and any hours that could
    not fit within the user's constraints.
    """

    if max_daily_hours <= 0:
        raise ValueError(
            "Maximum daily hours must be greater than zero."
        )

    if schedule_days <= 0:
        raise ValueError(
            "Schedule days must be greater than zero."
        )

    if start_date is None:
        start_date = date.today()

    schedule = []

    for day_index in range(schedule_days):
        current_date = (
            start_date + timedelta(days=day_index)
        )

        schedule.append({
            "date": current_date,
            "date_label": current_date.strftime(
                "%A, %d %B"
            ),
            "day_index": day_index,
            "sessions": [],
            "total_hours": 0.0
        })

    ordered_courses = sorted(
        allocated_courses,
        key=lambda course: (
            course["days_remaining"],
            -course["priority_score"]
        )
    )

    unscheduled = []

    for course in ordered_courses:
        remaining_hours = round(
            course["recommended_hours"],
            1
        )

        if remaining_hours <= 0:
            continue

        final_study_day = min(
            max(course["days_remaining"] - 1, 0),
            schedule_days - 1
        )

        eligible_days = schedule[
            :final_study_day + 1
        ]

        while remaining_hours > 0:
            available_days = [
                day
                for day in eligible_days
                if day["total_hours"] < max_daily_hours
            ]

            if not available_days:
                break

            selected_day = min(
                available_days,
                key=lambda day: (
                    day["total_hours"],
                    day["day_index"]
                )
            )

            remaining_capacity = round(
                max_daily_hours
                - selected_day["total_hours"],
                1
            )

            session_hours = min(
                remaining_hours,
                remaining_capacity,
                2.0
            )

            session_hours = round(
                session_hours,
                1
            )

            if session_hours <= 0:
                break

            existing_session = next(
                (
                    session
                    for session
                    in selected_day["sessions"]
                    if session["course_name"]
                    == course["name"]
                ),
                None
            )

            if existing_session:
                existing_session["hours"] = round(
                    existing_session["hours"]
                    + session_hours,
                    1
                )

            else:
                selected_day["sessions"].append({
                    "course_name": course["name"],
                    "hours": session_hours,
                    "priority_score":
                        course["priority_score"],
                    "days_remaining":
                        course["days_remaining"]
                })

            selected_day["total_hours"] = round(
                selected_day["total_hours"]
                + session_hours,
                1
            )

            remaining_hours = round(
                remaining_hours - session_hours,
                1
            )

        if remaining_hours > 0:
            unscheduled.append({
                "course_name": course["name"],
                "hours": remaining_hours,
                "reason": (
                    "Not enough available time before "
                    "the assessment deadline."
                )
            })

    active_days = [
        day
        for day in schedule
        if day["sessions"]
    ]

    scheduled_total = round(
        sum(
            day["total_hours"]
            for day in active_days
        ),
        1
    )

    unscheduled_total = round(
        sum(
            item["hours"]
            for item in unscheduled
        ),
        1
    )

    return {
        "days": active_days,
        "scheduled_total": scheduled_total,
        "unscheduled": unscheduled,
        "unscheduled_total": unscheduled_total
    }