"""
Gemini LLM Service for Generating Human-Readable Explanations
"""

import google.generativeai as genai
from typing import Dict, List
import time

from app.config import get_settings
from app.utils.logger import setup_logger
from app.utils.preprocessing import TextPreprocessor

settings = get_settings()
logger = setup_logger(__name__)


class LLMService:
    """
    Gemini LLM service for explanation generation
    """
    
    def __init__(self):
        """
        Initialize Gemini API
        """
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
            logger.info(f"Gemini LLM initialized: {settings.GEMINI_MODEL}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {str(e)}", exc_info=True)
            raise RuntimeError(f"Gemini initialization failed: {str(e)}")
    
    def generate_explanation(
        self,
        title: str,
        text: str,
        prediction: str,
        confidence: float,
        word_highlights: List[Dict]
    ) -> str:
        """
        Generate human-readable explanation using Gemini
        
        Args:
            title: Article title
            text: Article text
            prediction: "Fake" or "Real"
            confidence: Confidence score
            word_highlights: Word importance from SHAP
            
        Returns:
            Human-readable explanation string
        """
        try:
            start_time = time.time()
            
            # Prepare word lists
            fake_words = [
                w for w in word_highlights 
                if w['direction'] == 'fake'
            ][:5]
            
            real_words = [
                w for w in word_highlights 
                if w['direction'] == 'real'
            ][:5]
            
            # Truncate text for LLM
            text_preview = TextPreprocessor.truncate_text_for_llm(text, max_words=100)
            
            # Build structured prompt
            prompt = self._build_prompt(
                title=title,
                text_preview=text_preview,
                prediction=prediction,
                confidence=confidence,
                fake_words=fake_words,
                real_words=real_words
            )
            
            # Generate explanation
            logger.debug(f"Calling Gemini API with prompt length: {len(prompt)}")
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=settings.GEMINI_TEMPERATURE,
                    max_output_tokens=settings.GEMINI_MAX_TOKENS,
                )
            )
            
            explanation = response.text.strip()
            
            llm_time = (time.time() - start_time) * 1000
            logger.info(f"Gemini explanation generated in {llm_time:.0f}ms")
            logger.debug(f"Explanation length: {len(explanation)} chars")
            
            return explanation
            
        except Exception as e:
            logger.error(f"Gemini API failed: {str(e)}", exc_info=True)
            # Return fallback explanation
            return self._get_fallback_explanation(prediction, confidence)
    
    def _build_prompt(
        self,
        title: str,
        text_preview: str,
        prediction: str,
        confidence: float,
        fake_words: List[Dict],
        real_words: List[Dict]
    ) -> str:
        """
        Build structured prompt for Gemini
        """
        # Format word lists
        fake_words_str = ", ".join([f"'{w['word']}'" for w in fake_words]) if fake_words else "none"
        real_words_str = ", ".join([f"'{w['word']}'" for w in real_words]) if real_words else "none"
        
        prompt = f"""You are an expert fact-checker explaining fake news detection results.

**Article Analysis:**
Title: "{title}"
Text Preview: "{text_preview}"

**Detection Result:**
Prediction: {prediction}
Confidence: {confidence*100:.1f}%

**Key Linguistic Indicators (from AI analysis):**
- Words indicating FAKE news: {fake_words_str}
- Words indicating REAL news: {real_words_str}

**Task:**
Generate a clear, 2-3 sentence explanation for a general audience explaining:
1. Why this article appears to be {prediction.lower()}
2. What specific language patterns or red flags were detected
3. One practical tip for readers to identify such content

**Guidelines:**
- Use simple, conversational language
- Be educational, not accusatory
- Avoid technical jargon (no "SHAP", "model", "AI")
- Focus on actionable insights
- Keep it concise (under 150 words)

**Explanation:**"""
        
        return prompt
    
    def _get_fallback_explanation(self, prediction: str, confidence: float) -> str:
        """
        Fallback explanation if Gemini API fails
        """
        logger.warning("Using fallback explanation (Gemini API failed)")
        
        if prediction == "Fake":
            return (
                f"This article shows signs of misinformation with {confidence*100:.1f}% confidence. "
                "It contains sensational language, emotional manipulation tactics, and lacks credible sources. "
                "Always verify claims through multiple reputable sources before sharing."
            )
        else:
            return (
                f"This article appears credible with {confidence*100:.1f}% confidence. "
                "It uses neutral, factual language and maintains professional journalistic standards. "
                "However, always cross-check important claims with other trusted news outlets."
            )
