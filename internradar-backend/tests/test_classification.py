"""Tests for internship classification."""

import pytest

from app.classification.internship_classifier import InternshipClassifier
from app.models.internship import InternshipCreate


def make_internship(title: str, description: str = "", skills: list[str] | None = None) -> InternshipCreate:
    return InternshipCreate(
        external_id="test-1",
        source="greenhouse",
        company="Example",
        title=title,
        location="Bangalore, India",
        remote=False,
        url="https://example.com",
        description=description,
        skills=skills or [],
    )


classifier = InternshipClassifier()


class TestClassifier:
    def test_machine_learning(self):
        assert classifier.classify(make_internship("Machine Learning Intern")) == "Machine Learning"

    def test_deep_learning(self):
        assert classifier.classify(make_internship("Deep Learning Research Intern")) == "Machine Learning"

    def test_nlp(self):
        assert classifier.classify(make_internship("NLP Engineer Intern")) == "Machine Learning"

    def test_generative_ai(self):
        assert classifier.classify(make_internship("Generative AI Intern")) == "Machine Learning"

    def test_data_science(self):
        assert classifier.classify(make_internship("Data Scientist Intern")) == "Data Science"

    def test_data_analytics(self):
        assert classifier.classify(make_internship("Data Analyst Intern")) == "Data Analytics"

    def test_sql_analytics(self):
        assert classifier.classify(make_internship("Business Intelligence Intern", skills=["SQL", "Tableau"])) == "Data Analytics"

    def test_cybersecurity(self):
        assert classifier.classify(make_internship("Cybersecurity Intern – Threat Analysis")) == "Cybersecurity"

    def test_embedded(self):
        assert classifier.classify(make_internship("Embedded Software Intern")) == "Embedded & Hardware"

    def test_vlsi(self):
        assert classifier.classify(make_internship("VLSI Design Intern")) == "Embedded & Hardware"

    def test_cloud_devops(self):
        assert classifier.classify(make_internship("Cloud Infrastructure Intern")) == "Cloud & DevOps"

    def test_kubernetes(self):
        assert classifier.classify(make_internship("DevOps Intern", skills=["Kubernetes", "Docker"])) == "Cloud & DevOps"

    def test_mobile_android(self):
        assert classifier.classify(make_internship("Android Developer Intern")) == "Mobile Development"

    def test_mobile_flutter(self):
        assert classifier.classify(make_internship("Flutter Intern")) == "Mobile Development"

    def test_uiux(self):
        assert classifier.classify(make_internship("UI/UX Design Intern")) == "UI/UX"

    def test_uiux_figma(self):
        assert classifier.classify(make_internship("Product Design Intern", skills=["Figma"])) == "UI/UX"

    def test_research(self):
        assert classifier.classify(make_internship("Research Intern – NLP Lab")) == "Machine Learning"

    def test_software_engineering(self):
        assert classifier.classify(make_internship("Software Engineering Intern")) == "Software Engineering"

    def test_backend(self):
        assert classifier.classify(make_internship("Backend Developer Intern")) == "Software Engineering"

    def test_product(self):
        assert classifier.classify(make_internship("Product Management Intern")) == "Product"

    def test_finance(self):
        assert classifier.classify(make_internship("Finance Intern – Investment Banking")) == "Finance"

    def test_marketing(self):
        assert classifier.classify(make_internship("Digital Marketing Intern")) == "Marketing"

    def test_operations(self):
        assert classifier.classify(make_internship("Supply Chain Operations Intern")) == "Operations"

    def test_hr(self):
        assert classifier.classify(make_internship("HR Talent Acquisition Intern")) == "Human Resources"

    def test_content(self):
        assert classifier.classify(make_internship("Content Writing Intern")) == "Content & Writing"

    def test_other_fallback(self):
        assert classifier.classify(make_internship("Administrative Intern")) == "Other"

    def test_ml_wins_over_software_engineering(self):
        # "ML Infrastructure Engineer Intern" has both ML and software keywords
        result = classifier.classify(make_internship("ML Infrastructure Engineer Intern"))
        assert result == "Machine Learning"
