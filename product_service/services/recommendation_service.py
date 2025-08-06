"""
Machine Learning Recommendation System
Provides food recommendations based on user behavior and preferences
"""

import json
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter

from shared_code.utils.redis import get_redis_manager
from shared_code.utils.logging import get_logger

logger = get_logger(__name__)


class RecommendationEngine:
    """ML-based recommendation engine for food items."""

    def __init__(self, redis_manager=None):
        self.redis = redis_manager or get_redis_manager()
        self.model_cache_ttl = 3600  # 1 hour
        self.user_profile_ttl = 86400  # 24 hours

    async def collect_user_behavior(
        self, user_id: str, action: str, item_data: Dict[str, Any]
    ):
        """
        Collect user behavior data for ML model training.

        Args:
            user_id: User identifier
            action: Action type (view, order, like, dislike, etc.)
            item_data: Data about the item (product_id, category, price, etc.)
        """
        try:
            behavior_key = f"user_behavior:{user_id}"
            behavior_entry = {
                "timestamp": datetime.now().isoformat(),
                "action": action,
                "item_data": item_data,
            }

            # Store behavior in Redis list
            await self.redis.lpush(behavior_key, json.dumps(behavior_entry))
            await self.redis.ltrim(behavior_key, 0, 999)  # Keep last 1000 actions
            await self.redis.expire(behavior_key, self.user_profile_ttl)

            # Update real-time counters
            await self._update_realtime_counters(user_id, action, item_data)

            logger.debug(f"Collected behavior for user {user_id}: {action}")

        except Exception as e:
            logger.error(f"Error collecting user behavior: {str(e)}")

    async def _update_realtime_counters(
        self, user_id: str, action: str, item_data: Dict[str, Any]
    ):
        """Update real-time counters for quick recommendations."""
        try:
            # Category preferences
            category = item_data.get("category")
            if category:
                category_key = f"user_category_pref:{user_id}"
                await self.redis.hincrby(category_key, category, 1)
                await self.redis.expire(category_key, self.user_profile_ttl)

            # Price range preferences
            price = item_data.get("price", 0)
            if price > 0:
                price_range = self._get_price_range(price)
                price_key = f"user_price_pref:{user_id}"
                await self.redis.hincrby(price_key, price_range, 1)
                await self.redis.expire(price_key, self.user_profile_ttl)

            # Restaurant preferences
            restaurant_id = item_data.get("restaurant_id")
            if restaurant_id:
                restaurant_key = f"user_restaurant_pref:{user_id}"
                await self.redis.hincrby(restaurant_key, restaurant_id, 1)
                await self.redis.expire(restaurant_key, self.user_profile_ttl)

        except Exception as e:
            logger.error(f"Error updating realtime counters: {str(e)}")

    def _get_price_range(self, price: float) -> str:
        """Categorize price into ranges."""
        if price < 20:
            return "budget"
        elif price < 50:
            return "mid_range"
        elif price < 100:
            return "premium"
        else:
            return "luxury"

    async def build_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Build comprehensive user profile from behavior data.

        Args:
            user_id: User identifier

        Returns:
            User profile dictionary
        """
        try:
            profile_key = f"user_profile:{user_id}"

            # Check if profile is cached
            cached_profile = await self.redis.get(profile_key)
            if cached_profile:
                return json.loads(cached_profile)

            # Build profile from behavior data
            behavior_key = f"user_behavior:{user_id}"
            behaviors = await self.redis.lrange(behavior_key, 0, -1)

            if not behaviors:
                return await self._default_user_profile()

            # Analyze behaviors
            profile = {
                "user_id": user_id,
                "created_at": datetime.now().isoformat(),
                "total_actions": len(behaviors),
                "category_preferences": {},
                "price_preferences": {},
                "restaurant_preferences": {},
                "cuisine_preferences": {},
                "time_preferences": {},
                "dietary_restrictions": [],
                "favorite_items": [],
                "average_order_value": 0.0,
                "order_frequency": "medium",
            }

            # Process behaviors
            categories = Counter()
            prices = []
            restaurants = Counter()
            cuisines = Counter()
            hours = Counter()
            orders = []

            for behavior_str in behaviors:
                try:
                    behavior = json.loads(behavior_str)
                    action = behavior.get("action")
                    item_data = behavior.get("item_data", {})
                    timestamp = datetime.fromisoformat(behavior.get("timestamp"))

                    if action in ["order", "like"]:
                        # Positive signals
                        categories[item_data.get("category", "unknown")] += 2
                        restaurants[item_data.get("restaurant_id", "unknown")] += 1
                        cuisines[item_data.get("cuisine", "unknown")] += 1

                        if action == "order":
                            price = item_data.get("price", 0)
                            if price > 0:
                                prices.append(price)
                                orders.append({"price": price, "timestamp": timestamp})

                    elif action == "view":
                        # Neutral signals
                        categories[item_data.get("category", "unknown")] += 1

                    # Time preferences
                    hours[timestamp.hour] += 1

                except Exception:
                    continue

            # Build preferences
            total_actions = max(len(behaviors), 1)

            profile["category_preferences"] = {
                cat: count / total_actions for cat, count in categories.most_common(10)
            }

            profile["restaurant_preferences"] = {
                rest: count / total_actions
                for rest, count in restaurants.most_common(10)
            }

            profile["cuisine_preferences"] = {
                cuisine: count / total_actions
                for cuisine, count in cuisines.most_common(10)
            }

            # Price analysis
            if prices:
                profile["average_order_value"] = sum(prices) / len(prices)
                profile["price_preferences"] = {
                    "min": min(prices),
                    "max": max(prices),
                    "avg": profile["average_order_value"],
                    "preferred_range": self._get_price_range(
                        profile["average_order_value"]
                    ),
                }

            # Time preferences
            if hours:
                peak_hours = [hour for hour, count in hours.most_common(3)]
                profile["time_preferences"] = {
                    "peak_hours": peak_hours,
                    "preferred_time": (
                        "lunch"
                        if 11 <= peak_hours[0] <= 14
                        else "dinner" if 18 <= peak_hours[0] <= 21 else "other"
                    ),
                }

            # Order frequency
            if orders:
                days_span = (
                    datetime.now() - min(order["timestamp"] for order in orders)
                ).days or 1
                frequency = len(orders) / days_span
                if frequency > 0.5:
                    profile["order_frequency"] = "high"
                elif frequency > 0.2:
                    profile["order_frequency"] = "medium"
                else:
                    profile["order_frequency"] = "low"

            # Cache profile
            await self.redis.setex(
                profile_key, self.user_profile_ttl, json.dumps(profile)
            )

            logger.info(f"Built user profile for {user_id}")
            return profile

        except Exception as e:
            logger.error(f"Error building user profile: {str(e)}")
            return await self._default_user_profile()

    async def _default_user_profile(self) -> Dict[str, Any]:
        """Return default user profile for new users."""
        return {
            "user_id": "new_user",
            "created_at": datetime.now().isoformat(),
            "total_actions": 0,
            "category_preferences": {"popular": 0.8, "trending": 0.6},
            "price_preferences": {"preferred_range": "mid_range"},
            "order_frequency": "low",
            "time_preferences": {"preferred_time": "dinner"},
        }

    async def get_recommendations(
        self,
        user_id: str,
        num_recommendations: int = 10,
        context: Dict[str, Any] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get personalized recommendations for a user.

        Args:
            user_id: User identifier
            num_recommendations: Number of recommendations to return
            context: Current context (time, location, etc.)

        Returns:
            List of recommended items with scores
        """
        try:
            # Get user profile
            user_profile = await self.build_user_profile(user_id)

            # Get available items (in real system, this would query product service)
            available_items = await self._get_available_items()

            # Score items based on user preferences
            scored_items = []

            for item in available_items:
                score = await self._calculate_item_score(item, user_profile, context)
                if score > 0:
                    scored_items.append(
                        {
                            "item": item,
                            "score": score,
                            "reasons": self._get_recommendation_reasons(
                                item, user_profile
                            ),
                        }
                    )

            # Sort by score and return top recommendations
            scored_items.sort(key=lambda x: x["score"], reverse=True)
            recommendations = scored_items[:num_recommendations]

            # Log recommendation event
            await self._log_recommendation_event(user_id, recommendations)

            logger.info(
                f"Generated {len(recommendations)} recommendations for user {user_id}"
            )
            return recommendations

        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            return []

    async def _calculate_item_score(
        self,
        item: Dict[str, Any],
        user_profile: Dict[str, Any],
        context: Dict[str, Any] = None,
    ) -> float:
        """Calculate recommendation score for an item."""
        try:
            score = 0.0

            # Category preference score
            category = item.get("category", "")
            category_prefs = user_profile.get("category_preferences", {})
            if category in category_prefs:
                score += category_prefs[category] * 0.3

            # Price preference score
            item_price = item.get("price", 0)
            price_prefs = user_profile.get("price_preferences", {})
            if price_prefs:
                user_avg_price = price_prefs.get("avg", 50)
                price_diff = abs(item_price - user_avg_price) / max(user_avg_price, 1)
                price_score = max(0, 1 - price_diff)
                score += price_score * 0.2

            # Restaurant preference score
            restaurant_id = item.get("restaurant_id", "")
            restaurant_prefs = user_profile.get("restaurant_preferences", {})
            if restaurant_id in restaurant_prefs:
                score += restaurant_prefs[restaurant_id] * 0.2

            # Rating score
            rating = item.get("rating", 0)
            if rating > 0:
                score += (rating / 5.0) * 0.15

            # Popularity score
            popularity = item.get("order_count", 0)
            if popularity > 0:
                popularity_score = min(1.0, popularity / 1000)  # Normalize to 0-1
                score += popularity_score * 0.1

            # Context-based adjustments
            if context:
                current_hour = context.get("hour", datetime.now().hour)
                time_prefs = user_profile.get("time_preferences", {})
                peak_hours = time_prefs.get("peak_hours", [])
                if current_hour in peak_hours:
                    score += 0.05

            return min(score, 1.0)  # Cap at 1.0

        except Exception as e:
            logger.error(f"Error calculating item score: {str(e)}")
            return 0.0

    def _get_recommendation_reasons(
        self, item: Dict[str, Any], user_profile: Dict[str, Any]
    ) -> List[str]:
        """Get reasons why an item was recommended."""
        reasons = []

        # Category preference
        category = item.get("category", "")
        category_prefs = user_profile.get("category_preferences", {})
        if category in category_prefs and category_prefs[category] > 0.1:
            reasons.append(f"You often order {category}")

        # Restaurant preference
        restaurant_id = item.get("restaurant_id", "")
        restaurant_prefs = user_profile.get("restaurant_preferences", {})
        if restaurant_id in restaurant_prefs:
            reasons.append("From a restaurant you like")

        # High rating
        rating = item.get("rating", 0)
        if rating >= 4.5:
            reasons.append("Highly rated by customers")

        # Popular item
        order_count = item.get("order_count", 0)
        if order_count > 500:
            reasons.append("Popular choice")

        return reasons[:3]  # Return top 3 reasons

    async def _get_available_items(self) -> List[Dict[str, Any]]:
        """Get available items (mock data for demonstration)."""
        # In a real system, this would query the product service
        return [
            {
                "id": "item_1",
                "name": "Margherita Pizza",
                "category": "pizza",
                "cuisine": "italian",
                "price": 25.99,
                "rating": 4.5,
                "restaurant_id": "rest_1",
                "order_count": 1250,
                "description": "Classic margherita with fresh basil",
            },
            {
                "id": "item_2",
                "name": "Chicken Burger",
                "category": "burger",
                "cuisine": "american",
                "price": 18.50,
                "rating": 4.2,
                "restaurant_id": "rest_2",
                "order_count": 890,
                "description": "Grilled chicken burger with fries",
            },
            {
                "id": "item_3",
                "name": "Pad Thai",
                "category": "noodles",
                "cuisine": "thai",
                "price": 22.00,
                "rating": 4.7,
                "restaurant_id": "rest_3",
                "order_count": 650,
                "description": "Traditional Thai noodles with shrimp",
            },
            # Add more mock items as needed
        ]

    async def _log_recommendation_event(
        self, user_id: str, recommendations: List[Dict[str, Any]]
    ):
        """Log recommendation event for analysis."""
        try:
            event = {
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "num_recommendations": len(recommendations),
                "item_ids": [rec["item"]["id"] for rec in recommendations],
                "top_score": recommendations[0]["score"] if recommendations else 0,
            }

            event_key = f"recommendation_events:{user_id}"
            await self.redis.lpush(event_key, json.dumps(event))
            await self.redis.ltrim(event_key, 0, 99)  # Keep last 100 events
            await self.redis.expire(event_key, 86400 * 7)  # 7 days

        except Exception as e:
            logger.error(f"Error logging recommendation event: {str(e)}")

    async def get_similar_items(
        self, item_id: str, num_similar: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get items similar to a given item.

        Args:
            item_id: Reference item ID
            num_similar: Number of similar items to return

        Returns:
            List of similar items
        """
        try:
            # This is a simplified similarity calculation
            # In production, use more sophisticated ML techniques

            available_items = await self._get_available_items()
            reference_item = next(
                (item for item in available_items if item["id"] == item_id), None
            )

            if not reference_item:
                return []

            similar_items = []

            for item in available_items:
                if item["id"] == item_id:
                    continue

                similarity_score = self._calculate_similarity(reference_item, item)
                if similarity_score > 0.3:  # Threshold for similarity
                    similar_items.append(
                        {"item": item, "similarity_score": similarity_score}
                    )

            # Sort by similarity and return top items
            similar_items.sort(key=lambda x: x["similarity_score"], reverse=True)
            return similar_items[:num_similar]

        except Exception as e:
            logger.error(f"Error getting similar items: {str(e)}")
            return []

    def _calculate_similarity(
        self, item1: Dict[str, Any], item2: Dict[str, Any]
    ) -> float:
        """Calculate similarity score between two items."""
        score = 0.0

        # Category similarity
        if item1.get("category") == item2.get("category"):
            score += 0.4

        # Cuisine similarity
        if item1.get("cuisine") == item2.get("cuisine"):
            score += 0.3

        # Price similarity
        price1 = item1.get("price", 0)
        price2 = item2.get("price", 0)
        if price1 > 0 and price2 > 0:
            price_diff = abs(price1 - price2) / max(price1, price2)
            price_similarity = max(0, 1 - price_diff)
            score += price_similarity * 0.2

        # Rating similarity
        rating1 = item1.get("rating", 0)
        rating2 = item2.get("rating", 0)
        if rating1 > 0 and rating2 > 0:
            rating_diff = abs(rating1 - rating2) / 5.0
            rating_similarity = max(0, 1 - rating_diff)
            score += rating_similarity * 0.1

        return score
