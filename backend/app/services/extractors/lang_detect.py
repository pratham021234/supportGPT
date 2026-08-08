import langdetect
import logging

logger = logging.getLogger(__name__)

class LanguageDetector:
    @staticmethod
    def detect(text: str) -> str:
        """
        Detects the language of the given text and returns its ISO 639-1 code.
        Returns 'unknown' if detection fails.
        """
        if not text or len(text.strip()) < 10:
            return "unknown"
            
        try:
            return langdetect.detect(text)
        except Exception as e:
            logger.warning(f"Language detection failed: {e}")
            return "unknown"
