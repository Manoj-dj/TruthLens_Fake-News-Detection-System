"""
RoBERTa Model Service for Fake News Detection
Handles model loading, inference, and prediction
"""

import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from typing import Dict, Tuple
import time

from app.config import get_settings
from app.utils.logger import setup_logger
from app.utils.preprocessing import TextPreprocessor

settings = get_settings()
logger = setup_logger(__name__)


class ModelService:
    """
    Singleton service for RoBERTa model inference
    """
    
    _instance = None
    _model = None
    _tokenizer = None
    _device = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelService, cls).__new__(cls)
            cls._instance._initialize_model()
        return cls._instance
    
    def _initialize_model(self):
        """
        Initialize model and tokenizer (called once)
        FIXED: Use slow tokenizer to bypass corrupted tokenizer.json
        """
        try:
            logger.info("Initializing RoBERTa model...")
            start_time = time.time()
            
            # Set device
            self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            logger.info(f"Using device: {self._device}")
            
            # Load tokenizer - FORCE SLOW TOKENIZER
            logger.info(f"Loading tokenizer from: {settings.MODEL_PATH}")
            logger.info("Using slow tokenizer to avoid tokenizer.json corruption issues")
            
            self._tokenizer = AutoTokenizer.from_pretrained(
                settings.MODEL_PATH,
                use_fast=False,  # ← KEY FIX: Force slow tokenizer
                trust_remote_code=True
            )
            
            logger.info(f"Tokenizer loaded: {type(self._tokenizer).__name__}")
            
            # Load model
            logger.info(f"Loading model from: {settings.MODEL_PATH}")
            self._model = AutoModelForSequenceClassification.from_pretrained(
                settings.MODEL_PATH,
                num_labels=2,
                trust_remote_code=True
            )
            self._model.to(self._device)
            self._model.eval()
            
            load_time = time.time() - start_time
            logger.info(f"Model loaded successfully in {load_time:.2f}s")
            logger.info(f"Model parameters: {sum(p.numel() for p in self._model.parameters()):,}")
            
        except Exception as e:
            logger.error(f"Failed to initialize model: {str(e)}", exc_info=True)
            raise RuntimeError(f"Model initialization failed: {str(e)}")

    
    def predict(self, title: str, text: str) -> Dict:
        """
        Predict if news is fake or real
        
        Args:
            title: Article title
            text: Article content
            
        Returns:
            Dictionary with prediction results
        """
        try:
            start_time = time.time()
            
            # Preprocess and combine
            combined_text = TextPreprocessor.combine_title_text(title, text)
            
            # Tokenize
            inputs = self._tokenizer(
                combined_text,
                return_tensors="pt",
                truncation=True,
                max_length=settings.MAX_TEXT_LENGTH,
                padding=True
            )
            inputs = {k: v.to(self._device) for k, v in inputs.items()}
            
            # Inference
            with torch.no_grad():
                outputs = self._model(**inputs)
                logits = outputs.logits
                probabilities = torch.nn.functional.softmax(logits, dim=-1)
                predicted_class = torch.argmax(probabilities, dim=-1).item()
                confidence = probabilities[0][predicted_class].item()
            
            prediction_time = (time.time() - start_time) * 1000
            
            result = {
                "prediction": "Fake" if predicted_class == 0 else "Real",
                "predicted_class": predicted_class,
                "confidence": float(confidence),
                "fake_probability": float(probabilities[0][0].item()),
                "real_probability": float(probabilities[0][1].item()),
                "combined_text": combined_text,
                "prediction_time_ms": prediction_time
            }
            
            logger.info(f"Prediction: {result['prediction']} ({result['confidence']:.2%}) in {prediction_time:.0f}ms")
            return result
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}", exc_info=True)
            raise RuntimeError(f"Prediction failed: {str(e)}")
    
    def is_loaded(self) -> bool:
        """
        Check if model is loaded
        """
        return self._model is not None and self._tokenizer is not None
    
    @property
    def device(self):
        return self._device
    
    @property
    def tokenizer(self):
        return self._tokenizer
    
    @property
    def model(self):
        return self._model
