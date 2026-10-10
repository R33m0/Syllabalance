from datetime import date, timedelta

from app import app


def _plan_form(**overrides):
    today = date.today()

    data = {
        "study_style": "steady",
        "grading_mode": "points",
        "today_date": today.isoformat(),
        "course_name": "Physics",
        "assessment_name": "Final exam",
        "current_grade": "60",
        "target_grade": "90",
        "assessment_weight": "30",
        "exam_date": (today + timedelta(days=5)).isoformat(),
        "confidence": "3",
        "credit_hours": "4",
        "total_hours": "7",
        "max_daily_hours": "4"
    }

    data.update(overrides)
    return data


def test_points_mode_is_used_in_rendered_plan():
    client = app.test_client()
    response = client.post("/", data=_plan_form())
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'data-grading-mode="points"' in page
    assert "100.0" in page
    assert "5 days" in page


def test_weekly_capacity_validation_blocks_plan():
    client = app.test_client()
    response = client.post(
        "/",
        data=_plan_form(
            total_hours="29",
            max_daily_hours="4"
        )
    )
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert (
        "With a 4-hour daily limit, you can study at most "
        "28 hours this week."
        in page
    )
    assert "Study allocation" not in page


def test_points_mode_rejects_impossible_current_points():
    client = app.test_client()
    response = client.post(
        "/",
        data=_plan_form(current_grade="71")
    )
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "cannot exceed 70" in page
    assert "Study allocation" not in page
