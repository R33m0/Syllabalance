# Syllabalance

Syllabalance is a Flask-based academic planning tool that helps students decide where their limited study time should go.

Instead of only listing assignments, it considers grade gaps, assessment weight, deadlines, confidence, course credit hours, and weekly availability. It then ranks competing course priorities, explains the ranking, and produces a realistic study schedule.

## Screenshots

### Course planner

![Syllabalance course planner](docs/screenshots/planner.png)

### Priority results

![Syllabalance priority results](docs/screenshots/results.png)

### Weekly schedule

![Syllabalance weekly schedule](docs/screenshots/schedule.png)

## What the application does

- Accepts multiple courses and assessments.
- Ranks courses using an explainable priority model.
- Allocates a limited number of weekly study hours.
- Checks whether a target grade is mathematically reachable.
- Calculates the assessment score required to reach a target.
- Lets students test possible assessment outcomes.
- Builds a seven-day study schedule.
- Explains why each course received its ranking.
- Supports light and dark themes.
- Stores interface preferences locally in the browser.
- Does not permanently store entered course information.

## Understanding the inputs

### Current course grade

The student's overall course grade so far, entered as a percentage out of 100.

For example, enter `78` if the current total course grade is 78%.

### Target course grade

The overall grade the student wants to achieve by the end of the course, out of 100.

### Upcoming assessment weight

How much the upcoming exam, assignment, or project contributes to the final course grade.

For example, enter `30` if the assessment is worth 30% of the course total.

### Days remaining

The number of days until the upcoming assessment is due.

### Confidence level

A self-reported value from 1 to 5:

- `1` means very low confidence.
- `3` means moderate confidence.
- `5` means very high confidence.

Lower confidence can increase the course's study priority.

### Course credit hours

The official credit value of the course.

### Available study hours

The total number of hours the student can realistically study during the selected week.

## How the planning process works

Syllabalance uses several stages:

1. It validates the course information entered by the student.
2. It calculates a priority score for each course.
3. It compares urgency, academic impact, grade gap, confidence, and course load.
4. It checks whether the target grade is mathematically reachable through the upcoming assessment.
5. It distributes the available study time across the ranked courses.
6. It converts those allocations into manageable sessions across seven days.
7. It generates plain-language explanations for the recommendations.

The application is intended to support student decisions. Its output is a recommendation, not a guarantee of a particular academic result.

## Main features

### Explainable course ranking

Each recommendation includes a short explanation describing the factors that influenced the course's position.

### Target feasibility analysis

The application calculates the assessment score required to reach the target grade and identifies targets that are currently:

- Within reach
- Challenging
- High risk
- Mathematically impossible through the selected assessment alone

### Assessment what-if calculator

Students can adjust a possible assessment score and immediately see:

- The projected overall course grade
- The change from the current grade
- Whether the selected target would be reached

### Constrained study-hour allocation

Available hours are distributed across competing courses while ensuring that the total recommendation does not exceed the student's stated availability.

### Weekly schedule

The scheduling engine divides allocated time into study sessions across seven days while respecting the selected daily limit.

## Technology

- Python
- Flask
- SciPy
- HTML
- CSS
- JavaScript
- Jinja
- pytest
- Gunicorn

## Project structure

```text
Syllabalance/
├── app.py
├── priority_engine.py
├── schedule_engine.py
├── requirements.txt
├── README.md
├── static/
│   ├── app.js
│   ├── style.css
│   └── what_if.js
├── templates/
│   └── index.html
├── tests/
│   ├── test_priority_engine.py
│   └── test_schedule_engine.py
└── docs/
    └── screenshots/
        ├── planner.png
        ├── results.png
        └── schedule.png
