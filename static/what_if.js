document.addEventListener("DOMContentLoaded", () => {
    const simulator = document.getElementById(
        "what-if-simulator"
    );

    if (!simulator) {
        return;
    }

    const courseSelect = document.getElementById(
        "simulation-course"
    );

    const scoreInput = document.getElementById(
        "simulation-score"
    );

    const scoreOutput = document.getElementById(
        "simulation-score-output"
    );

    const projectedGradeOutput = document.getElementById(
        "projected-grade"
    );

    const gradeChangeOutput = document.getElementById(
        "projected-change"
    );

    const targetStatusOutput = document.getElementById(
        "projected-target-status"
    );

    const requiredScoreOutput = document.getElementById(
        "simulation-required-score"
    );

    const courseDataElements = document.querySelectorAll(
        "[data-simulation-course]"
    );

    const courses = Array.from(
        courseDataElements
    ).map((element) => {
        return {
            name: element.dataset.name,
            currentGrade: Number(
                element.dataset.currentGrade
            ),
            targetGrade: Number(
                element.dataset.targetGrade
            ),
            assessmentWeight: Number(
                element.dataset.assessmentWeight
            )
        };
    });

    function calculateProjectedGrade(
        currentGrade,
        assessmentWeight,
        assessmentScore
    ) {
        const completedWeight =
            100 - assessmentWeight;

        const currentContribution =
            currentGrade * (completedWeight / 100);

        const assessmentContribution =
            assessmentScore * (assessmentWeight / 100);

        return (
            currentContribution +
            assessmentContribution
        );
    }

    function calculateRequiredScore(
        currentGrade,
        targetGrade,
        assessmentWeight
    ) {
        if (assessmentWeight <= 0) {
            return null;
        }

        const completedWeight =
            100 - assessmentWeight;

        const currentContribution =
            currentGrade * (completedWeight / 100);

        return (
            (targetGrade - currentContribution) /
            (assessmentWeight / 100)
        );
    }

    function formatChange(change) {
        if (Math.abs(change) < 0.05) {
            return "No meaningful change";
        }

        const sign = change > 0 ? "+" : "";

        return (
            sign +
            change.toFixed(1) +
            " percentage points"
        );
    }

    function updateSimulator() {
        const selectedIndex = Number(
            courseSelect.value
        );

        const selectedCourse =
            courses[selectedIndex];

        if (!selectedCourse) {
            return;
        }

        let assessmentScore = Number(
            scoreInput.value
        );

        if (!Number.isFinite(assessmentScore)) {
            assessmentScore = 0;
        }

        assessmentScore = Math.min(
            100,
            Math.max(0, assessmentScore)
        );

        scoreInput.value = assessmentScore;

        const projectedGrade =
            calculateProjectedGrade(
                selectedCourse.currentGrade,
                selectedCourse.assessmentWeight,
                assessmentScore
            );

        const gradeChange =
            projectedGrade -
            selectedCourse.currentGrade;

        const requiredScore =
            calculateRequiredScore(
                selectedCourse.currentGrade,
                selectedCourse.targetGrade,
                selectedCourse.assessmentWeight
            );

        scoreOutput.textContent =
            assessmentScore.toFixed(0) + "%";

        projectedGradeOutput.textContent =
            projectedGrade.toFixed(1) + "%";

        gradeChangeOutput.textContent =
            formatChange(gradeChange);

        if (requiredScore === null) {
            requiredScoreOutput.textContent =
                "Not available";
        } else if (requiredScore > 100) {
            requiredScoreOutput.textContent =
                requiredScore.toFixed(1) +
                "% — currently impossible";
        } else if (requiredScore <= 0) {
            requiredScoreOutput.textContent =
                "Target already secured";
        } else {
            requiredScoreOutput.textContent =
                requiredScore.toFixed(1) + "%";
        }

        if (
            projectedGrade >=
            selectedCourse.targetGrade
        ) {
            targetStatusOutput.textContent =
                "This score reaches the target of " +
                selectedCourse.targetGrade.toFixed(1) +
                "%.";

            targetStatusOutput.className =
                "simulation-status target-reached";
        } else {
            const shortfall =
                selectedCourse.targetGrade -
                projectedGrade;

            targetStatusOutput.textContent =
                "This result remains " +
                shortfall.toFixed(1) +
                " points below the target.";

            targetStatusOutput.className =
                "simulation-status target-missed";
        }
    }

    courses.forEach((course, index) => {
        const option =
            document.createElement("option");

        option.value = index;
        option.textContent = course.name;

        courseSelect.appendChild(option);
    });

    courseSelect.addEventListener(
        "change",
        updateSimulator
    );

    scoreInput.addEventListener(
        "input",
        updateSimulator
    );

    updateSimulator();
});