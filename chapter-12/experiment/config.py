from __future__ import annotations

"""Static configuration for the chapter 12 vendor bake-off experiment.

This module encodes the workloads, language pairs, and vendor identifiers used
by the experiment harness. Real systems would often externalize these as YAML
or JSON configs; here we keep them as Python constants for simplicity and
offline execution.
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class Workload:
    """Represents a logical workload under evaluation.

    Fields roughly mirror the long-form specification but are trimmed for this
    offline simulation.
    """

    workload_id: str
    description: str
    language_pairs: List[str]


# Workloads as described in the specification
WORKLOADS: Dict[str, Workload] = {
    "pharma_patient_info_high_risk": Workload(
        workload_id="pharma_patient_info_high_risk",
        description=(
            "High-risk, patient-facing pharmaceutical information leaflets and "
            "safety communications requiring strict fidelity and compliance."
        ),
        language_pairs=["en->de", "en->fr", "en->es", "en->ja"],
    ),
    "finance_marketing_and_disclosures_medium_risk": Workload(
        workload_id="finance_marketing_and_disclosures_medium_risk",
        description=(
            "Mixture of regulated financial disclosures and adjacent marketing "
            "content where accuracy and tone both matter."
        ),
        language_pairs=["en->es", "en->pt-BR", "en->fr", "en->zh-CN"],
    ),
    "b2b_saas_ui_and_help_low_to_medium_risk": Workload(
        workload_id="b2b_saas_ui_and_help_low_to_medium_risk",
        description=(
            "Software UI strings, notifications, and help-center content for a "
            "B2B SaaS product."
        ),
        language_pairs=["en->de", "en->fr", "en->ja", "en->ko"],
    ),
}


# Vendor identifiers: one baseline and two additional vendors used in the
# treatment hybrid model.
BASELINE_VENDOR_ID = "baseline_single_vendor"
VENDOR_A_ID = "vendor_mt_a"
VENDOR_B_ID = "vendor_llm_b"


# Simple hybrid routing policy, mapping (workload_id, target_lang) to vendor_id.
# This is a stand-in for more complex learned or rule-based routing.
HYBRID_ROUTING_POLICY: Dict[str, Dict[str, str]] = {
    # For pharma high-risk, we might prefer a conservative MT engine (vendor A)
    # for European languages and vendor B for Japanese.
    "pharma_patient_info_high_risk": {
        "de": VENDOR_A_ID,
        "fr": VENDOR_A_ID,
        "es": VENDOR_A_ID,
        "ja": VENDOR_B_ID,
    },
    # For finance, we split responsibilities between vendors.
    "finance_marketing_and_disclosures_medium_risk": {
        "es": VENDOR_A_ID,
        "pt-BR": VENDOR_A_ID,
        "fr": VENDOR_B_ID,
        "zh-CN": VENDOR_B_ID,
    },
    # For SaaS UI/help, we arbitrarily route half the languages to each.
    "b2b_saas_ui_and_help_low_to_medium_risk": {
        "de": VENDOR_A_ID,
        "fr": VENDOR_B_ID,
        "ja": VENDOR_A_ID,
        "ko": VENDOR_B_ID,
    },
}
