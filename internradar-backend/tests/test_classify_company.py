"""Tests for company classification logic."""

import pytest

from app.classification.company_classifier import (
    FEATURED_MNCS,
    STARTUP_SOURCES,
    classify_company,
    parse_headcount,
)


class TestClassifyCompany:
    def test_featured_mnc_by_exact_name(self) -> None:
        assert classify_company("Google") == "mnc"
        assert classify_company("microsoft") == "mnc"
        assert classify_company("Amazon") == "mnc"

    def test_featured_mnc_with_suffix(self) -> None:
        assert classify_company("Google LLC") == "mnc"
        assert classify_company("Microsoft India") == "mnc"

    def test_startup_by_source(self) -> None:
        assert classify_company("Cursor", source="yc") == "startup"
        assert classify_company("Perplexity", source="wellfound") == "startup"
        assert classify_company("Mercor", source="simplify") == "startup"
        assert classify_company("SomeCo", source="ripplematch") == "startup"

    def test_startup_by_small_headcount(self) -> None:
        assert classify_company("Acme Corp", company_size="50 - 200") == "startup"
        assert classify_company("Acme Corp", company_size="1,000 - 5,000") == "startup"

    def test_enterprise_by_large_headcount(self) -> None:
        assert classify_company("Wipro", company_size="10,000+") == "enterprise"
        assert classify_company("Infosys", company_size="200,000") == "enterprise"

    def test_enterprise_default(self) -> None:
        assert classify_company("Wipro") == "enterprise"
        assert classify_company("Infosys") == "enterprise"

    def test_empty_company(self) -> None:
        assert classify_company("") == "enterprise"
        assert classify_company("   ") == "enterprise"


class TestParseHeadcount:
    def test_range(self) -> None:
        assert parse_headcount("1,000 - 5,000") == 1000
        assert parse_headcount("201-500") == 201

    def test_single(self) -> None:
        assert parse_headcount("10,001+") == 10001
        assert parse_headcount("50") == 50

    def test_none(self) -> None:
        assert parse_headcount(None) is None
        assert parse_headcount("") is None
        assert parse_headcount("Unknown") is None
