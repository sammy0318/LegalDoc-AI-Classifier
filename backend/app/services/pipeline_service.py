import logging

from app.services.qa_service import QAService
from app.services.retrieval_service import RetrievalService
from app.services.context_service import ContextService
from app.services.llm_service import check_llm_connection, get_llm_provider
from app.services.prompt_service import PromptService
from app.config import Settings
from app.utils.text_processing import strip_markdown

logger = logging.getLogger(__name__)


class PipelineService:
    """Port of askLegalQuestion.js askLegalQuestion().
    Preserves the exact 6-step pipeline flow and fallback behavior.
    """

    def __init__(
        self,
        qa_service: QAService,
        retrieval_service: RetrievalService,
        context_service: ContextService,
        prompt_service: PromptService,
        settings: Settings,
    ):
        self._qa = qa_service
        self._retrieval = retrieval_service
        self._context = context_service
        self._prompt = prompt_service
        self._settings = settings

    async def ask_legal_question(self, query: str, language: str = "en") -> dict:
        # Step 1: Try QA dataset (threshold 0.85 for direct return)
        qa_result = self._qa.find_answer(query)
        if qa_result and qa_result["confidence"] >= 0.85:
            # If Hindi requested, translate the QA answer via LLM
            if language == "hi":
                llm_available = await check_llm_connection(self._settings)
                if llm_available:
                    llm = get_llm_provider(self._settings)
                    system_msg = (
                        "You are a translator. You MUST write your ENTIRE output in Hindi "
                        "using Devanagari script (हिंदी). Do NOT use any English words or Latin script."
                    )
                    translate_prompt = (
                        "नीचे दिए गए कानूनी उत्तर का हिंदी में अनुवाद करें। "
                        "केवल हिंदी (देवनागरी लिपि) में लिखें।\n\n"
                        f"{qa_result['answer']}"
                    )
                    try:
                        translated = await llm.generate_answer(translate_prompt, system_message=system_msg)
                        if translated and translated.strip():
                            return {
                                "answer": strip_markdown(translated),
                                "source": qa_result["source"],
                                "method": "qa_dataset",
                                "confidence": qa_result["confidence"],
                            }
                    except Exception:
                        pass  # Fall through to return English QA answer
            return {
                "answer": strip_markdown(qa_result["answer"]),
                "source": qa_result["source"],
                "method": "qa_dataset",
                "confidence": qa_result["confidence"],
            }

        # Step 2: Retrieve relevant sections
        sections = self._retrieval.retrieve_relevant_sections(query)
        if not sections:
            msg = ("उपलब्ध अधिनियमों में इस प्रश्न से संबंधित कोई कानूनी प्रावधान नहीं मिला।"
                   if language == "hi" else
                   "No relevant legal provision was found for this query in the available Acts.")
            return {
                "answer": strip_markdown(msg),
                "source": "acts",
                "method": "fallback",
            }

        # Step 3: Build context
        context = self._context.build_context(sections)
        if not context or len(context) < 100:
            msg = ("संबंधित कानूनी प्रावधान मिले, लेकिन विश्वसनीय व्याख्या उत्पन्न करने के लिए पर्याप्त पाठ उपलब्ध नहीं था।"
                   if language == "hi" else
                   "Relevant legal provisions were found, but insufficient text was available to generate a reliable explanation.")
            return {
                "answer": msg,
                "source": "acts",
                "method": "fallback",
            }

        # Step 4: Check LLM availability
        llm_available = await check_llm_connection(self._settings)
        if not llm_available:
            note = ("⚠ AI इंजन वर्तमान में अनुपलब्ध है। नीचे कानूनी पाठ दिया गया है:\n\n"
                    if language == "hi" else
                    "⚠ AI engine is currently unavailable. Showing legal text-based information only:\n\n")
            return {
                "answer": strip_markdown(note + context),
                "source": "acts",
                "method": "no_llm",
            }

        # Step 5: Call LLM
        llm = get_llm_provider(self._settings)
        prompt, system_message = self._prompt.build_prompt(context, query, language=language)
        try:
            llm_answer = await llm.generate_answer(prompt, system_message=system_message)
        except Exception as exc:
            logger.error("LLM generate_answer failed: %s", exc)
            return {
                "answer": strip_markdown(("⚠ AI मॉडल से उत्तर प्राप्त करने में त्रुटि हुई।" if language == "hi" else "The AI model failed to generate a response.")),
                "source": "acts",
                "method": "error",
            }

        if not llm_answer or not llm_answer.strip():
            msg = ("AI मॉडल दिए गए कानूनी संदर्भ से विश्वसनीय उत्तर उत्पन्न नहीं कर सका।"
                   if language == "hi" else
                   "The AI model could not generate a reliable answer from the provided legal context.")
            return {
                "answer": strip_markdown(msg),
                "source": "llm",
                "method": "fallback",
            }

        # Step 6: Final successful response
        return {
            "answer": strip_markdown(llm_answer),
            "source": "LLM + Legal Acts",
            "method": "llm",
        }
