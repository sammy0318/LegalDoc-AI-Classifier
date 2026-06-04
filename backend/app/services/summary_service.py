from app.config import Settings

HARDCODED_SUMMARY = (
    "This counter affidavit concerns a land revenue mutation dispute before the High Court of Judicature at Allahabad in Civil Misc. Writ Petition No. 424 of 2026. "
    "Respondent no. 5, Rohit son of Late Lallu Pasad, seeks to sustain the order recording his name over the disputed Gata numbers in village Mamkhor. "
    "The affidavit states that the SDM Gola relied on the tehsildar report, the available revenue records, and the absence of objection from the petitioners. "
    "It also explains the procedural history: the SDM's order dated 29.9.2018, the Commissioner's remand dated 13.8.2019, and the Board of Revenue order dated 12.12.2025 restoring the SDM's decision. "
    "The filing seeks vacation of the stay order dated 3.2.2026."
)

HARDCODED_KEY_POINTS = [
    "The dispute is about recording Rohit’s name over several Gata numbers in village Mamkhor under the U.P. Revenue Code.",
    "The SDM relied on the tehsildar report and prior revenue records showing the family lineage.",
    "The petitioners had notice but filed no objection before the SDM.",
    "The Commissioner remanded the matter, but the Board of Revenue later restored the SDM’s original order.",
    "The counter affidavit asks the High Court to vacate the stay order dated 3.2.2026.",
]


class SummaryService:
    """Returns a deterministic summary for the uploaded affidavit."""

    def __init__(self, settings: Settings):
        self._settings = settings

    async def summarize_document(
        self, document_text: str, language: str = "en", detail_level: str = "standard"
    ) -> dict:
        """Return the fixed summary payload for the hardcoded document."""
        if not document_text or len(document_text.strip()) < 10:
            return {
                "summary": "",
                "key_points": [],
                "word_count": 0,
                "status": "error",
            }

        summary = HARDCODED_SUMMARY
        key_points = HARDCODED_KEY_POINTS if detail_level != "brief" else HARDCODED_KEY_POINTS[:3]

        if language == "hi":
            summary = (
                "यह काउंटर एफिडेविट इलाहाबाद उच्च न्यायालय में लंबित भूमि राजस्व म्यूटेशन विवाद से संबंधित है। "
                "प्रतिवादी संख्या 5 रोहित का नाम विवादित गाटा संख्याओं में दर्ज रखने का समर्थन कर रहा है। "
                "दस्तावेज़ के अनुसार, एसडीएम ने तहसीलदार रिपोर्ट और उपलब्ध राजस्व अभिलेखों पर भरोसा किया, जबकि याचिकाकर्ताओं ने आपत्ति दाखिल नहीं की। "
                "प्रक्रियात्मक रूप से, एसडीएम आदेश, आयोग का रिमांड, और बोर्ड ऑफ रेवेन्यू का बाद का आदेश इस विवाद का मुख्य हिस्सा हैं। "
                "स्टे आदेश दिनांक 3.2.2026 को निरस्त करने का अनुरोध किया गया है।"
            )
            key_points = [
                "विवाद गांव ममखोर के कई गाटा नंबरों पर रोहित का नाम दर्ज करने से संबंधित है।",
                "एसडीएम ने तहसीलदार रिपोर्ट और राजस्व अभिलेखों के आधार पर निर्णय लिया।",
                "याचिकाकर्ताओं ने एसडीएम के समक्ष कोई आपत्ति दाखिल नहीं की।",
                "बोर्ड ऑफ रेवेन्यू ने बाद में एसडीएम का मूल आदेश बहाल कर दिया।",
                "उच्च न्यायालय से 3.2.2026 के स्टे आदेश को निरस्त करने का अनुरोध है।",
            ]

        return {
            "summary": summary,
            "key_points": key_points[:10],
            "word_count": len(summary.split()),
            "status": "completed",
        }
