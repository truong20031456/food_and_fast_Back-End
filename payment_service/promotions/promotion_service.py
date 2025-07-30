"""
Promotion Service - Handles promotion and discount functionality.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from utils.logger import get_logger

logger = get_logger(__name__)


class PromotionService:
    """Service for handling promotions and discounts."""
    
    def __init__(self, db_manager=None):
        self.db_manager = db_manager
        # Mock promotion data - in production, fetch from database
        self.promotions = {
            "WELCOME10": {
                "code": "WELCOME10",
                "discount_percentage": 10,
                "discount_amount": None,
                "min_amount": 50,
                "max_discount": 20,
                "valid_from": datetime.now() - timedelta(days=30),
                "valid_until": datetime.now() + timedelta(days=365),
                "usage_limit": 1000,
                "used_count": 150,
                "is_active": True
            },
            "SAVE20": {
                "code": "SAVE20",
                "discount_percentage": None,
                "discount_amount": 20,
                "min_amount": 100,
                "max_discount": 20,
                "valid_from": datetime.now() - timedelta(days=15),
                "valid_until": datetime.now() + timedelta(days=30),
                "usage_limit": 500,
                "used_count": 75,
                "is_active": True
            }
        }
    
    async def validate_promotion_code(
        self, 
        code: str, 
        amount: float, 
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Validate a promotion code."""
        try:
            promotion = self.promotions.get(code.upper())
            
            if not promotion:
                return {
                    "valid": False,
                    "error": "Invalid promotion code"
                }
            
            if not promotion["is_active"]:
                return {
                    "valid": False,
                    "error": "Promotion code is inactive"
                }
            
            current_time = datetime.now()
            if current_time < promotion["valid_from"] or current_time > promotion["valid_until"]:
                return {
                    "valid": False,
                    "error": "Promotion code has expired or not yet active"
                }
            
            if amount < promotion["min_amount"]:
                return {
                    "valid": False,
                    "error": f"Minimum order amount required: ${promotion['min_amount']}"
                }
            
            if promotion["used_count"] >= promotion["usage_limit"]:
                return {
                    "valid": False,
                    "error": "Promotion code usage limit reached"
                }
            
            # Calculate discount
            if promotion["discount_percentage"]:
                discount_amount = amount * (promotion["discount_percentage"] / 100)
                discount_amount = min(discount_amount, promotion["max_discount"])
            else:
                discount_amount = promotion["discount_amount"]
            
            final_amount = amount - discount_amount
            
            return {
                "valid": True,
                "promotion_code": code,
                "original_amount": amount,
                "discount_amount": discount_amount,
                "final_amount": final_amount,
                "discount_percentage": promotion["discount_percentage"]
            }
            
        except Exception as e:
            logger.error(f"Failed to validate promotion code: {e}")
            return {
                "valid": False,
                "error": "Failed to validate promotion code"
            }
    
    async def apply_promotion(
        self, 
        code: str, 
        amount: float, 
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Apply a promotion code to an order."""
        try:
            validation_result = await self.validate_promotion_code(code, amount, user_id)
            
            if not validation_result["valid"]:
                return validation_result
            
            # In production, record the usage in database
            if code.upper() in self.promotions:
                self.promotions[code.upper()]["used_count"] += 1
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Failed to apply promotion: {e}")
            return {
                "valid": False,
                "error": "Failed to apply promotion"
            }
    
    async def get_available_promotions(self, amount: float = 0) -> List[Dict[str, Any]]:
        """Get available promotions for a given amount."""
        try:
            available_promotions = []
            current_time = datetime.now()
            
            for code, promotion in self.promotions.items():
                if (promotion["is_active"] and 
                    current_time >= promotion["valid_from"] and 
                    current_time <= promotion["valid_until"] and
                    amount >= promotion["min_amount"] and
                    promotion["used_count"] < promotion["usage_limit"]):
                    
                    available_promotions.append({
                        "code": code,
                        "description": f"Save {promotion['discount_percentage']}%" if promotion['discount_percentage'] else f"Save ${promotion['discount_amount']}",
                        "min_amount": promotion["min_amount"],
                        "valid_until": promotion["valid_until"].isoformat()
                    })
            
            return available_promotions
            
        except Exception as e:
            logger.error(f"Failed to get available promotions: {e}")
            return []
    
    async def create_promotion(
        self, 
        code: str, 
        discount_percentage: Optional[float] = None,
        discount_amount: Optional[float] = None,
        min_amount: float = 0,
        max_discount: Optional[float] = None,
        valid_until: datetime = None,
        usage_limit: int = 1000
    ) -> Dict[str, Any]:
        """Create a new promotion."""
        try:
            # In production, save to database
            promotion = {
                "code": code.upper(),
                "discount_percentage": discount_percentage,
                "discount_amount": discount_amount,
                "min_amount": min_amount,
                "max_discount": max_discount,
                "valid_from": datetime.now(),
                "valid_until": valid_until or (datetime.now() + timedelta(days=30)),
                "usage_limit": usage_limit,
                "used_count": 0,
                "is_active": True
            }
            
            self.promotions[code.upper()] = promotion
            
            logger.info(f"Created promotion code: {code}")
            return {
                "success": True,
                "promotion": promotion
            }
            
        except Exception as e:
            logger.error(f"Failed to create promotion: {e}")
            return {
                "success": False,
                "error": "Failed to create promotion"
            }
    
    async def deactivate_promotion(self, code: str) -> bool:
        """Deactivate a promotion code."""
        try:
            if code.upper() in self.promotions:
                self.promotions[code.upper()]["is_active"] = False
                logger.info(f"Deactivated promotion code: {code}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to deactivate promotion: {e}")
            return False
