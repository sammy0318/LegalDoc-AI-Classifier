"""Hardcoded extraction service used to keep the backend running without OCR.

This service preserves the existing upload/review response shape, but returns a
fixed legal document payload instead of running PaddleOCR or any external OCR
stack. That keeps the backend startup and upload flow deterministic.
"""

from __future__ import annotations

HARDCODED_EXTRACTION_TEXT = """Here's the full extracted text and analysis:

DOCUMENT: Counter Affidavit - High Court of Judicature at Allahabad
Civil Misc. Writ Petition No. 424 of 2026, District: Gorakhpur

PARTIES

Petitioners: Jawahar Lal, Somnath, Seshnath (all sons of Kashi Prasad), residents of village Mamkhor, Tappa Mazuri, Pargana Dhuriyapur, Tehsil Gola, District Gorakhpur
Respondents:

State of U.P. through Secretary, Land Revenue Dept., Lucknow
Board of Revenue U.P., Lucknow
Commissioner Gorakhpur Division
Sub Divisional Magistrate, Tehsil Gola, Gorakhpur
Rohit son of Lallu Pasad, village Mamkhor, Gorakhpur



Deponent: Vivek Yadav, aged 23, son of Late Krishnamurari Yadav, Mamkhor, Gorakhpur. Aadhar No. 478646839246. He is pairokar and family friend of Respondent no. 5.
Advocate: Rajesh Kumar Yadav, AOR No. A/R-0458/12, Chamber-1, M.G. Marg, High Court, Allahabad. Mobile: 9415292601

CORE FACTS (from affidavit paragraphs)

Respondent no. 5 (Rohit, son of Late Lallu) filed application under Section 31/32 U.P. Revenue Code 2006 for recording his name over Gata nos. 238, 265, 266K, 295, 390, 383, 385, 649 and 737 in village Mamkhor as legal heir of Late Lallu.
SDM Gola called Tehsildar report (dated 30.8.2018), which confirmed names of Ayodhya, Kashi and Lallu sons of Raghunath in Khatauni as per 1359 Fasli.
Petitioners were served notice but filed no objection.
SDM passed order dated 29.9.2018 allowing name recording of Rohit based on evidence and record.
Petitioners filed revision against 29.9.2018 order - Commissioner remanded back the matter on 13.8.2019 (illegally per respondent).
Respondent no. 5 filed revision before Board of Revenue, which allowed it vide order dated 12.12.2025, restoring the SDM's original order.
Present writ petition challenges this, and court issued stay order dated 3.2.2026.
This counter affidavit seeks vacation of the stay order.


CONCLUSION FOR HARDCODING
Document Type     : Counter Affidavit
Court             : High Court of Judicature at Allahabad
Case No.          : Civil Misc. Writ Petition No. 424 of 2026
District          : Gorakhpur
Filed By          : Respondent No. 5 (Rohit son of Lallu Pasad)
Against           : Stay order dated 3.2.2026
Subject Matter    : Land revenue mutation / name recording dispute (Section 31/32 UP Revenue Code)
Key Dates         : SDM Order: 29.9.2018 | Commissioner Remand: 13.8.2019 | Board of Revenue Order: 12.12.2025 | Stay Order: 3.2.2026
Prayer            : Vacate stay order dated 3.2.2026
Advocate          : Rajesh Kumar Yadav, AOR A/R-0458/12"""


def build_hardcoded_extraction_result(page_count: int = 1) -> dict:
    return {
        "raw_text": HARDCODED_EXTRACTION_TEXT,
        "page_count": page_count,
        "confidence_score": 1.0,
    }


class VisionService:
    """Drop-in replacement that returns the hardcoded document payload."""

    def __init__(self, lang: str = "auto"):
        self._lang = lang

    async def extract_text(self, image_bytes: bytes) -> dict:
        return build_hardcoded_extraction_result(page_count=1)

    async def extract_text_from_pdf(self, pdf_bytes: bytes) -> dict:
        return build_hardcoded_extraction_result(page_count=1)
