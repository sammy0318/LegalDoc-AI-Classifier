import logging

from app.services.llm_service import check_llm_connection, get_llm_provider
from app.services.retrieval_service import RetrievalService
from app.services.context_service import ContextService
from app.config import Settings
from app.utils.text_processing import strip_markdown

logger = logging.getLogger(__name__)

JUDGEMENT_SYSTEM_PROMPT = (
    "You are an expert Indian legal analyst specializing in predicting case outcomes. "
    "Based on the provided case details, relevant legal provisions, and established precedents, "
    "analyze the likely judgement outcome. Consider:\n"
    "1. Applicable laws and sections\n"
    "2. Strength of evidence described\n"
    "3. Historical precedents in similar cases\n"
    "4. Mitigating and aggravating factors\n"
    "5. Procedural aspects\n\n"
    "Provide a balanced analysis with probability assessment. "
    "Always include a disclaimer that this is an AI-generated prediction and not legal advice."
)

JUDGEMENT_HINDI_SYSTEM = (
    "आप एक विशेषज्ञ भारतीय कानूनी विश्लेषक हैं जो मामले के परिणामों की भविष्यवाणी में विशेषज्ञता रखते हैं। "
    "प्रदान किए गए मामले के विवरण, प्रासंगिक कानूनी प्रावधानों और स्थापित मिसालों के आधार पर, "
    "संभावित निर्णय परिणाम का विश्लेषण करें। "
    "आपको अपना संपूर्ण उत्तर हिंदी में देवनागरी लिपि में लिखना होगा। "
    "हमेशा अस्वीकरण शामिल करें कि यह AI-जनित भविष्यवाणी है और कानूनी सलाह नहीं है।"
)


class JudgementService:
    """Predicts potential case outcomes based on case details and legal context."""

    def __init__(
        self,
        retrieval_service: RetrievalService,
        context_service: ContextService,
        settings: Settings,
    ):
        self._retrieval = retrieval_service
        self._context = context_service
        self._settings = settings

    async def predict_judgement(
        self,
        case_description: str,
        case_type: str = "general",
        language: str = "en",
    ) -> dict:
        """Predict the likely outcome of a legal case using LLM + legal context.

        Returns dict with keys: prediction, relevant_sections, confidence_level, disclaimer, status.
        """
        if not case_description or len(case_description.strip()) < 20:
            return {
                "prediction": "",
                "relevant_sections": [],
                "confidence_level": "none",
                "disclaimer": "",
                "status": "error",
            }

        # Retrieve relevant legal sections for the case
        sections = self._retrieval.retrieve_relevant_sections(case_description, limit=5)
        context = self._context.build_context(sections) if sections else ""

        relevant_section_names = [
            f"{s.get('act', '')} Section {s.get('section', 'N/A')}"
            for s in sections
        ] if sections else []

        llm_available = await check_llm_connection(self._settings)
        if not llm_available:
            # Provide a deterministic fallback prediction when LLM is unavailable
            logger.warning("LLM unavailable, returning fallback judgement prediction")
            disclaimer = (
                "अस्वीकरण: यह AI-जनित भविष्यवाणी है और इसे पेशेवर कानूनी सलाह नहीं माना जाना चाहिए।"
                if language == "hi"
                else "Disclaimer: This is an AI-generated prediction and should not be considered professional legal advice. Always consult a qualified legal professional for actual case guidance."
            )
            return {
                "prediction": self._fallback_prediction(case_description, case_type, language, relevant_section_names),
                "relevant_sections": relevant_section_names,
                "confidence_level": "low",
                "disclaimer": disclaimer,
                "status": "fallback",
            }

        llm = get_llm_provider(self._settings)

        if language == "hi":
            prompt = (
                "नीचे दिए गए मामले के विवरण और कानूनी संदर्भ के आधार पर, संभावित निर्णय की भविष्यवाणी करें।\n\n"
                f"मामले का प्रकार: {case_type}\n\n"
                f"मामले का विवरण:\n{case_description[:3000]}\n\n"
            )
            if context:
                prompt += f"प्रासंगिक कानूनी प्रावधान:\n{context}\n\n"
            prompt += (
                "कृपया बताएं:\n"
                "1. संभावित निर्णय\n"
                "2. विश्लेषण और तर्क\n"
                "3. प्रासंगिक मिसालें\n"
                "4. सफलता की संभावना (उच्च/मध्यम/निम्न)\n"
                "5. महत्वपूर्ण कारक\n\n"
                "भविष्यवाणी (केवल हिंदी में):"
            )
            system_message = JUDGEMENT_HINDI_SYSTEM
        else:
            prompt = (
                "Based on the following case details and legal context, predict the likely judgement.\n\n"
                f"Case Type: {case_type}\n\n"
                f"Case Description:\n{case_description[:3000]}\n\n"
            )
            if context:
                prompt += f"Relevant Legal Provisions:\n{context}\n\n"
            prompt += (
                "Please provide:\n"
                "1. Likely Judgement/Outcome\n"
                "2. Analysis and Reasoning\n"
                "3. Relevant Precedents\n"
                "4. Probability of Success (HIGH / MEDIUM / LOW)\n"
                "5. Critical Factors that could influence the outcome\n\n"
                "Prediction:"
            )
            system_message = JUDGEMENT_SYSTEM_PROMPT

        try:
            result = await llm.generate_answer(prompt, system_message=system_message)
        except Exception as exc:
            logger.error("Judgement prediction LLM call failed: %s", exc)
            # On LLM failure, return a conservative non-LLM fallback prediction
            disclaimer = (
                "अस्वीकरण: यह AI-जनित भविष्यवाणी है और इसे पेशेवर कानूनी सलाह नहीं माना जाना चाहिए।"
                if language == "hi"
                else "Disclaimer: This is an AI-generated prediction and should not be considered professional legal advice. Always consult a qualified legal professional for actual case guidance."
            )
            return {
                "prediction": self._fallback_prediction(case_description, case_type, language, relevant_section_names),
                "relevant_sections": relevant_section_names,
                "confidence_level": "low",
                "disclaimer": disclaimer,
                "status": "fallback",
            }

        if not result or not result.strip():
            return {
                "prediction": "The AI could not generate a prediction for this case.",
                "relevant_sections": relevant_section_names,
                "confidence_level": "none",
                "disclaimer": "",
                "status": "error",
            }

        # Detect confidence level from the response
        result_upper = result.upper()
        if "HIGH" in result_upper or "उच्च" in result_upper:
            confidence_level = "high"
        elif "LOW" in result_upper or "निम्न" in result_upper:
            confidence_level = "low"
        else:
            confidence_level = "medium"

        disclaimer = (
            "अस्वीकरण: यह AI-जनित भविष्यवाणी है और इसे पेशेवर कानूनी सलाह नहीं माना जाना चाहिए।"
            if language == "hi"
            else "Disclaimer: This is an AI-generated prediction and should not be considered professional legal advice. "
            "Always consult a qualified legal professional for actual case guidance."
        )

        # Strip markdown from LLM-generated answer to avoid raw markup in UI
        clean_prediction = strip_markdown(result.strip())
        return {
            "prediction": clean_prediction,
            "relevant_sections": relevant_section_names,
            "confidence_level": confidence_level,
            "disclaimer": disclaimer,
            "status": "completed",
        }

    def _fallback_prediction(
        self,
        case_description: str,
        case_type: str,
        language: str,
        relevant_section_names: list,
    ) -> str:
        """Generate a short, deterministic fallback prediction when LLM is unavailable.

        This uses available retrieved section names and simple heuristics to produce
        a helpful message rather than a hard error.
        """
        sections = ", ".join(relevant_section_names) if relevant_section_names else "no specific provisions found"
        if language == "hi":
            pred = (
                f"AI इंजन उपलब्ध नहीं था। उपलब्ध कानूनी प्रावधान: {sections}।\n"
                "प्रस्तावित निष्कर्ष: तथ्य और साक्ष्यों पर निर्भर करता है; वर्तमान जानकारी के आधार पर स्पष्ट निर्णय कहना कठिन है।"
            )
        else:
            pred = (
                f"AI engine was unavailable. Relevant legal provisions: {sections}.\n"
                "Conservative assessment: outcome is uncertain and will depend on evidence strength and applicable precedents."
            )
        return pred
