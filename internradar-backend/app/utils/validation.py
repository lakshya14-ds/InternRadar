"""Internship URL validation and redirection checker."""

import asyncio
import logging
from urllib.parse import urlparse
import httpx

logger = logging.getLogger(__name__)

_validation_semaphore = asyncio.Semaphore(10)


async def validate_job_url(url: str) -> tuple[bool, str, str, str]:
    """Validate a job URL.

    Follows redirects and checks for generic pages or expired postings.
    Returns (is_valid, original_url, canonical_url, final_url).
    """
    if not url:
        return False, "", "", ""

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }

    original_url = url
    canonical_url = url
    final_url = url

    parsed_orig = urlparse(url)
    if not parsed_orig.scheme or not parsed_orig.netloc:
        return False, original_url, canonical_url, final_url

    async with _validation_semaphore:
        try:
            async with httpx.AsyncClient(
                headers=headers, timeout=10.0, follow_redirects=True
            ) as client:
                response = await client.get(url)

            # Check 1: HTTP 200
            if response.status_code != 200:
                logger.info("URL validation failed: HTTP %d for %s", response.status_code, url)
                return False, original_url, canonical_url, final_url

            final_url = str(response.url)
            parsed_final = urlparse(final_url)

            # Check 2: NOT homepage
            if parsed_final.path.strip("/") == "":
                logger.info("URL validation failed: Redirects to homepage for %s", url)
                return False, original_url, canonical_url, final_url

            # Check 3: NOT category, search, or login page
            path_lower = parsed_final.path.lower()

            is_job_detail = False
            # Check if it has a job ID or specific detail pattern
            detail_patterns = [
                "/jobs/",
                "/postings/",
                "/posting/",
                "/job/",
                "/detail/",
                "/career/",
            ]
            if any(p in path_lower for p in detail_patterns):
                is_job_detail = True

            # If it's a generic landing page, reject
            if not is_job_detail:
                generic_pages = ["/search", "/login", "/signin", "/signup", "/register"]
                if any(ind in path_lower for ind in generic_pages):
                    logger.info("URL validation failed: Generic landing/auth page for %s", url)
                    return False, original_url, canonical_url, final_url

            # Check 4: Content Validation
            page_text = response.text.lower()
            expired_keywords = [
                "posting has expired",
                "job not available",
                "this job is no longer",
                "no internships found",
                "position has been filled",
                "job is closed",
                "page not found",
                "404",
                "not found",
            ]

            if any(keyword in page_text for keyword in expired_keywords):
                logger.info("URL validation failed: Expired content on page for %s", url)
                return False, original_url, canonical_url, final_url

            # Determine a canonical clean URL (stripping query parameters)
            canonical_url = f"{parsed_final.scheme}://{parsed_final.netloc}{parsed_final.path}"

            return True, original_url, canonical_url, final_url

        except Exception as exc:
            logger.info("URL validation failed: Request exception for %s: %s", url, exc)
            return False, original_url, canonical_url, final_url
