from pathlib import Path


def test_ecommerce_price_monitor_decision_note_is_public_safe() -> None:
    note = Path("production/ecommerce-price-monitor-decision.md").read_text(encoding="utf-8")

    required_terms = [
        "not a provider ranking",
        "Local browser worker",
        "Proxy-backed browser worker",
        "Scraping API",
        "Managed browser provider",
        "cost per 1k successful pages",
        "reports/cost-assumption-worksheet.md",
        "measured",
        "estimated",
        "not tested",
    ]

    for term in required_terms:
        assert term in note

    forbidden_terms = [
        "https://www.scraperapi.com",
        "fp_ref",
        "best provider",
        "affiliate lane",
        "conversion target",
    ]

    for term in forbidden_terms:
        assert term.lower() not in note.lower()


def test_provider_boundary_checklist_is_vendor_neutral() -> None:
    checklist = Path("production/provider-boundary-checklist.md").read_text(encoding="utf-8")

    required_terms = [
        "vendor-neutral",
        "Local fixture path runs without paid services",
        "evidence label",
        "measured_at",
        "Attempted pages",
        "Cost per 1k successful pages",
        "Nearby disclosure",
        "open-source path remains documented",
        "No provider is described as universally best",
        "Private affiliate registry details are not copied into public docs",
    ]

    for term in required_terms:
        assert term in checklist

    forbidden_terms = [
        "https://www.scraperapi.com",
        "fp_ref",
        "affiliate lane",
        "conversion target",
        "mrr",
    ]

    for term in forbidden_terms:
        assert term.lower() not in checklist.lower()


def test_readme_links_production_decision_next_steps_without_provider_links() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")

    required_terms = [
        "## Production Decision Next Steps",
        "reports/cost-assumption-worksheet.md",
        "production/ecommerce-price-monitor-decision.md",
        "production/provider-boundary-checklist.md",
        "measured, estimated,",
        "not-tested provider evidence",
    ]

    for term in required_terms:
        assert term in readme

    forbidden_terms = [
        "https://www.scraperapi.com",
        "fp_ref",
        "affiliate lane",
        "conversion target",
        "best provider",
    ]

    for term in forbidden_terms:
        assert term.lower() not in readme.lower()


def test_public_traffic_snapshot_template_avoids_private_tracking_fields() -> None:
    template = Path("docs/traffic-snapshot-template.md").read_text(encoding="utf-8")

    required_terms = [
        "GitHub Traffic",
        "Referrers",
        "Popular Content",
        "Release And Artifact Signals",
        "Quickstart blockers",
        "Next maintenance action",
    ]

    for term in required_terms:
        assert term in template

    forbidden_terms = [
        "affiliate click",
        "provider signup",
        "conversion target",
        "service inquiry",
        "campaign",
        "mrr",
    ]

    for term in forbidden_terms:
        assert term.lower() not in template.lower()
