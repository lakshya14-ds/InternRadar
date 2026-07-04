"""Company name normalization helpers."""

import re

COMPANY_NORMALIZATION_RULES = {
    "google llc": "Google",
    "google india pvt ltd": "Google",
    "google india private limited": "Google",
    "google inc": "Google",
    "google inc.": "Google",
    "microsoft corporation": "Microsoft",
    "microsoft india pvt ltd": "Microsoft",
    "microsoft india": "Microsoft",
    "accenture services pvt ltd": "Accenture",
    "accenture india": "Accenture",
    "tata consultancy services ltd": "TCS",
    "tata consultancy services": "TCS",
    "tcs india": "TCS",
    "amazon dev center india": "Amazon",
    "amazon.com": "Amazon",
    "amazon india": "Amazon",
}


def normalize_company_name(name: str) -> str:
    """Normalize common company names to their base canonical name."""
    if not name:
        return ""

    clean_orig = name.strip()
    clean_lower = clean_orig.lower()

    # 1. Direct dictionary match
    if clean_lower in COMPANY_NORMALIZATION_RULES:
        return COMPANY_NORMALIZATION_RULES[clean_lower]

    # 2. General regex stripping of common corporate suffixes
    suffixes = [
        r"\bllc\b",
        r"\binc\.?\b",
        r"\bcorp(oration)?\b",
        r"\bco\.?\b",
        r"\bpvt\.?\s*ltd\.?\b",
        r"\bprivate\s+limited\b",
        r"\bltd\.?\b",
        r"\blimited\b",
        r"\bindia\b",
        r"\bsolutions\b",
        r"\btechnologies\b",
        r"\bservices\b",
    ]

    clean = clean_orig
    for suffix in suffixes:
        clean = re.sub(suffix, "", clean, flags=re.IGNORECASE).strip()

    # Clean up double spaces or trailing punctuation
    clean = re.sub(r"\s+", " ", clean)
    clean = clean.strip(" ,.-")

    return clean if clean else clean_orig
