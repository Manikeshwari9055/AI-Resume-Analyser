// =====================================
// BACKEND URL
// =====================================

const API_BASE_URL = "https://ai-resume-analyser-backend-bskv.onrender.com";


// =====================================
// SCREEN NAVIGATION
// =====================================

function showScreen(screenId) {

    const screens = [
        "welcomeScreen",
        "registerScreen",
        "loginScreen",
        "dashboardScreen"
    ];

    screens.forEach(function(id) {

        const screen = document.getElementById(id);

        if (screen) {
            screen.style.display = "none";
        }

    });

    const selectedScreen = document.getElementById(screenId);

    if (selectedScreen) {

        if (screenId === "dashboardScreen") {
            selectedScreen.style.display = "block";
        } else {
            selectedScreen.style.display = "flex";
        }

    }

    const footer = document.querySelector("footer");

    if (footer) {
        footer.style.display =
            screenId === "dashboardScreen" ? "block" : "none";
    }
}


// =====================================
// GLOBAL VARIABLES
// =====================================

let uploadedResumeSkills = [];
let uploadedResumeText = "";
let latestAnalysis = null;


// =====================================
// RESUME UPLOAD AND ANALYSIS
// =====================================

async function uploadResume() {

    const loadingMessage = document.getElementById("loadingMessage");
    const uploadButton = document.getElementById("uploadButton");
    const fileInput = document.getElementById("resume");
    const status = document.getElementById("status");

    if (!fileInput || !fileInput.files.length) {
        if (status) status.innerText = "Please select a PDF resume!";
        return;
    }

    const file = fileInput.files[0];

    if (!file.name.toLowerCase().endsWith(".pdf")) {
        if (status) status.innerText = "Please upload a PDF file!";
        return;
    }

    const token = sessionStorage.getItem("authToken");

    if (!token) {
        if (status) status.innerText = "Please log in first!";
        return;
    }

    if (loadingMessage) loadingMessage.style.display = "block";

    if (uploadButton) {
        uploadButton.disabled = true;
        uploadButton.innerText = "Analysing...";
    }

    const formData = new FormData();
    formData.append("resume", file);

    if (status) status.innerText = "Analyzing resume...";

    try {

        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`
            },
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Resume upload failed!");
        }

        uploadedResumeSkills = data.skills || [];
        uploadedResumeText = data.resume_text || "";
        latestAnalysis = data;

        if (status) {
            status.innerText = data.message || "Analysis completed!";
        }

        // Resume score
        const scoreElement = document.getElementById("score");

        if (scoreElement) {
            scoreElement.innerText = data.score + "%";
        }

        // Total skills
        const totalSkills = document.getElementById("totalSkills");

        if (totalSkills) {
            totalSkills.innerText = uploadedResumeSkills.length;
        }

        // Missing skills
        const missingContainer = document.getElementById("missing");

        if (missingContainer) {

            missingContainer.innerHTML = "";

            (data.missing_skills || []).forEach(function(skill) {

                const skillItem = document.createElement("p");
                skillItem.innerText = skill;

                missingContainer.appendChild(skillItem);

            });
        }

        // Total missing skills
        const totalMissing = document.getElementById("totalMissing");

        if (totalMissing) {
            totalMissing.innerText = (data.missing_skills || []).length;
        }

        // Summary score
        const summaryScore = document.getElementById("summaryScore");
        const scoreProgress = document.getElementById("scoreProgress");

        if (scoreProgress) {
            scoreProgress.style.width = data.score + "%";
        }

        if (summaryScore) {
            summaryScore.innerText = data.score + "%";
        }

        // Detected skills
        const skillsContainer = document.getElementById("skills");

        if (skillsContainer) {

            skillsContainer.innerHTML = "";

            uploadedResumeSkills.forEach(function(skill) {

                const skillItem = document.createElement("p");
                skillItem.innerText = skill;

                skillsContainer.appendChild(skillItem);

            });
        }

        // Skill recommendations
        const suggestionsContainer = document.getElementById("suggestions");

        if (suggestionsContainer) {

            suggestionsContainer.innerHTML = "";

            const missingSkills = data.missing_skills || [];

            const recommendations = {
                "Python": "Learn Python basics, functions and OOP.",
                "Java": "Learn Java fundamentals and OOP concepts.",
                "SQL": "Practice SQL queries, joins and database concepts.",
                "HTML": "Learn HTML elements and forms.",
                "CSS": "Practice CSS layouts, Flexbox and Grid.",
                "JavaScript": "Learn JavaScript DOM and events.",
                "React": "Learn React components, props and state.",
                "Machine Learning": "Study regression, classification and model evaluation.",
                "Data Science": "Learn Pandas, NumPy and data visualization.",
                "Flask": "Build Python web applications using Flask.",
                "C": "Practice C programming and pointers.",
                "C++": "Learn C++ OOP and STL."
            };

            if (missingSkills.length === 0) {

                const message = document.createElement("p");
                message.innerText = "Great! All listed skills were detected.";

                suggestionsContainer.appendChild(message);

            } else {

                missingSkills.forEach(function(skill) {

                    const item = document.createElement("p");

                    item.innerText =
                        skill + ": " +
                        (recommendations[skill] || "Explore this skill.");

                    suggestionsContainer.appendChild(item);

                });
            }
        }

        // Job recommendations
        displayJobRoles(uploadedResumeSkills);

    } catch (error) {

        console.error("Upload error:", error);

        if (status) {
            status.innerText = "Error: " + error.message;
        }

    } finally {

        if (loadingMessage) {
            loadingMessage.style.display = "none";
        }

        if (uploadButton) {
            uploadButton.disabled = false;
            uploadButton.innerText = "Upload & Analyse";
        }
    }
}


// =====================================
// JOB ROLE RECOMMENDATIONS
// =====================================

function displayJobRoles(skills) {

    const jobsContainer = document.getElementById("jobs");

    if (!jobsContainer) return;

    jobsContainer.innerHTML = "";

    const jobRoles = [

        {
            name: "Python Developer",
            required: ["Python", "SQL", "Flask"]
        },

        {
            name: "Java Developer",
            required: ["Java", "SQL"]
        },

        {
            name: "Frontend Developer",
            required: ["HTML", "CSS", "JavaScript", "React"]
        },

        {
            name: "Data Scientist",
            required: ["Python", "SQL", "Machine Learning", "Data Science"]
        },

        {
            name: "Machine Learning Engineer",
            required: ["Python", "Machine Learning", "Data Science"]
        }

    ];

    jobRoles.forEach(function(job) {

        const matched = job.required.filter(function(skill) {
            return skills.includes(skill);
        });

        const percentage = Math.round(
            (matched.length / job.required.length) * 100
        );

        const item = document.createElement("p");

        item.innerText =
            job.name + " - " + percentage + "% skill match";

        jobsContainer.appendChild(item);

    });
}


// =====================================
// JOB DESCRIPTION MATCHING
// =====================================

function matchJobDescription() {

    const descriptionElement = document.getElementById("jobDescription");
    const resultElement = document.getElementById("jobMatchResult");

    if (!descriptionElement || !resultElement) {
        console.error("Job description HTML elements not found.");
        return;
    }

    const description = descriptionElement.value.toLowerCase();

    if (!description.trim()) {
        resultElement.innerText = "Please enter a job description.";
        return;
    }

    const matchedSkills = uploadedResumeSkills.filter(function(skill) {
        return description.includes(skill.toLowerCase());
    });

    resultElement.innerText =
        "Matching skills: " +
        (matchedSkills.length ? matchedSkills.join(", ") : "None") +
        "\nTotal matching skills: " + matchedSkills.length;
}


// =====================================
// USER REGISTRATION
// =====================================

async function registerUser() {

    const username = document.getElementById("registerUsername").value.trim();
    const password = document.getElementById("registerPassword").value;
    const status = document.getElementById("registerStatus");

    if (!username || !password) {
        if (status) {
            status.innerText = "Please enter username and password.";
        }
        return;
    }

    try {

        const response = await fetch(`${API_BASE_URL}/register`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        });

        const data = await response.json();

        if (status) {
            status.innerText = data.message || data.error;
        }

        if (response.ok) {
            document.getElementById("registerPassword").value = "";
        }

    } catch (error) {

        console.error("Registration error:", error);

        if (status) {
            status.innerText = "Error connecting to server!";
        }

    }
}


// =====================================
// USER LOGIN
// =====================================

async function loginUser() {

    const username = document.getElementById("loginUsername").value.trim();
    const password = document.getElementById("loginPassword").value;
    const status = document.getElementById("loginStatus");

    if (!username || !password) {
        if (status) {
            status.innerText = "Please enter username and password.";
        }
        return;
    }

    try {

        const response = await fetch(`${API_BASE_URL}/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || data.error || "Login failed!");
        }

        if (!data.token) {
            throw new Error("Server did not return a login token.");
        }

        // Save authentication token
        sessionStorage.setItem("authToken", data.token);

        if (status) {
            status.innerText = data.message || "Login successful!";
        }

        const welcomeMessage = document.getElementById("welcomeMessage");
        const profileUsername = document.getElementById("profileUsername");
        const profileStatus = document.getElementById("profileStatus");

        if (welcomeMessage) {
            welcomeMessage.innerText = "Welcome, " + data.username + "!";
        }

        if (profileUsername) {
            profileUsername.innerText = data.username;
        }

        if (profileStatus) {
            profileStatus.innerText = "Logged in";
        }

        // Open dashboard after successful login
        showScreen("dashboardScreen");

    } catch (error) {

        console.error("Login error:", error);

        if (status) {
            status.innerText = "Error: " + error.message;
        }

    }
}


// =====================================
// USER LOGOUT
// =====================================

async function logoutUser() {

    const status = document.getElementById("logoutStatus");

    // Remove saved login token
    sessionStorage.removeItem("authToken");

    if (status) {
        status.innerText = "Logged out successfully!";
    }

    const welcomeMessage = document.getElementById("welcomeMessage");
    const profileUsername = document.getElementById("profileUsername");
    const profileStatus = document.getElementById("profileStatus");

    if (welcomeMessage) {
        welcomeMessage.innerText = "";
    }

    if (profileUsername) {
        profileUsername.innerText = "Not logged in";
    }

    if (profileStatus) {
        profileStatus.innerText = "Logged out";
    }

    // Return to login screen
    showScreen("loginScreen");
}


// =====================================
// PROFILE TOGGLE
// =====================================

function toggleProfile() {

    const profile = document.getElementById("profileCard");

    if (!profile) return;

    if (profile.style.display === "none") {
        profile.style.display = "block";
    } else {
        profile.style.display = "none";
    }
}


// =====================================
// DOWNLOAD PDF REPORT
// =====================================

function downloadReport() {

    if (!latestAnalysis) {
        alert("Please analyze a resume first!");
        return;
    }

    if (!window.jspdf) {
        alert("PDF report library is not loaded!");
        return;
    }

    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();

    doc.setFontSize(20);
    doc.text("AI Resume Analysis Report", 20, 20);

    doc.setFontSize(12);

    doc.text(
        "Resume Score: " + latestAnalysis.score + "%",
        20,
        35
    );

    doc.text("Skills Found:", 20, 50);

    let y = 60;

    uploadedResumeSkills.forEach(function(skill) {

        if (y > 270) {
            doc.addPage();
            y = 20;
        }

        doc.text("- " + skill, 25, y);
        y += 8;

    });

    y += 8;

    doc.text("Missing Skills:", 20, y);
    y += 10;

    (latestAnalysis.missing_skills || []).forEach(function(skill) {

        if (y > 270) {
            doc.addPage();
            y = 20;
        }

        doc.text("- " + skill, 25, y);
        y += 8;

    });

    doc.save("Resume_Analysis_Report.pdf");

}


// =====================================
// INITIAL SCREEN
// =====================================

document.addEventListener("DOMContentLoaded", function() {

    showScreen("welcomeScreen");

});