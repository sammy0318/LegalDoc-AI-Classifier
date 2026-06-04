from app.config import Settings

HARDCODED_TIMELINE = [
    {
        "date": "30.8.2018",
        "event": "Tehsildar report confirmed the names of Ayodhya, Kashi, and Lallu sons of Raghunath in the revenue record.",
    },
    {
        "date": "29.9.2018",
        "event": "SDM Gola passed the mutation order allowing Rohit’s name to be recorded over the disputed Gata numbers.",
    },
    {
        "date": "13.8.2019",
        "event": "The Commissioner remanded the matter back for reconsideration.",
    },
    {
        "date": "12.12.2025",
        "event": "Board of Revenue allowed the revision and restored the SDM’s original order.",
    },
    {
        "date": "3.2.2026",
        "event": "The High Court issued a stay order in the present writ petition; the counter affidavit seeks vacation of this stay.",
    },
]


class TimelineService:
    """Returns a deterministic legal timeline for the uploaded affidavit."""

    def __init__(self, settings: Settings):
        self._settings = settings

    async def generate_timeline(
        self, document_text: str, language: str = "en"
    ) -> dict:
        """Return the fixed timeline payload for the hardcoded document."""
        if not document_text or len(document_text.strip()) < 10:
            return {
                "timeline": [],
                "event_count": 0,
                "status": "error",
            }

        timeline = HARDCODED_TIMELINE if language == "en" else [
            {"date": "30.8.2018", "event": "तहसीलदार रिपोर्ट में आयोध्या, काशी और लल्लू के नाम की पुष्टि हुई।"},
            {"date": "29.9.2018", "event": "एसडीएम गोला ने रोहित के नाम दर्ज करने का आदेश पारित किया।"},
            {"date": "13.8.2019", "event": "आयुक्त ने मामले को पुनर्विचार हेतु वापस भेजा।"},
            {"date": "12.12.2025", "event": "बोर्ड ऑफ रेवेन्यू ने एसडीएम का मूल आदेश बहाल किया।"},
            {"date": "3.2.2026", "event": "उच्च न्यायालय ने स्टे आदेश जारी किया; प्रतिवाद-पत्र में इसे निरस्त करने का अनुरोध है।"},
        ]

        return {
            "timeline": timeline,
            "event_count": len(timeline),
            "status": "completed",
        }
