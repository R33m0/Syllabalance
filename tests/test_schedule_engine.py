from datetime import date

from schedule_engine import build_study_schedule


def test_schedule_allocates_all_hours():
    courses = [
        {
            "name": "Course Alpha",
            "priority_score": 60,
            "days_remaining": 3,
            "recommended_hours": 4.0
        },
        {
            "name": "Course Beta",
            "priority_score": 40,
            "days_remaining": 6,
            "recommended_hours": 2.0
        }
    ]

    result = build_study_schedule(
        allocated_courses=courses,
        max_daily_hours=3,
        start_date=date(2026, 9, 20),
        schedule_days=7
    )

    assert result["scheduled_total"] == 6.0
    assert result["unscheduled_total"] == 0.0
    assert result["unscheduled"] == []


def test_sessions_respect_daily_limit():
    courses = [
        {
            "name": "Course Alpha",
            "priority_score": 60,
            "days_remaining": 4,
            "recommended_hours": 5.0
        },
        {
            "name": "Course Beta",
            "priority_score": 40,
            "days_remaining": 7,
            "recommended_hours": 3.0
        }
    ]

    result = build_study_schedule(
        allocated_courses=courses,
        max_daily_hours=2,
        start_date=date(2026, 9, 20),
        schedule_days=7
    )

    for day in result["days"]:
        assert day["total_hours"] <= 2.0


def test_urgent_course_is_scheduled_before_deadline():
    courses = [
        {
            "name": "Urgent Course",
            "priority_score": 70,
            "days_remaining": 3,
            "recommended_hours": 4.0
        }
    ]

    result = build_study_schedule(
        allocated_courses=courses,
        max_daily_hours=2,
        start_date=date(2026, 9, 20),
        schedule_days=7
    )

    urgent_sessions = [
        day
        for day in result["days"]
        if any(
            session["course_name"]
            == "Urgent Course"
            for session in day["sessions"]
        )
    ]

    assert urgent_sessions

    assert all(
        day["day_index"] <= 2
        for day in urgent_sessions
    )


def test_unscheduled_hours_are_reported():
    courses = [
        {
            "name": "Course Alpha",
            "priority_score": 70,
            "days_remaining": 1,
            "recommended_hours": 5.0
        }
    ]

    result = build_study_schedule(
        allocated_courses=courses,
        max_daily_hours=2,
        start_date=date(2026, 9, 20),
        schedule_days=7
    )

    assert result["scheduled_total"] == 2.0
    assert result["unscheduled_total"] == 3.0

    assert (
        result["unscheduled"][0]["course_name"]
        == "Course Alpha"
    )


def test_invalid_daily_limit_is_rejected():
    try:
        build_study_schedule(
            allocated_courses=[],
            max_daily_hours=0,
            start_date=date(2026, 9, 20),
            schedule_days=7
        )

        assert False

    except ValueError:
        assert True