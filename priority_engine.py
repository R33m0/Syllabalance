import numpy as np
from scipy.optimize import minimize


def calculate_required_grade(
    current_grade,
    target_grade,
    assessment_weight
):
    """
    Calculate the assessment grade required to reach
    a target course grade.

    The current grade is treated as the average across
    coursework completed before the assessment.
    """

    if not 0 <= current_grade <= 100:
        raise ValueError(
            "Current grade must be between 0 and 100."
        )

    if not 0 <= target_grade <= 100:
        raise ValueError(
            "Target grade must be between 0 and 100."
        )

    if not 0 < assessment_weight <= 100:
        raise ValueError(
            "Assessment weight must be greater than 0."
        )

    assessment_ratio = assessment_weight / 100
    completed_ratio = 1 - assessment_ratio

    completed_contribution = (
        current_grade * completed_ratio
    )

    required_grade = (
        target_grade - completed_contribution
    ) / assessment_ratio

    maximum_achievable_grade = (
        completed_contribution
        + 100 * assessment_ratio
    )

    minimum_possible_grade = (
        completed_contribution
    )

    required_grade = round(required_grade, 1)

    maximum_achievable_grade = round(
        maximum_achievable_grade,
        1
    )

    minimum_possible_grade = round(
        minimum_possible_grade,
        1
    )

    if required_grade <= 0:
        return {
            "required_grade": 0.0,
            "maximum_achievable_grade":
                maximum_achievable_grade,
            "minimum_possible_grade":
                minimum_possible_grade,
            "status": "secured",
            "message": (
                "The target is already secured even with "
                "a score of 0% on this assessment."
            )
        }

    if required_grade > 100:
        return {
            "required_grade": required_grade,
            "maximum_achievable_grade":
                maximum_achievable_grade,
            "minimum_possible_grade":
                minimum_possible_grade,
            "status": "not_possible",
            "message": (
                f"Reaching this target would require "
                f"{required_grade}%. Even with 100% on "
                f"the assessment, the highest achievable "
                f"course grade is "
                f"{maximum_achievable_grade}%."
            )
        }

    if required_grade <= 75:
        return {
            "required_grade": required_grade,
            "maximum_achievable_grade":
                maximum_achievable_grade,
            "minimum_possible_grade":
                minimum_possible_grade,
            "status": "within_reach",
            "message": (
                f"A score of {required_grade}% is needed "
                "to reach the target grade."
            )
        }

    if required_grade <= 90:
        return {
            "required_grade": required_grade,
            "maximum_achievable_grade":
                maximum_achievable_grade,
            "minimum_possible_grade":
                minimum_possible_grade,
            "status": "challenging",
            "message": (
                f"A score of {required_grade}% is needed. "
                "The target is achievable but requires "
                "a strong assessment result."
            )
        }

    return {
        "required_grade": required_grade,
        "maximum_achievable_grade":
            maximum_achievable_grade,
        "minimum_possible_grade":
            minimum_possible_grade,
        "status": "high_risk",
        "message": (
            f"A score of {required_grade}% is needed. "
            "The target is possible, but there is very "
            "little margin for lost marks."
        )
    }


def calculate_priority(
    current_grade,
    target_grade,
    assessment_weight,
    days_remaining,
    confidence,
    credit_hours
):
    """Calculate a course priority score from 0 to 100."""

    grade_gap = max(
        target_grade - current_grade,
        0
    ) / 100

    weight_score = assessment_weight / 100

    urgency_score = 1 / (
        1 + days_remaining / 7
    )

    confidence_need = (
        5 - confidence
    ) / 4

    credit_score = credit_hours / 4

    priority_score = (
        grade_gap * 0.30
        + weight_score * 0.25
        + urgency_score * 0.25
        + confidence_need * 0.15
        + credit_score * 0.05
    )

    return round(priority_score * 100, 2)


def create_priority_explanation(course):
    """
    Explain the main reasons behind a course's
    calculated priority.
    """

    reasons = []

    grade_gap = (
        course["target_grade"]
        - course["current_grade"]
    )

    if grade_gap >= 15:
        reasons.append(
            f"a {grade_gap:g}-point gap remains "
            "between the current and target grade"
        )

    elif grade_gap > 0:
        reasons.append(
            f"the target is {grade_gap:g} points above "
            "the current grade"
        )

    else:
        reasons.append(
            "the current grade already meets the target"
        )

    if course["days_remaining"] <= 3:
        reasons.append(
            f"the assessment is due in only "
            f"{course['days_remaining']} days"
        )

    elif course["days_remaining"] <= 7:
        reasons.append(
            "the assessment is due within one week"
        )

    if course["assessment_weight"] >= 30:
        reasons.append(
            f"the assessment contributes "
            f"{course['assessment_weight']:g}% "
            "of the course grade"
        )

    if course["confidence"] <= 2:
        reasons.append(
            "the reported confidence level is low"
        )

    if len(reasons) == 1:
        reasons.append(
            "its combined urgency and course weight "
            "still affect the recommendation"
        )

    return (
        "This course received its priority because "
        + ", and ".join(reasons)
        + "."
    )


def rank_courses(courses):
    """
    Calculate and rank courses from highest
    to lowest priority.
    """

    ranked_courses = []

    for course in courses:
        score = calculate_priority(
            current_grade=course["current_grade"],
            target_grade=course["target_grade"],
            assessment_weight=course[
                "assessment_weight"
            ],
            days_remaining=course["days_remaining"],
            confidence=course["confidence"],
            credit_hours=course["credit_hours"]
        )

        feasibility = calculate_required_grade(
            current_grade=course["current_grade"],
            target_grade=course["target_grade"],
            assessment_weight=course[
                "assessment_weight"
            ]
        )

        course_result = course.copy()

        course_result["priority_score"] = score

        course_result["required_grade"] = (
            feasibility["required_grade"]
        )

        course_result["maximum_achievable_grade"] = (
            feasibility[
                "maximum_achievable_grade"
            ]
        )

        course_result["minimum_possible_grade"] = (
            feasibility[
                "minimum_possible_grade"
            ]
        )

        course_result["feasibility_status"] = (
            feasibility["status"]
        )

        course_result["feasibility_message"] = (
            feasibility["message"]
        )

        course_result["priority_explanation"] = (
            create_priority_explanation(course)
        )

        ranked_courses.append(course_result)

    return sorted(
        ranked_courses,
        key=lambda course: course["priority_score"],
        reverse=True
    )


def allocate_study_hours(
    ranked_courses,
    total_hours
):
    """
    Allocate limited study hours using
    constrained optimization.
    """

    if total_hours <= 0:
        raise ValueError(
            "Total study hours must be greater than zero."
        )

    if not ranked_courses:
        return []

    priority_scores = np.array([
        max(course["priority_score"], 0.01)
        for course in ranked_courses
    ])

    number_of_courses = len(ranked_courses)

    starting_hours = np.full(
        number_of_courses,
        total_hours / number_of_courses
    )

    def objective(hours):
        utility = (
            priority_scores * np.log1p(hours)
        )

        return -np.sum(utility)

    constraints = {
        "type": "eq",
        "fun": lambda hours: (
            np.sum(hours) - total_hours
        )
    }

    bounds = [
        (0, total_hours)
        for _ in ranked_courses
    ]

    result = minimize(
        objective,
        starting_hours,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints
    )

    if not result.success:
        raise RuntimeError(
            "Study-hour optimization failed."
        )

    rounded_hours = np.round(
        result.x,
        1
    )

    rounding_difference = round(
        total_hours - np.sum(rounded_hours),
        1
    )

    highest_priority_index = np.argmax(
        priority_scores
    )

    rounded_hours[
        highest_priority_index
    ] += rounding_difference

    allocations = []

    for course, hours in zip(
        ranked_courses,
        rounded_hours
    ):
        course_result = course.copy()

        course_result["recommended_hours"] = float(
            hours
        )

        allocations.append(course_result)

    return allocations