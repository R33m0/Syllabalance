from nudge_engine import build_plan_nudges


def test_nudges_are_limited_and_urgency_ranked():
    courses = [
        {
            "name": "Physics",
            "assessment_name": "Final exam",
            "days_remaining": 2,
            "recommended_hours": 6.0,
            "feasibility_status": "challenging",
            "priority_score": 60,
            "required_grade": 84,
            "maximum_achievable_grade": 90
        },
        {
            "name": "Biology",
            "assessment_name": "Midterm",
            "days_remaining": 5,
            "recommended_hours": 3.0,
            "feasibility_status": "high_risk",
            "priority_score": 45,
            "required_grade": 94,
            "maximum_achievable_grade": 96
        },
        {
            "name": "Calculus",
            "assessment_name": "Final exam",
            "days_remaining": 7,
            "recommended_hours": 2.0,
            "feasibility_status": "secured",
            "priority_score": 30,
            "required_grade": 0,
            "maximum_achievable_grade": 100
        }
    ]

    nudges = build_plan_nudges(
        courses,
        limit=2
    )

    assert len(nudges) == 2
    assert "2 days" in nudges[0]["short"]


def test_impossible_target_nudge_uses_maximum_grade():
    courses = [
        {
            "name": "Biology",
            "assessment_name": "Final exam",
            "days_remaining": 4,
            "recommended_hours": 5.0,
            "feasibility_status": "not_possible",
            "priority_score": 65,
            "required_grade": 130,
            "maximum_achievable_grade": 82.5
        }
    ]

    nudges = build_plan_nudges(courses)

    assert "not reachable" in nudges[0]["short"]
    assert "82.5 out of 100" in nudges[0]["detailed"]


def test_unscheduled_hours_receive_highest_attention():
    courses = [
        {
            "name": "Physics",
            "assessment_name": "Final exam",
            "days_remaining": 1,
            "recommended_hours": 5.0,
            "feasibility_status": "high_risk",
            "priority_score": 70,
            "required_grade": 95,
            "maximum_achievable_grade": 97
        }
    ]

    schedule = {
        "days": [],
        "unscheduled": [
            {
                "course_name": "Physics",
                "assessment_name": "Final exam",
                "hours": 3.0
            }
        ]
    }

    nudges = build_plan_nudges(
        courses,
        study_schedule=schedule
    )

    assert nudges[0]["kind"] == "capacity"
    assert "3 hours" in nudges[0]["short"]