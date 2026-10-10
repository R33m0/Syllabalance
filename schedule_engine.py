from datetime import date, timedelta


VALID_STUDY_STYLES = {
    "steady",
    "front-loader",
    "deadline-driven"
}

HOUR_UNIT = 0.1


def _exam_date(course):
    """Return a course exam date when one was supplied."""

    value = course.get("exam_date")

    if value is None or value == "":
        return None

    if isinstance(value, date):
        return value

    try:
        return date.fromisoformat(str(value))
    except ValueError as error:
        raise ValueError(
            "Exam dates must use YYYY-MM-DD format."
        ) from error


def _hours_to_units(hours):
    """Convert decimal hours into integer tenths of an hour."""

    return max(int(round(float(hours) / HOUR_UNIT)), 0)


def _units_to_hours(units):
    """Convert integer tenths back into display-ready hours."""

    return round(units * HOUR_UNIT, 1)


def _weighted_units(total_units, weights):
    """Split integer units proportionally without losing any units."""

    if total_units <= 0 or not weights:
        return [0 for _ in weights]

    weight_total = sum(weights)

    raw_shares = [
        total_units * weight / weight_total
        for weight in weights
    ]

    units = [int(share) for share in raw_shares]

    remaining_units = total_units - sum(units)

    remainder_order = sorted(
        range(len(weights)),
        key=lambda index: (
            raw_shares[index] - units[index],
            weights[index]
        ),
        reverse=True
    )

    for index in remainder_order[:remaining_units]:
        units[index] += 1

    return units


def _build_style_targets(
    total_units,
    eligible_day_count,
    study_style
):
    """Return the preferred per-day units for one exam."""

    if eligible_day_count <= 0:
        return []

    if study_style == "steady":
        return _weighted_units(
            total_units,
            [1 for _ in range(eligible_day_count)]
        )

    if study_style == "front-loader":
        weights = [
            (eligible_day_count - index) ** 2
            for index in range(eligible_day_count)
        ]

        return _weighted_units(total_units, weights)

    minimum_units = 1 if total_units >= eligible_day_count else 0

    targets = [
        minimum_units
        for _ in range(eligible_day_count)
    ]

    remaining_units = total_units - sum(targets)

    increasing_weights = [
        (index + 1) ** 2
        for index in range(eligible_day_count)
    ]

    extra_units = _weighted_units(
        remaining_units,
        increasing_weights
    )

    return [
        base_units + extra
        for base_units, extra in zip(
            targets,
            extra_units
        )
    ]


def _add_session(day, course, session_units):
    """Add or extend one exam session on a schedule day."""

    if session_units <= 0:
        return

    session_hours = _units_to_hours(session_units)

    existing_session = next(
        (
            session
            for session in day["sessions"]
            if session["course_name"] == course["name"]
            and session.get("assessment_name")
            == course.get("assessment_name")
        ),
        None
    )

    if existing_session:
        existing_session["hours"] = round(
            existing_session["hours"] + session_hours,
            1
        )
    else:
        day["sessions"].append({
            "course_name": course["name"],
            "assessment_name": course.get(
                "assessment_name"
            ),
            "hours": session_hours,
            "priority_score": course["priority_score"],
            "days_remaining": course["days_remaining"]
        })

    day["used_units"] += session_units
    day["total_hours"] = _units_to_hours(
        day["used_units"]
    )


def _spill_order(eligible_days, study_style):
    """Choose where overflow should go for each study style."""

    if study_style == "front-loader":
        return sorted(
            eligible_days,
            key=lambda day: day["day_index"]
        )

    if study_style == "deadline-driven":
        return sorted(
            eligible_days,
            key=lambda day: day["day_index"],
            reverse=True
        )

    return sorted(
        eligible_days,
        key=lambda day: (
            day["used_units"],
            day["day_index"]
        )
    )


def build_study_schedule(
    allocated_courses,
    max_daily_hours,
    start_date=None,
    schedule_days=7,
    study_style="steady"
):
    """
    Convert recommended exam hours into a seven-day schedule.

    Study styles change the shape of each exam's schedule:
    steady spreads work evenly, front-loader emphasizes early
    days, and deadline-driven increases work near the exam while
    reserving a minimum session on every eligible day when the
    allocated hours allow it.

    Sessions are never placed on or after an exam day. The daily
    total never exceeds the supplied maximum daily study hours.
    """

    if max_daily_hours <= 0:
        raise ValueError(
            "Maximum daily hours must be greater than zero."
        )

    if schedule_days <= 0:
        raise ValueError(
            "Schedule days must be greater than zero."
        )

    if study_style not in VALID_STUDY_STYLES:
        raise ValueError(
            "Study style must be steady, front-loader, "
            "or deadline-driven."
        )

    if start_date is None:
        start_date = date.today()

    maximum_daily_units = _hours_to_units(
        max_daily_hours
    )

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
            "total_hours": 0.0,
            "used_units": 0
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
        remaining_units = _hours_to_units(
            course["recommended_hours"]
        )

        if remaining_units <= 0:
            continue

        course_exam_date = _exam_date(course)

        if course_exam_date is not None:
            eligible_days = [
                day
                for day in schedule
                if day["date"] < course_exam_date
            ]
        else:
            eligible_day_count = min(
                max(int(course["days_remaining"]), 0),
                schedule_days
            )

            eligible_days = schedule[:eligible_day_count]

        eligible_day_count = len(eligible_days)

        targets = _build_style_targets(
            remaining_units,
            eligible_day_count,
            study_style
        )

        for day, target_units in zip(
            eligible_days,
            targets
        ):
            available_units = max(
                maximum_daily_units - day["used_units"],
                0
            )

            session_units = min(
                target_units,
                available_units,
                remaining_units
            )

            _add_session(
                day,
                course,
                session_units
            )

            remaining_units -= session_units

        while remaining_units > 0:
            available_days = [
                day
                for day in eligible_days
                if day["used_units"] < maximum_daily_units
            ]

            if not available_days:
                break

            selected_day = _spill_order(
                available_days,
                study_style
            )[0]

            available_units = (
                maximum_daily_units
                - selected_day["used_units"]
            )

            session_units = min(
                remaining_units,
                available_units
            )

            _add_session(
                selected_day,
                course,
                session_units
            )

            remaining_units -= session_units

        if remaining_units > 0:
            unscheduled.append({
                "course_name": course["name"],
                "assessment_name": course.get(
                    "assessment_name"
                ),
                "hours": _units_to_hours(
                    remaining_units
                ),
                "reason": (
                    "Not enough available time before "
                    "the exam date."
                )
            })

    for day in schedule:
        day.pop("used_units", None)

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
        "unscheduled_total": unscheduled_total,
        "study_style": study_style
    }
