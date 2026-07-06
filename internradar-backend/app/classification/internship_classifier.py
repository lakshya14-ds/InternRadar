"""Rule-based internship classification."""

from app.models.internship import InternshipCreate


class InternshipClassifier:
    """Keyword-based classifier for internship categories.

    Categories are ordered from most-specific to least-specific so that a
    role like "ML Infrastructure Engineer Intern" is tagged as
    "Machine Learning" rather than "Software Engineering".
    """

    CATEGORY_KEYWORDS: dict[str, tuple[str, ...]] = {
        # ── Highly specific / technical ──────────────────────────────────────
        "AI": (
            " ai ",
            "artificial intelligence",
            "llm",
            "generative ai",
            "gen ai",
            "openai",
            "anthropic",
            "langchain",
            "rag ",
            "prompt engineer",
            "agentic",
            "copilot",
        ),
        "Machine Learning": (
            "machine learning",
            "ml",
            "deep learning",
            "artificial intelligence",
            "computer vision",
            "nlp",
            "natural language processing",
            "llm",
            "generative ai",
            "gen ai",
            "reinforcement learning",
            "neural network",
        ),
        "Data Science": (
            "data scientist",
            "data science",
            "statistics",
            "statistical",
            "experiment",
            "modeling",
            "predictive",
            "forecasting",
        ),
        "Data Analytics": (
            "data analyst",
            "analytics",
            "sql",
            "dashboard",
            "business intelligence",
            "bi ",
            "tableau",
            "power bi",
            "looker",
            "excel",
            "reporting",
        ),
        "Cybersecurity": (
            "security",
            "cyber",
            "threat",
            "vulnerability",
            "penetration",
            "soc",
            "siem",
            "ethical hack",
            "infosec",
            "cryptography",
        ),
        "Embedded & Hardware": (
            "embedded",
            "firmware",
            "rtos",
            "fpga",
            "vhdl",
            "verilog",
            "hardware",
            "iot",
            "microcontroller",
            "pcb",
            "vlsi",
            "semiconductor",
            "rtl",
            "asic",
            "analog",
            "digital design",
        ),
        "Cloud & DevOps": (
            "cloud",
            "devops",
            "kubernetes",
            "docker",
            "aws",
            "azure",
            "gcp",
            "infrastructure",
            "site reliability",
            "sre",
            "ci/cd",
            "terraform",
            "ansible",
        ),
        "Mobile Development": (
            "android",
            "ios",
            "flutter",
            "react native",
            "mobile",
            "swift",
            "kotlin",
        ),
        "Human Resources": (
            "human resources",
            "hr intern",
            "hr ",
            "talent acquisition",
            "talent management",
            "recruitment",
            "people operations",
        ),
        "UI/UX": (
            "ui/ux",
            "ux design",
            "ui design",
            "user experience",
            "user interface",
            "figma",
            "product design",
            "interaction design",
            "visual design",
            "graphic design",
            "design intern",
        ),
        "Research": (
            "research",
            "researcher",
            "scientist",
            "lab",
            "phd",
            "thesis",
            "publication",
            "academic",
        ),
        # ── Broader technical ─────────────────────────────────────────────────
        "Software Engineering": (
            "software",
            "backend",
            "front-end",
            "frontend",
            "full stack",
            "fullstack",
            "developer",
            "engineer",
            "python",
            "java",
            "golang",
            "rust",
            "c++",
            "scala",
            "typescript",
            "react",
            "node",
            "django",
            "spring",
            "api",
            "web",
        ),
        # ── Business / domain ─────────────────────────────────────────────────
        "Product": (
            "product manager",
            "product management",
            "product intern",
            "growth",
            "product analyst",
        ),
        "Business Analytics": (
            "business analyst",
            "strategy",
            "market analysis",
            "market research",
            "competitive intelligence",
        ),
        "Finance": (
            "finance",
            "fintech",
            "investment",
            "banking",
            "equity",
            "risk",
            "quant",
            "treasury",
            "accounting",
            "ca ",
            "chartered accountant",
            "financial",
        ),
        "Marketing": (
            "marketing",
            "digital marketing",
            "seo",
            "sem",
            "content marketing",
            "brand",
            "social media",
            "growth marketing",
            "performance marketing",
        ),
        "Operations": (
            "operations",
            "supply chain",
            "logistics",
            "program coordinator",
            "program management",
            "project management",
            "process",
            "procurement",
        ),

        "Legal & Compliance": (
            "legal",
            "compliance",
            "policy",
            "regulatory",
            "law",
            "advocate",
        ),
        "Content & Writing": (
            "content",
            "writing",
            "copywriting",
            "technical writer",
            "editor",
            "journalism",
            "communication",
        ),
    }

    def classify(self, internship: InternshipCreate) -> str:
        """Classify an internship using title, description, skills, and tags.

        Evaluation order matters: more-specific categories are listed first in
        CATEGORY_KEYWORDS so they win over broader buckets like
        "Software Engineering".
        """

        haystack = " " + " ".join(
            [
                internship.title,
                internship.description,
                " ".join(internship.skills),
                " ".join(internship.tags),
            ]
        ).casefold() + " "

        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if any(keyword in haystack for keyword in keywords):
                return category

        return "Other"
