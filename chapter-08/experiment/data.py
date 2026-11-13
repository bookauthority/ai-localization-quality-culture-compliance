from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class SourceItem:
    source_id: str
    workload: str
    source_text: str
    source_language: str
    target_language: str
    market: str
    channel: str
    topic: str
    risk_level: str


def _wl1_items() -> List[SourceItem]:
    # Marketing landing pages, short synthetic examples
    base = "WL1_marketing_landing_pages"
    return [
        SourceItem(
            source_id="WL1-001",
            workload=base,
            source_text=(
                "Our cloud platform is a slam dunk for your business, "
                "helping you score big wins without breaking a sweat."
            ),
            source_language="en-US",
            target_language="ja-JP",
            market="ja-JP",
            channel="web_marketing",
            topic="product_value_props",
            risk_level="medium",
        ),
        SourceItem(
            source_id="WL1-002",
            workload=base,
            source_text=(
                "Sign up in minutes and watch your productivity skyrocket. "
                "No need to burn the midnight oil to stay ahead."
            ),
            source_language="en-US",
            target_language="de-DE",
            market="de-DE",
            channel="web_marketing",
            topic="campaign_slogans",
            risk_level="medium",
        ),
        SourceItem(
            source_id="WL1-003",
            workload=base,
            source_text=(
                "Our SaaS is a real game changer, giving your team superpowers "
                "without a steep learning curve."
            ),
            source_language="en-US",
            target_language="pt-BR",
            market="pt-BR",
            channel="digital_ads",
            topic="feature_descriptions",
            risk_level="medium",
        ),
    ]


def _wl2_items() -> List[SourceItem]:
    base = "WL2_support_and_help_center_articles"
    return [
        SourceItem(
            source_id="WL2-001",
            workload=base,
            source_text=(
                "If your payment fails, don't panic. Please double-check your "
                "card details and try again, or contact your bank."
            ),
            source_language="en-US",
            target_language="es-MX",
            market="es-MX",
            channel="help_center",
            topic="payment_issues",
            risk_level="low",
        ),
        SourceItem(
            source_id="WL2-002",
            workload=base,
            source_text=(
                "To change your account email, go to Settings > Account and "
                "follow the on-screen instructions. We appreciate your patience."
            ),
            source_language="en-US",
            target_language="ar-SA",
            market="ar-SA",
            channel="in-app_support",
            topic="account_management",
            risk_level="low",
        ),
        SourceItem(
            source_id="WL2-003",
            workload=base,
            source_text=(
                "If a feature seems confusing, you can walk through our guided "
                "tour or reach out to support for a helping hand."
            ),
            source_language="en-US",
            target_language="hi-IN",
            market="hi-IN",
            channel="help_center",
            topic="feature_usage",
            risk_level="low",
        ),
    ]


def _wl3_items() -> List[SourceItem]:
    base = "WL3_high_sensitivity_pharma_patient_leaflets"
    return [
        SourceItem(
            source_id="WL3-001",
            workload=base,
            source_text=(
                "This medication helps manage symptoms of depression. Some "
                "patients may feel worse before they feel better. If you have "
                "thoughts of self-harm, contact a doctor immediately."
            ),
            source_language="en-US",
            target_language="fr-FR",
            market="fr-FR",
            channel="patient_education_web",
            topic="disease_education",
            risk_level="high",
        ),
        SourceItem(
            source_id="WL3-002",
            workload=base,
            source_text=(
                "Do not stop taking this medicine without talking to your "
                "doctor, even if you feel ashamed or fear what your family "
                "might think."
            ),
            source_language="en-US",
            target_language="es-ES",
            market="es-ES",
            channel="patient_leaflet_pdf",
            topic="medication_guide",
            risk_level="high",
        ),
        SourceItem(
            source_id="WL3-003",
            workload=base,
            source_text=(
                "Some side effects related to reproductive health may be "
                "sensitive topics in your community. Speak privately with a "
                "health professional if you have concerns."
            ),
            source_language="en-US",
            target_language="zh-CN",
            market="zh-CN",
            channel="patient_leaflet_pdf",
            topic="side_effects_and_warnings",
            risk_level="high",
        ),
    ]


def load_all_source_items() -> List[SourceItem]:
    """Return the full synthetic dataset for all workloads.

    This acts as a stand-in for proper dataset preparation scripts.
    """

    return _wl1_items() + _wl2_items() + _wl3_items()
