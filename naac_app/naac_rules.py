# Simple editable NAAC keyword mapping (MVP).
# You can expand metrics & keywords as per your NAAC framework (College/University).

NAAC_MAPPING = {
    "C1": {
        "Curriculum Design and Development": {
            "required": ["curriculum", "syllabus", "program outcomes", "co-po", "bos", "academic council"],
            "optional": ["revision", "feedback", "stakeholders", "industry", "cbcs"]
        },
        "Academic Flexibility": {
            "required": ["elective", "choice based", "credit", "flexibility"],
            "optional": ["interdisciplinary", "online course", "mooc", "nptel"]
        },
    },
    "C2": {
        "Teaching-Learning Process": {
            "required": ["teaching", "learning", "lesson plan", "attendance"],
            "optional": ["innovative", "experiential", "participative", "ict"]
        },
        "Student Performance and Learning Outcomes": {
            "required": ["outcomes", "attainment", "assessment", "result analysis"],
            "optional": ["rubrics", "benchmark", "continuous evaluation"]
        },
    },
    "C3": {
        "Research Publications": {
            "required": ["research", "publication", "journal", "conference"],
            "optional": ["scopus", "wos", "ugc care", "doi", "impact factor"]
        },
        "Innovation and Extension": {
            "required": ["innovation", "extension", "outreach", "community"],
            "optional": ["incubation", "startup", "ipr", "patent"]
        },
    },
    "C4": {
        "Infrastructure and Learning Resources": {
            "required": ["infrastructure", "laboratory", "library", "ict facilities"],
            "optional": ["smart classroom", "wifi", "e-resources", "lms"]
        },
    },
    "C5": {
        "Student Support": {
            "required": ["scholarship", "mentoring", "counselling", "support"],
            "optional": ["placement", "career guidance", "competitive exams"]
        },
        "Student Progression": {
            "required": ["progression", "higher education", "placement statistics"],
            "optional": ["alumni", "entrepreneurship", "self-employment"]
        },
    },
    "C6": {
        "Governance and Leadership": {
            "required": ["governance", "leadership", "strategy", "planning"],
            "optional": ["iqac", "organogram", "stakeholder participation"]
        },
        "Financial Management": {
            "required": ["budget", "audit", "utilization", "financial"],
            "optional": ["internal audit", "external audit", "procurement"]
        },
    },
    "C7": {
        "Institutional Values and Best Practices": {
            "required": ["values", "best practices", "green campus", "gender", "environment"],
            "optional": ["energy conservation", "waste management", "inclusive"]
        },
    }
}