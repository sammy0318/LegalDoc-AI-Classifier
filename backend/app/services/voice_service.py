import logging

from app.services.pipeline_service import PipelineService
from app.config import Settings

logger = logging.getLogger(__name__)


class VoiceService:
    """Handles voice-based legal queries.

    The actual speech-to-text runs in the browser via the Web Speech API.
    This service receives the transcribed text, processes it through the
    existing legal pipeline, and returns a voice-friendly response.
    """

    def __init__(self, pipeline_service: PipelineService, settings: Settings):
        self._pipeline = pipeline_service
        self._settings = settings

    async def process_voice_query(
        self, transcript: str, language: str = "en"
    ) -> dict:
        """Process a voice-transcribed legal query through the pipeline.

        Returns dict with keys: answer, source, method, confidence, transcript.
        """
        if not transcript or len(transcript.strip()) < 3:
            return {
                "answer": "I didn't catch that. Could you please repeat your question?"
                if language == "en"
                else "मैं समझ नहीं पाया। कृपया अपना प्रश्न दोहराएं।",
                "source": "voice",
                "method": "error",
                "confidence": None,
                "transcript": transcript or "",
            }

        # Clean up voice transcript (common speech-to-text artifacts)
        cleaned = transcript.strip()

        # Run through the existing legal pipeline
        result = await self._pipeline.ask_legal_question(cleaned, language=language)

        # Ensure voice responses do not contain Markdown markup
        from app.utils.text_processing import strip_markdown

        return {
            "answer": strip_markdown(result.get("answer", "")),
            "source": result.get("source", ""),
            "method": result.get("method", "error"),
            "confidence": result.get("confidence"),
            "transcript": cleaned,
        }
