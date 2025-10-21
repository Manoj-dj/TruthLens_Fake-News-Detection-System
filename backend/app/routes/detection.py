"""
Detection API Routes
Main endpoints for fake news detection
"""

from fastapi import APIRouter, HTTPException, status
from datetime import datetime
import uuid
import time

from app.models import (
    NewsDetectionRequest,
    DetectionResponse,
    WordHighlight,
    ErrorResponse
)
from app.services.model_service import ModelService
from app.services.xai_service import XAIService
from app.services.llm_service import LLMService
from app.utils.aws_utils import DynamoDBService
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter(prefix="/api", tags=["Detection"])

# Initialize services (singleton pattern)
model_service = ModelService()
xai_service = XAIService(model_service)
llm_service = LLMService()
dynamodb_service = DynamoDBService()


@router.post(
    "/detect",
    response_model=DetectionResponse,
    status_code=status.HTTP_200_OK,
    summary="Detect fake news from title and text",
    description="Analyzes news article and returns prediction with XAI explanation"
)
async def detect_fake_news(request: NewsDetectionRequest):
    """
    Main endpoint for fake news detection
    
    **Request Body:**
    - title: Article title (5-500 chars)
    - text: Article content (20-10000 chars)
    
    **Response:**
    - prediction: "Fake" or "Real"
    - confidence: Confidence score (0-1)
    - explanation: Human-readable explanation from Gemini LLM
    - word_highlights: Top words influencing prediction
    - processing_time_ms: Total processing time
    
    **Process Flow:**
    1. Validate and preprocess input
    2. RoBERTa model prediction
    3. SHAP XAI analysis (word importance)
    4. Gemini LLM explanation generation
    5. Log to DynamoDB
    6. Return results
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        logger.info(f"[{request_id}] Detection request received")
        logger.info(f"[{request_id}] Title: {request.title[:50]}...")
        
        # Step 1: Model Prediction
        logger.info(f"[{request_id}] Step 1: Running RoBERTa prediction...")
        prediction_result = model_service.predict(request.title, request.text)
        
        # Step 2: XAI Analysis
        logger.info(f"[{request_id}] Step 2: Running SHAP XAI analysis...")
        word_importance = xai_service.get_word_importance(
            combined_text=prediction_result['combined_text'],
            predicted_class=prediction_result['predicted_class'],
            top_n=15
        )
        
        # Convert to response format
        word_highlights = [
            WordHighlight(
                word=w['word'],
                importance=w['importance'],
                direction=w['direction']
            )
            for w in word_importance
        ]
        
        # Step 3: Generate LLM Explanation
        logger.info(f"[{request_id}] Step 3: Generating Gemini explanation...")
        explanation = llm_service.generate_explanation(
            title=request.title,
            text=request.text,
            prediction=prediction_result['prediction'],
            confidence=prediction_result['confidence'],
            word_highlights=word_importance
        )
        
        # Calculate total processing time
        total_time_ms = (time.time() - start_time) * 1000
        
        # Step 4: Log to DynamoDB (async, don't block response)
        logger.info(f"[{request_id}] Step 4: Logging to DynamoDB...")
        try:
            dynamodb_service.log_prediction(
                request_id=request_id,
                title=request.title,
                text=request.text,
                prediction=prediction_result['prediction'],
                confidence=prediction_result['confidence'],
                word_highlights=word_importance,
                explanation=explanation,
                processing_time_ms=total_time_ms
            )
        except Exception as db_error:
            logger.error(f"[{request_id}] DynamoDB logging failed: {str(db_error)}")
            # Don't fail the request if logging fails
        
        # Build response
        response = DetectionResponse(
            success=True,
            prediction=prediction_result['prediction'],
            confidence=prediction_result['confidence'],
            fake_probability=prediction_result['fake_probability'],
            real_probability=prediction_result['real_probability'],
            explanation=explanation,
            word_highlights=word_highlights,
            processing_time_ms=total_time_ms,
            timestamp=datetime.utcnow().isoformat(),
            request_id=request_id
        )
        
        logger.info(
            f"[{request_id}] Detection completed: {response.prediction} "
            f"({response.confidence:.2%}) in {total_time_ms:.0f}ms"
        )
        
        return response
        
    except Exception as e:
        logger.error(f"[{request_id}] Detection failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "Detection processing failed",
                "error_type": type(e).__name__,
                "message": str(e),
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )


@router.get(
    "/health",
    summary="Health check endpoint",
    description="Check if API and model are ready"
)
async def health_check():
    """
    Health check endpoint
    """
    try:
        is_healthy = model_service.is_loaded()
        
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "app_name": "TruthLens Fake News Detection API",
            "version": "1.0.0",
            "is_model_loaded": is_healthy,  # ← Changed from model_loaded
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "app_name": "TruthLens Fake News Detection API",
            "version": "1.0.0",
            "is_model_loaded": False,  # ← Changed from model_loaded
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

