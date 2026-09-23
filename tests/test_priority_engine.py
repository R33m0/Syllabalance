from priority_engine import (
    calculate_required_grade,
    calculate_priority,
    create_priority_explanation,
    rank_courses,
    allocate_study_hours
)


def test_required_grade_calculation():
    result = calculate_required_grade(
        current_grade=80,
        target_grade=80,
        assessment_weight=30
    )

    assert result["required_grade"] == 80.0
    assert result["status"] == "challenging"

    assert (
        result["maximum_achievable_grade"]
        == 86.0
    )


def test_impossible_target_is_identified():
    result = calculate_required_grade(
        current_grade=70,
        target_grade=90,
        assessment_weight=25
    )

    assert result["required_grade"] == 150.0

    assert (
        result["maximum_achievable_grade"]
        == 77.5
    )

    assert (
        result["minimum_possible_grade"]
        == 52.5
    )

    assert result["status"] == "not_possible"

    assert "77.5%" in result["message"]


def test_invalid_assessment_weight_is_rejected():
    try:
        calculate_required_grade(
            current_grade=80,
            target_grade=85,
            assessment_weight=0
        )

        assert False

    except ValueError:
        assert True


def test_priority_calculation():
    score = calculate_priority(
        current_grade=70,
        target_grade=90,
        assessment_weight=25,
        days_remaining=7,
        confidence=2,
        credit_hours=4
    )

    assert score == 41.0


def test_closer_deadline_has_higher_priority():
    urgent_score = calculate_priority(
        current_grade=70,
        target_grade=85,
        assessment_weight=30,
        days_remaining=2,
        confidence=3,
        credit_hours=3
    )

    later_score = calculate_priority(
        current_grade=70,
        target_grade=85,
        assessment_weight=30,
        days_remaining=20,
        confidence=3,
        credit_hours=3
    )

    assert urgent_score > later_score


def test_priority_explanation_is_generated():
    course = {
        "name": "Course Alpha",
        "current_grade": 70,
        "target_grade": 90,
        "assessment_weight": 35,
        "days_remaining": 3,
        "confidence": 2,
        "credit_hours": 4
    }

    explanation = create_priority_explanation(course)

    assert "20-point gap" in explanation
    assert "3 days" in explanation
    assert "35%" in explanation
    assert "confidence level is low" in explanation


def test_courses_are_ranked_highest_first():
    courses = [
        {
            "name": "Course Alpha",
            "current_grade": 72,
            "target_grade": 88,
            "assessment_weight": 30,
            "days_remaining": 4,
            "confidence": 2,
            "credit_hours": 4
        },
        {
            "name": "Course Beta",
            "current_grade": 84,
            "target_grade": 88,
            "assessment_weight": 15,
            "days_remaining": 14,
            "confidence": 4,
            "credit_hours": 3
        },
        {
            "name": "Course Gamma",
            "current_grade": 78,
            "target_grade": 85,
            "assessment_weight": 20,
            "days_remaining": 10,
            "confidence": 3,
            "credit_hours": 3
        }
    ]

    ranked = rank_courses(courses)

    assert ranked[0]["name"] == "Course Alpha"

    assert (
        ranked[0]["priority_score"]
        >= ranked[1]["priority_score"]
    )

    assert (
        ranked[1]["priority_score"]
        >= ranked[2]["priority_score"]
    )

    assert "required_grade" in ranked[0]

    assert (
        "maximum_achievable_grade"
        in ranked[0]
    )

    assert "priority_explanation" in ranked[0]


def test_study_hour_allocation():
    ranked_courses = [
        {
            "name": "Course Alpha",
            "priority_score": 60
        },
        {
            "name": "Course Beta",
            "priority_score": 35
        },
        {
            "name": "Course Gamma",
            "priority_score": 20
        }
    ]

    allocations = allocate_study_hours(
        ranked_courses,
        total_hours=10
    )

    allocated_total = sum(
        course["recommended_hours"]
        for course in allocations
    )

    assert round(allocated_total, 1) == 10.0

    assert (
        allocations[0]["recommended_hours"]
        > allocations[1]["recommended_hours"]
    )