document.addEventListener("DOMContentLoaded", function () {
    const welcomeScreen =
        document.getElementById("welcome-screen");

    const plannerApp =
        document.getElementById("planner-app");

    const profileForm =
        document.getElementById("profile-form");

    const studentNameInput =
        document.getElementById("student-name");

    const displayName =
        document.getElementById("display-name");

    const changeProfileButton =
        document.getElementById("change-profile");

    const dailyQuote =
        document.getElementById("daily-quote");

    const modeLabel =
        document.getElementById("mode-label");

    const courseList =
        document.getElementById("course-list");

    const addCourseButton =
        document.getElementById("add-course");


    const quotes = {
        stoic: [
            "Focus on the next action. The rest can wait.",
            "You do not need control over everything—only your response.",
            "A difficult task becomes smaller each time you return to it.",
            "Do what the day requires, one deliberate step at a time.",
            "Your attention is yours. Place it where it matters.",
            "Discipline is choosing what matters beyond the present moment.",
            "Progress begins when you stop negotiating with the first step."
        ],

        gentle: [
            "A slower day can still move your life forward.",
            "You are allowed to learn without punishing yourself.",
            "Small progress still counts, especially on difficult days.",
            "Begin with what feels possible, then continue from there.",
            "Your best effort does not have to look the same every day.",
            "Rest and progress can belong in the same plan.",
            "Speak to yourself like someone you genuinely want to succeed."
        ],

        driven: [
            "The work you complete today gives tomorrow more options.",
            "Make the goal smaller, then make the effort undeniable.",
            "Momentum begins with one task finished properly.",
            "You are building evidence that you can rely on yourself.",
            "Ambition becomes real when it reaches your calendar.",
            "Start before you feel completely ready.",
            "Your future deserves more than good intentions."
        ]
    };


    function getSavedProfile() {
        try {
            return {
                name: localStorage.getItem(
                    "syllabalanceName"
                ),

                mode:
                    localStorage.getItem(
                        "syllabalanceMode"
                    ) || "stoic"
            };
        } catch (error) {
            return {
                name: null,
                mode: "stoic"
            };
        }
    }


    function saveProfile(name, mode) {
        try {
            localStorage.setItem(
                "syllabalanceName",
                name
            );

            localStorage.setItem(
                "syllabalanceMode",
                mode
            );
        } catch (error) {
            console.log(
                "Browser storage is unavailable."
            );
        }
    }


    function getDailyQuote(mode) {
        const modeQuotes =
            quotes[mode] || quotes.stoic;

        const today = new Date();

        const dateNumber = Math.floor(
            new Date(
                today.getFullYear(),
                today.getMonth(),
                today.getDate()
            ).getTime() / 86400000
        );

        const quoteIndex =
            dateNumber % modeQuotes.length;

        return modeQuotes[quoteIndex];
    }


    function formatModeName(mode) {
        return (
            mode.charAt(0).toUpperCase()
            + mode.slice(1)
            + " mode"
        );
    }


    function showPlanner(name, mode) {
        displayName.textContent = name;

        dailyQuote.textContent =
            getDailyQuote(mode);

        modeLabel.textContent =
            formatModeName(mode);

        welcomeScreen.classList.add("hidden");
        plannerApp.classList.remove("hidden");
    }


    function showWelcome(name, mode) {
        if (name) {
            studentNameInput.value = name;
        }

        const selectedMode =
            document.querySelector(
                `input[name="motivation-mode"][value="${mode}"]`
            );

        if (selectedMode) {
            selectedMode.checked = true;
        }

        plannerApp.classList.add("hidden");
        welcomeScreen.classList.remove("hidden");

        studentNameInput.focus();
    }


    profileForm.addEventListener(
        "submit",
        function (event) {
            event.preventDefault();

            const name =
                studentNameInput.value.trim();

            const selectedModeInput =
                document.querySelector(
                    'input[name="motivation-mode"]:checked'
                );

            if (!name || !selectedModeInput) {
                return;
            }

            const selectedMode =
                selectedModeInput.value;

            saveProfile(name, selectedMode);
            showPlanner(name, selectedMode);
        }
    );


    changeProfileButton.addEventListener(
        "click",
        function () {
            const profile = getSavedProfile();

            showWelcome(
                profile.name,
                profile.mode
            );
        }
    );


    /*
        Course controls only exist on the planning page.
        They are not loaded on the results page.
    */

    if (courseList && addCourseButton) {
        function updateCourseNumbers() {
            const courses =
                courseList.querySelectorAll(
                    ".course-entry"
                );

            courses.forEach(
                function (course, index) {
                    const legend =
                        course.querySelector("legend");

                    legend.textContent =
                        `Course ${index + 1}`;
                }
            );
        }


        addCourseButton.addEventListener(
            "click",
            function () {
                const currentCourses =
                    courseList.querySelectorAll(
                        ".course-entry"
                    );

                if (currentCourses.length >= 8) {
                    alert(
                        "You can add up to 8 courses."
                    );

                    return;
                }

                const newCourse =
                    currentCourses[0].cloneNode(true);

                newCourse
                    .querySelectorAll("input")
                    .forEach(function (input) {
                        input.value = "";
                    });

                const oldRemoveButton =
                    newCourse.querySelector(
                        ".remove-course"
                    );

                if (oldRemoveButton) {
                    oldRemoveButton.remove();
                }

                const removeButton =
                    document.createElement("button");

                removeButton.type = "button";

                removeButton.className =
                    "remove-course";

                removeButton.textContent =
                    "Remove course";

                removeButton.addEventListener(
                    "click",
                    function () {
                        newCourse.remove();
                        updateCourseNumbers();
                    }
                );

                newCourse.appendChild(removeButton);
                courseList.appendChild(newCourse);

                updateCourseNumbers();

                newCourse.scrollIntoView({
                    behavior: "smooth",
                    block: "center"
                });

                const courseNameInput =
                    newCourse.querySelector(
                        'input[name="course_name"]'
                    );

                if (courseNameInput) {
                    courseNameInput.focus();
                }
            }
        );
    }


    const savedProfile = getSavedProfile();

    if (savedProfile.name) {
        showPlanner(
            savedProfile.name,
            savedProfile.mode
        );
    } else {
        showWelcome(
            "",
            savedProfile.mode
        );
    }
});