"""Tests for BaseConnector filters: is_internship and is_india_location."""

import pytest

from app.connectors.lever_connector import LeverConnector


@pytest.fixture()
def connector() -> LeverConnector:
    return LeverConnector(company_slugs=[])


# ── Phase 1: title must contain an internship keyword ────────────────────────

class TestPhase1TitleInclusion:
    def test_intern_keyword(self, connector):
        assert connector.is_internship("Software Engineering Intern")

    def test_internship_keyword(self, connector):
        assert connector.is_internship("Summer Internship – Data Science")

    def test_trainee_keyword(self, connector):
        assert connector.is_internship("Graduate Trainee – Product")

    def test_apprentice_keyword(self, connector):
        assert connector.is_internship("Apprentice Engineer")

    def test_rejects_no_internship_keyword_in_title(self, connector):
        assert not connector.is_internship("Treasury Operations")

    def test_rejects_empty_title(self, connector):
        assert not connector.is_internship("")

    def test_rejects_regular_role_title(self, connector):
        assert not connector.is_internship("Data Analyst", "We are building an intern-facing product")


# ── Phase 2: title must NOT contain seniority signals ────────────────────────

class TestPhase2TitleExclusion:
    def test_rejects_senior_engineer(self, connector):
        assert not connector.is_internship("Senior Software Engineer")

    def test_rejects_senior_manager(self, connector):
        assert not connector.is_internship("Senior Manager – Treasury Operations")

    def test_rejects_manager(self, connector):
        assert not connector.is_internship("Engineering Manager")

    def test_rejects_director(self, connector):
        assert not connector.is_internship("Director of Engineering")

    def test_rejects_principal(self, connector):
        assert not connector.is_internship("Principal Software Engineer")

    def test_rejects_staff(self, connector):
        assert not connector.is_internship("Staff Engineer")

    def test_rejects_lead(self, connector):
        assert not connector.is_internship("Lead Data Scientist")

    def test_rejects_full_time(self, connector):
        assert not connector.is_internship("Full-Time Backend Developer")

    def test_rejects_contract(self, connector):
        assert not connector.is_internship("Contract Python Developer")

    def test_rejects_part_time(self, connector):
        assert not connector.is_internship("Part-Time Data Analyst")

    def test_rejects_intern_substring_in_senior_title(self, connector):
        # "internal" contains "intern" — must not match
        assert not connector.is_internship("Senior Internal Tools Engineer")

    def test_rejects_vp(self, connector):
        assert not connector.is_internship("VP of Engineering")

    def test_rejects_consultant(self, connector):
        assert not connector.is_internship("Consultant – Supply Chain")

    def test_rejects_architect(self, connector):
        assert not connector.is_internship("Solutions Architect")


# ── Phase 3: description must NOT contain experienced-hire signals ────────────

class TestPhase3DescriptionExclusion:

    # ── The exact Paytm case from the screenshot ─────────────────────────────
    def test_rejects_paytm_treasury_operations_case(self, connector):
        """Exact scenario from the reported bug — must be rejected."""
        title = "Treasury Operations"
        description = (
            "Senior Manager – Treasury Operations "
            "EXPERIENCE 7 – 10 Years "
            "QUALIFICATION CA / MBA (Finance) "
            "LOCATION Noida, India"
        )
        assert not connector.is_internship(title, description)

    def test_rejects_7_to_10_years_experience(self, connector):
        assert not connector.is_internship(
            "Data Intern",
            "EXPERIENCE 7 – 10 Years of relevant work experience required."
        )

    def test_rejects_2_plus_years(self, connector):
        assert not connector.is_internship(
            "Software Intern",
            "Minimum 2+ years of experience in backend development."
        )

    def test_rejects_3_years_experience(self, connector):
        assert not connector.is_internship(
            "Business Trainee",
            "You must have 3 years of experience in finance."
        )

    def test_rejects_5_years_minimum(self, connector):
        assert not connector.is_internship(
            "Operations Intern",
            "Minimum 5 years in supply chain management required."
        )

    def test_rejects_at_least_4_years(self, connector):
        assert not connector.is_internship(
            "Product Intern",
            "At least 4 years of product management experience."
        )

    def test_rejects_ca_mba_qualification(self, connector):
        assert not connector.is_internship(
            "Finance Trainee",
            "QUALIFICATION CA / MBA (Finance) with relevant experience."
        )

    def test_rejects_ctc_salary_line(self, connector):
        assert not connector.is_internship(
            "Analyst Intern",
            "CTC: 15 LPA. We are looking for an experienced professional."
        )

    def test_rejects_senior_manager_in_description(self, connector):
        assert not connector.is_internship(
            "Operations Trainee",
            "This role reports to the Senior Manager and requires deep expertise."
        )

    # ── Should still PASS (0–1 yr or fresher-friendly descriptions) ──────────

    def test_allows_0_to_1_year_experience(self, connector):
        assert connector.is_internship(
            "Software Engineering Intern",
            "0 to 1 year of experience. Freshers welcome."
        )

    def test_allows_fresher_description(self, connector):
        assert connector.is_internship(
            "Data Science Intern",
            "No prior experience required. Open to final year students."
        )

    def test_allows_1_year_experience(self, connector):
        assert connector.is_internship(
            "ML Intern",
            "0-1 years of experience preferred."
        )

    def test_allows_description_mentioning_senior_team_member(self, connector):
        # Mentioning a senior person in context is fine — it's "Senior Manager" as
        # a job title in the description that we block
        assert connector.is_internship(
            "Product Intern",
            "You will work alongside our product team and learn from experienced engineers."
        )

    def test_allows_standard_internship_description(self, connector):
        assert connector.is_internship(
            "Backend Engineering Intern",
            "We are looking for a motivated intern to join our engineering team. "
            "This is a 6-month paid internship. No prior experience needed."
        )


# ── is_india_location ─────────────────────────────────────────────────────────

class TestIsIndiaLocation:
    def test_bangalore(self, connector):
        assert connector.is_india_location("Bangalore")

    def test_bengaluru_variant(self, connector):
        assert connector.is_india_location("Bengaluru, Karnataka")

    def test_mumbai(self, connector):
        assert connector.is_india_location("Mumbai, Maharashtra, India")

    def test_delhi(self, connector):
        assert connector.is_india_location("New Delhi")

    def test_ncr(self, connector):
        assert connector.is_india_location("NCR")

    def test_gurugram(self, connector):
        assert connector.is_india_location("Gurugram")

    def test_gurgaon_alias(self, connector):
        assert connector.is_india_location("Gurgaon")

    def test_noida(self, connector):
        assert connector.is_india_location("Noida, Uttar Pradesh")

    def test_hyderabad(self, connector):
        assert connector.is_india_location("Hyderabad, Telangana")

    def test_pune(self, connector):
        assert connector.is_india_location("Pune")

    def test_chennai(self, connector):
        assert connector.is_india_location("Chennai")

    def test_india_bare(self, connector):
        assert connector.is_india_location("India")

    def test_rejects_san_francisco(self, connector):
        assert not connector.is_india_location("San Francisco, CA")

    def test_rejects_london(self, connector):
        assert not connector.is_india_location("London, UK")

    def test_rejects_new_york(self, connector):
        assert not connector.is_india_location("New York, USA")

    def test_rejects_singapore(self, connector):
        assert not connector.is_india_location("Singapore")

    def test_rejects_empty(self, connector):
        assert not connector.is_india_location("")

    def test_rejects_remote_without_india(self, connector):
        assert not connector.is_india_location("Remote")

    def test_rejects_not_specified(self, connector):
        assert not connector.is_india_location("Not specified")


# ── clean_url tests ───────────────────────────────────────────────────────────

class TestCleanUrl:
    def test_strips_tracking_parameters(self):
        from app.utils.validation import clean_url
        url = "https://careers.google.com/jobs/results/?q=intern&utm_source=linkedin&ref=123"
        assert clean_url(url) == "https://careers.google.com/jobs/results/?q=intern"

    def test_preserves_non_tracking_parameters(self):
        from app.utils.validation import clean_url
        url = "https://example.com/job?id=9988&gh_jid=12345"
        assert clean_url(url) == "https://example.com/job?id=9988&gh_jid=12345"
