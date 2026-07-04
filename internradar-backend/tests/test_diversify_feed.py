"""Tests for feed diversification correctness."""

from datetime import UTC, datetime

from app.models.internship import InternshipInDB
from app.services.internship_service import diversify_feed


def _make(
    company: str,
    source: str,
    *,
    title: str = "Intern",
    location: str = "Bangalore, India",
) -> InternshipInDB:
    return InternshipInDB(
        _id=str(abs(hash(company + source + title)) % (10**9)),
        external_id="ext-1",
        source=source,
        company=company,
        title=title,
        location=location,
        remote=False,
        employment_type="Internship",
        url="https://example.com",
        description="A great internship",
        skills=["python"],
        tags=[],
        category="Software Engineering",
        scraped_at=datetime.now(UTC),
        fingerprint=f"fp-{company}-{source}",
    )


def test_no_company_flood_in_first_20() -> None:
    """No single company should appear more than 2× in the first 20 cards."""
    candidates = []
    # 10 companies × 5 listings each across internshala + greenhouse + lever + yc
    for source in ("internshala", "greenhouse", "lever", "yc", "wellfound"):
        for i in range(10):
            candidates.append(_make(f"Company{i}", source))

    result = diversify_feed(candidates, page_size=20)
    first_20 = result[:20]

    company_counts: dict[str, int] = {}
    for item in first_20:
        comp = item.company.lower().strip()
        company_counts[comp] = company_counts.get(comp, 0) + 1

    for comp, count in company_counts.items():
        assert count <= 2, f"Company {comp} appears {count} times in first 20 (max 2)"


def test_internshala_capped_in_first_20() -> None:
    """Internshala should not exceed 30% of the first window (20 cards → max 6)."""
    candidates = []
    # Heavy Internshala: 50 listings, plus 5 from other sources.
    for _ in range(50):
        candidates.append(_make("InternshalaCo", "internshala"))
    for source in ("greenhouse", "lever", "yc", "wellfound", "simplify"):
        for _ in range(5):
            candidates.append(_make("StartupCo", source))

    result = diversify_feed(candidates, page_size=20)
    first_20 = result[:20]

    internshala_count = sum(1 for item in first_20 if item.source.lower() == "internshala")
    assert internshala_count <= 6, (
        f"Internshala has {internshala_count} cards in first 20 (max 6 = 30%)"
    )


def test_single_candidate_returns_itself() -> None:
    candidates = [_make("Solo", "greenhouse")]
    result = diversify_feed(candidates, page_size=20)
    assert len(result) == 1
    assert result[0].company == "Solo"


def test_empty_candidates_returns_empty() -> None:
    assert diversify_feed([], page_size=20) == []
