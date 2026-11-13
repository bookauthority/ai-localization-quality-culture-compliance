from typing import List, Dict

CHAPTER_NUMBER = 11
EXPERIMENT_ID = "exp-ch11-linguistic-assets-tm-terms-vs-none-v1"

# Three workloads with small synthetic segment sets. In a real setup, these
# would be loaded from JSONL/XLIFF etc.; here they are embedded to keep the
# project self-contained and deterministic.

WORKLOADS: List[Dict] = [
    {
        "id": "workload-marketing-high-style",
        "description": "Marketing and brand copy with strong style and terminology requirements.",
        "language_pair": "en->fr",
        "segments": [
            {
                "segment_id": "mkt_001",
                "source": "Welcome to CloudSync, the secure way to protect your data.",
                "domain": "marketing",
            },
            {
                "segment_id": "mkt_002",
                "source": "Upgrade to CloudSync Pro for unlimited backups and priority support.",
                "domain": "marketing",
            },
            {
                "segment_id": "mkt_003",
                "source": "CloudSync keeps your files safe across every device.",
                "domain": "marketing",
            },
            {
                "segment_id": "mkt_004",
                "source": "Experience seamless collaboration with CloudSync Teams.",
                "domain": "marketing",
            },
        ],
    },
    {
        "id": "workload-product-ui-terminology-heavy",
        "description": "Product UI strings and in-app messages with strict terminology and non-translatable requirements.",
        "language_pair": "en->es",
        "segments": [
            {
                "segment_id": "ui_001",
                "source": "Open CloudSync settings",
                "domain": "ui",
            },
            {
                "segment_id": "ui_002",
                "source": "CloudSync backup failed. Try again.",
                "domain": "ui",
            },
            {
                "segment_id": "ui_003",
                "source": "Accept the CloudSync Terms of Service.",
                "domain": "ui",
            },
            {
                "segment_id": "ui_004",
                "source": "Your CloudSync Pro trial expires in 3 days.",
                "domain": "ui",
            },
        ],
    },
    {
        "id": "workload-support-knowledgebase-mixed",
        "description": "Support/knowledge base articles with high consistency expectations.",
        "language_pair": "en->de",
        "segments": [
            {
                "segment_id": "kb_001",
                "source": "To restore a previous version, open CloudSync and select History.",
                "domain": "kb",
            },
            {
                "segment_id": "kb_002",
                "source": "CloudSync stores encrypted copies of your files in our data centers.",
                "domain": "kb",
            },
            {
                "segment_id": "kb_003",
                "source": "If CloudSync backup fails, check your network connection and try again.",
                "domain": "kb",
            },
            {
                "segment_id": "kb_004",
                "source": "CloudSync Pro customers can contact premium support via chat.",
                "domain": "kb",
            },
        ],
    },
]
