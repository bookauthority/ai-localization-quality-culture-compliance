from typing import Dict, List

CHAPTER_NUMBER = 9
EXPERIMENT_ID = "exp-ch09-compliance-pipeline-prepost-v1"

# Synthetic workloads. In a real system, these would be loaded from JSONL
# datasets under data/ch09_compliance/ as described in the specification.
# Here we define tiny, deterministic fixtures that vaguely resemble the
# described workloads and allow us to exercise the baseline and treatment
# logic symmetrically.

WORKLOADS: List[Dict[str, object]] = [
    {
        "id": "w1-pharma-ifus",
        "description": "Pharmaceutical IFU and safety communications.",
        "risk_profile": "high",
        "source_lang": "en",
        "target_langs": ["es-ES", "de-DE"],
        "documents": [
            {
                "id": "w1-doc1",
                "text": (
                    "This medicine may cause side effects. Read all the "
                    "instructions before use. Contact your doctor at "
                    "patient@example.com for questions."
                ),
            },
            {
                "id": "w1-doc2",
                "text": (
                    "WARNING: Serious risks include liver damage. "
                    "Dosage: 10 mg per day. For emergencies call 111-222-3333."
                ),
            },
        ],
    },
    {
        "id": "w2-financial-disclosures",
        "description": "Investment product summaries and disclosures.",
        "risk_profile": "high",
        "source_lang": "en",
        "target_langs": ["fr-FR", "de-DE"],
        "documents": [
            {
                "id": "w2-doc1",
                "text": (
                    "Past performance is not a reliable indicator of "
                    "future results. This product offers a guaranteed return "
                    "of 5% per year."
                ),
            },
            {
                "id": "w2-doc2",
                "text": (
                    "Your capital is at risk. Returns may vary. "
                    "Investor name: John Doe."
                ),
            },
        ],
    },
    {
        "id": "w3-support-tickets-pii",
        "description": "Customer support tickets with embedded PII.",
        "risk_profile": "medium",
        "source_lang": "en",
        "target_langs": ["es-ES"],
        "documents": [
            {
                "id": "w3-doc1",
                "text": (
                    "Hello, my name is Alice Smith and my account number is "
                    "123456789. Please reset my password."
                ),
            },
            {
                "id": "w3-doc2",
                "text": (
                    "Patient Bob Brown, DOB 1970-01-01, reports side "
                    "effects after taking the medication. Contact at "
                    "bob.brown@example.org."
                ),
            },
        ],
    },
    {
        "id": "w4-lowrisk-marketing",
        "description": "Low-risk generic marketing copy.",
        "risk_profile": "low",
        "source_lang": "en",
        "target_langs": ["fr-FR"],
        "documents": [
            {
                "id": "w4-doc1",
                "text": "Our product helps you stay organized and productive.",
            },
            {
                "id": "w4-doc2",
                "text": "Discover new features every week with our updates.",
            },
        ],
    },
]

# Configuration for simple compliance rules. These are intentionally
# rudimentary but capture the idea of required disclaimers and forbidden
# phrases.

# Phrases that should be present in high-risk financial documents.
REQUIRED_FINANCIAL_DISCLAIMERS = [
    "past performance is not a reliable indicator of future results",
    "your capital is at risk",
]

# Phrases that are considered forbidden promotional claims.
FORBIDDEN_FINANCIAL_PHRASES = [
    "guaranteed return",
]

# Simple tokenization separator set for our trivial tokenizer.
TOKEN_SEPARATORS = " \t\n\r,.!?;:()[]{}"