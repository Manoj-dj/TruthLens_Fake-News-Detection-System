"""
Text Preprocessing Utilities
"""

import re
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class TextPreprocessor:
    """
    Text preprocessing for fake news detection
    """
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Basic text cleaning
        
        Args:
            text: Raw input text
            
        Returns:
            Cleaned text
        """
        try:
            # Remove extra whitespace
            text = re.sub(r'\s+', ' ', text)
            
            # Remove special characters but keep punctuation
            text = re.sub(r'[^\w\s.,!?;:\'-]', '', text)
            
            # Strip leading/trailing whitespace
            text = text.strip()
            
            logger.debug(f"Text cleaned: length={len(text)}")
            return text
            
        except Exception as e:
            logger.error(f"Error cleaning text: {str(e)}")
            return text
    
    @staticmethod
    def combine_title_text(title: str, text: str, separator: str = " </s> ") -> str:
        """
        Combine title and text with separator token
        
        Args:
            title: Article title
            text: Article content
            separator: Separator token (RoBERTa uses </s>)
            
        Returns:
            Combined text
        """
        try:
            cleaned_title = TextPreprocessor.clean_text(title)
            cleaned_text = TextPreprocessor.clean_text(text)
            
            combined = f"{cleaned_title}{separator}{cleaned_text}"
            
            logger.debug(f"Combined title+text: length={len(combined)}")
            return combined
            
        except Exception as e:
            logger.error(f"Error combining title and text: {str(e)}")
            return f"{title} {text}"
    
    @staticmethod
    def truncate_text_for_llm(text: str, max_words: int = 150) -> str:
        """
        Truncate text for LLM prompt to save tokens
        
        Args:
            text: Full text
            max_words: Maximum number of words
            
        Returns:
            Truncated text
        """
        words = text.split()
        if len(words) <= max_words:
            return text
        
        truncated = ' '.join(words[:max_words]) + "..."
        logger.debug(f"Text truncated for LLM: {len(words)} -> {max_words} words")
        return truncated
