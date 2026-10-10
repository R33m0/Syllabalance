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


def _single_exam_schedule(study_style):
    courses = [
        {
            "name": "Physics",
            "assessment_name": "Final exam",
            "priority_score": 70,
            "days_remaining": 7,
            "recommended_hours": 7.0
        }
    ]

    return build_study_schedule(
        allocated_courses=courses,
        max_daily_hours=4,
        start_date=date(2026, 9, 20),
        schedule_days=7,
        study_style=study_style
    )


def _daily_exam_hours(schedule):
    return [
        day["sessions"][0]["hours"]
        for day in schedule["days"]
    ]


def test_steady_style_spreads_hours_evenly():
    result = _single_exam_schedule("steady")
    hours = _daily_exam_hours(result)

    assert hours == [1.0] * 7


def test_front_loader_places_more_work_early():
    result = _single_exam_schedule("front-loader")
    hours = _daily_exam_hours(result)

    assert hours[0] > hours[-1]
    assert sum(hours[:2]) > sum(hours[-2:])


def test_deadline_driven_increases_hours_near_exam():
    result = _single_exam_schedule("deadline-driven")
    hours = _daily_exam_hours(result)

    assert len(hours) == 7
    assert all(hours_for_day > 0 for hours_for_day in hours)
    assert hours[-1] > hours[0]


def test_no_session_occurs_on_or_after_exam_day():
    courses = [
        {
            "name": "Physics",
            "assessment_name": "Midterm",
            "priority_score": 70,
            "days_remaining": 3,
            "recommended_hours": 6.0
        }
    ]

    result = build_study_schedule(
        allocated_courses=courses,
        max_daily_hours=3,
        start_date=date(2026, 9, 20),
        schedule_days=7,
        study_style="deadline-driven"
    )

    assert all(
        day["day_index"] < 3
        for day in result["days"]
    )


def test_exam_date_is_the_schedule_deadline_source():
    exam_date = date(2026, 9, 22)

    courses = [
        {
            "name": "Physics",
            "assessment_name": "Final exam",
            "priority_score": 70,
            "days_remaining": 7,
            "exam_date": exam_date,
            "recommended_hours": 6.0
        }
    ]

    result = build_study_schedule(
        allocated_courses=courses,
        max_daily_hours=3,
        start_date=date(2026, 9, 20),
        schedule_days=7,
        study_style="steady"
    )

    assert result["scheduled_total"] == 6.0
    assert all(
        day["date"] < exam_date
        for day in result["days"]
    )


def test_invalid_study_style_is_rejected():
    try:
        build_study_schedule(
            allocated_courses=[],
            max_daily_hours=2,
            start_date=date(2026, 9, 20),
            schedule_days=7,
            study_style="random"
        )

        assert False

    except ValueError:
        assert True
