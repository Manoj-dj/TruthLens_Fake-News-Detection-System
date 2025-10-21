"""
AWS DynamoDB Utilities for Logging Predictions
UPDATED: Fixed Float to Decimal conversion
"""

import boto3
from botocore.exceptions import ClientError
from datetime import datetime
from typing import Dict, Optional
from decimal import Decimal  # ← ADDED
import uuid

from app.config import get_settings
from app.utils.logger import setup_logger

settings = get_settings()
logger = setup_logger(__name__)


def convert_floats_to_decimal(obj):
    """
    Recursively convert float values to Decimal for DynamoDB compatibility
    
    Args:
        obj: Any Python object (dict, list, float, etc.)
        
    Returns:
        Object with all floats converted to Decimal
    """
    if isinstance(obj, float):
        # Convert float to Decimal
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        # Recursively convert dictionary values
        return {k: convert_floats_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        # Recursively convert list items
        return [convert_floats_to_decimal(i) for i in obj]
    else:
        # Return as-is for other types
        return obj


class DynamoDBService:
    """
    DynamoDB service for logging predictions
    """
    
    def __init__(self):
        """
        Initialize DynamoDB client
        """
        try:
            self.dynamodb = boto3.resource(
                'dynamodb',
                region_name=settings.AWS_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID or None,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY or None
            )
            self.table = self.dynamodb.Table(settings.DYNAMODB_TABLE_NAME)
            logger.info(f"DynamoDB initialized: {settings.DYNAMODB_TABLE_NAME}")
        except Exception as e:
            logger.error(f"DynamoDB initialization failed: {str(e)}")
            self.table = None
    
    def log_prediction(
        self,
        request_id: str,
        title: str,
        text: str,
        prediction: str,
        confidence: float,
        word_highlights: list,
        explanation: str,
        processing_time_ms: float
    ) -> bool:
        """
        Log prediction to DynamoDB
        
        Args:
            request_id: Unique request ID
            title: Article title
            text: Article text
            prediction: Fake/Real
            confidence: Confidence score
            word_highlights: Word importance
            explanation: LLM explanation
            processing_time_ms: Processing time
            
        Returns:
            True if successful, False otherwise
        """
        if not self.table:
            logger.warning("DynamoDB not configured, skipping logging")
            return False
        
        try:
            item = {
                'id': request_id,
                'timestamp': datetime.utcnow().isoformat(),
                'title': title[:500],  # Truncate long titles
                'text_preview': text[:200],  # Store preview only
                'prediction': prediction,
                'confidence': confidence,
                'word_highlights': word_highlights[:10],  # Top 10 words
                'explanation': explanation,
                'processing_time_ms': processing_time_ms,
                'input_type': 'text'
            }
            
            # Convert all floats to Decimal (CRITICAL FIX)
            item = convert_floats_to_decimal(item)
            
            self.table.put_item(Item=item)
            logger.info(f"Logged prediction to DynamoDB: {request_id}")
            return True
            
        except ClientError as e:
            logger.error(f"DynamoDB put_item failed: {str(e)}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"Unexpected error logging to DynamoDB: {str(e)}", exc_info=True)
            return False
