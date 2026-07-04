"""Company classification into startup / mnc / enterprise.

A single source of truth for the "featured MNC" set and the startup-source set,
plus a :func:`classify_company` helper used at ingest time and in analytics.

Classification rules (in priority order):
  1. ``mnc``        — company matches the well-known featured MNC set.
  2. ``startup``    — ingested from a startup ecosystem source (YC, Wellfound,
                      Simplify, RippleMatch) or the parsed ``company_size`` is
                      small (effective headcount <= ~1000).
  3. ``enterprise`` — large companies that are not in the featured MNC list
                      (e.g. Wipro, Infosys, TCS, Cognizant).

Keeping this logic in one place prevents the previous behaviour where
everything that was not a featured MNC was mislabelled a "startup".
"""

from __future__ import annotations

import re

#: Well-known multinational tech employers shown in the "Featured MNC" rail.
FEATURED_MNCS: frozenset[str] = frozenset({
    "google", "microsoft", "amazon", "nvidia", "adobe", "atlassian",
    "salesforce", "databricks", "uber", "stripe", "snowflake", "mongodb",
    "servicenow", "cisco", "intel", "qualcomm", "oracle", "vmware",
    "paypal", "sap",
})

#: Sources that primarily index startup / early-stage opportunities.
STARTUP_SOURCES: frozenset[str] = frozenset({"yc", "wellfound", "simplify", "ripplematch"})

#: Maximum effective headcount for a company to still count as a "startup".
_STARTUP_MAX_HEADCOUNT = 1000


def _normalize(name: str) -> str:
    """Lower-case, strip punctuation/suffixes for robust comparison."""
    if not name:
        return ""
    clean = name.lower().strip()
    clean = re.sub(r"\s+india$", "", clean)        # drop trailing "India"
    clean = re.sub(r"[^\w\s]", "", clean)          # drop punctuation
    return clean.strip()


def parse_headcount(company_size: str | None) -> int | None:
    """Best-effort extraction of an effective headcount from a size string.

    Handles values such as ``"1,000 - 5,000"``, ``"201-500"``, ``"10,001+"``
    by returning the lower bound (the conservative estimate of how large the
    company is). Returns ``None`` when no number can be parsed.
    """
    if not company_size:
        return None
    numbers = re.findall(r"\d[\d,]*", company_size)
    if not numbers:
        return None
    try:
        # The first number is the lower bound of the range.
        return int(numbers[0].replace(",", ""))
    except ValueError:
        return None


def classify_company(
    company: str,
    source: str | None = None,
    company_size: str | None = None,
) -> str:
    """Classify a company as ``"startup"``, ``"mnc"`` or ``"enterprise"``.

    Priority:
      1. Exact/substring match against :data:`FEATURED_MNCS` -> ``"mnc"``.
      2. Startup ecosystem source or small headcount -> ``"startup"``.
      3. Otherwise -> ``"enterprise"`` (large non-featured companies).
    """
    norm = _normalize(company)

    # 1. Featured MNC — match either the whole name or the leading token so
    #    "Google India" / "Google LLC" still resolve correctly.
    if norm:
        tokens = norm.split()
        first_token = tokens[0] if tokens else norm
        if norm in FEATURED_MNCS or first_token in FEATURED_MNCS:
            return "mnc"

    # 2. Startup by source …
    src = (source or "").lower().strip()
    if src in STARTUP_SOURCES:
        return "startup"

    # … or by small headcount.
    headcount = parse_headcount(company_size)
    if headcount is not None and headcount <= _STARTUP_MAX_HEADCOUNT:
        return "startup"

    # 3. Anything else is a (typically large) enterprise employer.
    return "enterprise"
