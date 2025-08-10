"""
User Context Manager for Adaptive Experience

This module tracks user behavior and preferences to provide:
- Adaptive information disclosure levels
- Mobile vs desktop optimization  
- Personalized interface preferences
- Smart recommendations based on usage patterns
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from .smart_formatter import InformationLevel, DisplayMode

logger = logging.getLogger(__name__)


@dataclass
class UserPreferences:
    """User preferences for interface customization"""
    preferred_level: InformationLevel = InformationLevel.STANDARD
    preferred_mode: DisplayMode = DisplayMode.AUTO
    prefers_detailed: bool = False
    is_mobile: bool = False
    frequent_user: bool = False
    has_comparisons: bool = False
    last_active: Optional[str] = None
    total_searches: int = 0
    last_levels_used: List[int] = None
    
    def __post_init__(self):
        if self.last_levels_used is None:
            self.last_levels_used = []


@dataclass  
class SessionContext:
    """Current session context and behavior"""
    current_vin: Optional[str] = None
    session_searches: int = 0
    level_changes: int = 0
    preferred_actions: List[str] = None
    is_mobile_session: bool = False
    session_start: Optional[str] = None
    
    def __post_init__(self):
        if self.preferred_actions is None:
            self.preferred_actions = []
        if self.session_start is None:
            self.session_start = datetime.now().isoformat()


class UserContextManager:
    """Manages user context and adaptive interface preferences"""
    
    def __init__(self, cache=None):
        """Initialize with optional cache backend"""
        self.cache = cache
        self._in_memory_contexts = {}  # Fallback storage
        self._in_memory_sessions = {}  # Session storage
    
    def _get_preferences_key(self, user_id: int) -> str:
        """Get cache key for user preferences"""
        return f"user:{user_id}:context:preferences"
    
    def _get_session_key(self, user_id: int) -> str:
        """Get cache key for current session"""
        return f"user:{user_id}:context:session"
    
    async def get_user_preferences(self, user_id: int) -> UserPreferences:
        """Get user preferences with smart defaults"""
        try:
            # Try cache first
            if self.cache:
                prefs_json = await self.cache.get(self._get_preferences_key(user_id))
                if prefs_json:
                    prefs_data = json.loads(prefs_json)
                    # Convert level back to enum
                    if "preferred_level" in prefs_data:
                        prefs_data["preferred_level"] = InformationLevel(prefs_data["preferred_level"])
                    if "preferred_mode" in prefs_data:
                        prefs_data["preferred_mode"] = DisplayMode(prefs_data["preferred_mode"])
                    return UserPreferences(**prefs_data)
            else:
                # In-memory fallback
                if user_id in self._in_memory_contexts:
                    return self._in_memory_contexts[user_id]
        except Exception as e:
            logger.error(f"Error loading user preferences for {user_id}: {e}")
        
        # Return defaults for new user
        return UserPreferences()
    
    async def save_user_preferences(self, user_id: int, preferences: UserPreferences) -> bool:
        """Save user preferences"""
        try:
            preferences.last_active = datetime.now().isoformat()
            
            # Convert to dict for serialization
            prefs_data = asdict(preferences)
            prefs_data["preferred_level"] = preferences.preferred_level.value
            prefs_data["preferred_mode"] = preferences.preferred_mode.value
            
            if self.cache:
                await self.cache.set(
                    self._get_preferences_key(user_id), 
                    json.dumps(prefs_data),
                    ttl=365 * 24 * 3600  # 1 year
                )
            else:
                # In-memory fallback
                self._in_memory_contexts[user_id] = preferences
            
            return True
        except Exception as e:
            logger.error(f"Error saving user preferences for {user_id}: {e}")
            return False
    
    async def get_session_context(self, user_id: int) -> SessionContext:
        """Get current session context"""
        try:
            session_key = self._get_session_key(user_id)
            
            if self.cache:
                session_json = await self.cache.get(session_key)
                if session_json:
                    session_data = json.loads(session_json)
                    return SessionContext(**session_data)
            else:
                # In-memory fallback
                if user_id in self._in_memory_sessions:
                    return self._in_memory_sessions[user_id]
        except Exception as e:
            logger.error(f"Error loading session context for {user_id}: {e}")
        
        # Return new session
        return SessionContext()
    
    async def save_session_context(self, user_id: int, session: SessionContext) -> bool:
        """Save current session context"""
        try:
            session_data = asdict(session)
            session_key = self._get_session_key(user_id)
            
            if self.cache:
                await self.cache.set(
                    session_key,
                    json.dumps(session_data),
                    ttl=24 * 3600  # 24 hours
                )
            else:
                # In-memory fallback
                self._in_memory_sessions[user_id] = session
            
            return True
        except Exception as e:
            logger.error(f"Error saving session context for {user_id}: {e}")
            return False
    
    async def track_vin_search(
        self, 
        user_id: int, 
        vin: str, 
        level_used: InformationLevel,
        is_mobile: bool = False
    ) -> None:
        """Track a VIN search and update user context"""
        try:
            # Update preferences
            prefs = await self.get_user_preferences(user_id)
            prefs.total_searches += 1
            prefs.is_mobile = is_mobile
            
            # Track level usage
            if len(prefs.last_levels_used) >= 10:
                prefs.last_levels_used.pop(0)  # Remove oldest
            prefs.last_levels_used.append(level_used.value)
            
            # Determine if user prefers detailed info
            if len(prefs.last_levels_used) >= 3:
                recent_levels = prefs.last_levels_used[-3:]
                avg_level = sum(recent_levels) / len(recent_levels)
                prefs.prefers_detailed = avg_level >= InformationLevel.DETAILED.value
            
            # Mark as frequent user after 5+ searches
            prefs.frequent_user = prefs.total_searches >= 5
            
            await self.save_user_preferences(user_id, prefs)
            
            # Update session
            session = await self.get_session_context(user_id)
            session.current_vin = vin
            session.session_searches += 1
            session.is_mobile_session = is_mobile
            
            await self.save_session_context(user_id, session)
            
            logger.info(f"Tracked VIN search for user {user_id}: {vin} at level {level_used.name}")
            
        except Exception as e:
            logger.error(f"Error tracking VIN search for user {user_id}: {e}")
    
    async def track_level_change(
        self, 
        user_id: int, 
        from_level: InformationLevel, 
        to_level: InformationLevel
    ) -> None:
        """Track when user changes information levels"""
        try:
            # Update session
            session = await self.get_session_context(user_id)
            session.level_changes += 1
            await self.save_session_context(user_id, session)
            
            # Update preferences based on direction of change
            prefs = await self.get_user_preferences(user_id)
            if to_level.value > from_level.value:
                # User wanted more detail
                prefs.prefers_detailed = True
                prefs.preferred_level = to_level
            else:
                # User wanted less detail - might prefer simpler view
                if to_level == InformationLevel.ESSENTIAL:
                    prefs.preferred_level = InformationLevel.ESSENTIAL
            
            await self.save_user_preferences(user_id, prefs)
            
            logger.info(f"Tracked level change for user {user_id}: {from_level.name} -> {to_level.name}")
            
        except Exception as e:
            logger.error(f"Error tracking level change for user {user_id}: {e}")
    
    async def track_action(self, user_id: int, action: str) -> None:
        """Track user actions for preference learning"""
        try:
            session = await self.get_session_context(user_id)
            if action not in session.preferred_actions:
                session.preferred_actions.append(action)
            
            # Keep only recent actions
            if len(session.preferred_actions) > 10:
                session.preferred_actions = session.preferred_actions[-10:]
            
            await self.save_session_context(user_id, session)
            
            # Update global preferences
            prefs = await self.get_user_preferences(user_id)
            if action == "compare_start":
                prefs.has_comparisons = True
                await self.save_user_preferences(user_id, prefs)
            
        except Exception as e:
            logger.error(f"Error tracking action for user {user_id}: {e}")
    
    async def suggest_optimal_level(
        self, 
        user_id: int, 
        data_richness: float = 0.5
    ) -> InformationLevel:
        """
        Suggest optimal information level based on user context and data richness
        
        Args:
            user_id: User ID
            data_richness: Richness of available data (0.0 to 1.0)
            
        Returns:
            Suggested information level
        """
        try:
            prefs = await self.get_user_preferences(user_id)
            session = await self.get_session_context(user_id)
            
            # Start with user's preferred level
            suggested = prefs.preferred_level
            
            # Adjust based on data richness
            if data_richness < 0.3:
                # Limited data - suggest essential
                suggested = InformationLevel.ESSENTIAL
            elif data_richness > 0.8 and prefs.prefers_detailed:
                # Rich data and user likes details
                suggested = InformationLevel.DETAILED
            
            # Adjust for mobile users
            if prefs.is_mobile or session.is_mobile_session:
                if suggested == InformationLevel.COMPLETE:
                    suggested = InformationLevel.DETAILED
                elif suggested == InformationLevel.DETAILED and not prefs.prefers_detailed:
                    suggested = InformationLevel.STANDARD
            
            # New users get standard level
            if prefs.total_searches < 3:
                suggested = InformationLevel.STANDARD
            
            return suggested
            
        except Exception as e:
            logger.error(f"Error suggesting optimal level for user {user_id}: {e}")
            return InformationLevel.STANDARD
    
    async def get_user_context_dict(self, user_id: int) -> Dict[str, Any]:
        """Get complete user context as dictionary for other components"""
        try:
            prefs = await self.get_user_preferences(user_id)
            session = await self.get_session_context(user_id)
            
            return {
                "preferred_level": prefs.preferred_level,
                "preferred_mode": prefs.preferred_mode,
                "prefers_detailed": prefs.prefers_detailed,
                "is_mobile": prefs.is_mobile or session.is_mobile_session,
                "frequent_user": prefs.frequent_user,
                "has_comparisons": prefs.has_comparisons,
                "total_searches": prefs.total_searches,
                "session_searches": session.session_searches,
                "level_changes": session.level_changes,
                "current_vin": session.current_vin,
                "preferred_actions": session.preferred_actions
            }
            
        except Exception as e:
            logger.error(f"Error getting user context for {user_id}: {e}")
            return {}
    
    async def detect_mobile_user(self, user_id: int, update_context) -> bool:
        """
        Detect if user is on mobile based on Telegram client info
        
        Args:
            user_id: User ID
            update_context: Telegram update context
            
        Returns:
            True if user appears to be on mobile
        """
        try:
            # Telegram doesn't directly expose client type, but we can infer
            # from message patterns, response times, and other indicators
            
            is_mobile = False
            
            # Check if this is consistent with past behavior
            prefs = await self.get_user_preferences(user_id)
            session = await self.get_session_context(user_id)
            
            # If user has shown mobile patterns before
            if prefs.is_mobile:
                is_mobile = True
            
            # Update session and preferences
            session.is_mobile_session = is_mobile
            await self.save_session_context(user_id, session)
            
            if is_mobile and not prefs.is_mobile:
                prefs.is_mobile = True
                await self.save_user_preferences(user_id, prefs)
            
            return is_mobile
            
        except Exception as e:
            logger.error(f"Error detecting mobile user {user_id}: {e}")
            return False
    
    async def calculate_data_richness(self, data: Dict[str, Any]) -> float:
        """
        Calculate richness score for vehicle data (0.0 to 1.0)
        
        Args:
            data: Vehicle data from API response
            
        Returns:
            Richness score from 0.0 (minimal) to 1.0 (very rich)
        """
        try:
            attrs = data.get("attributes", {})
            if not attrs:
                return 0.0
            
            score = 0.0
            total_weight = 0.0
            
            # Essential fields (high weight)
            essential_fields = ["year", "make", "model", "vin"]
            essential_weight = 0.3
            essential_count = sum(1 for field in essential_fields if attrs.get(field))
            score += (essential_count / len(essential_fields)) * essential_weight
            total_weight += essential_weight
            
            # Standard fields (medium weight)
            standard_fields = ["body", "fuel_type", "engine", "transmission", "drive"]
            standard_weight = 0.25
            standard_count = sum(1 for field in standard_fields if attrs.get(field))
            score += (standard_count / len(standard_fields)) * standard_weight
            total_weight += standard_weight
            
            # Detailed fields (medium weight)
            detailed_fields = ["length_mm", "width_mm", "height_mm", "weight_empty_kg", "manufacturer"]
            detailed_weight = 0.25
            detailed_count = sum(1 for field in detailed_fields if attrs.get(field))
            score += (detailed_count / len(detailed_fields)) * detailed_weight
            total_weight += detailed_weight
            
            # Premium fields (lower weight but valuable)
            premium_weight = 0.2
            has_marketvalue = "marketvalue" in data and data["marketvalue"]
            has_history = "history" in data and data["history"]
            has_features = isinstance(attrs.get("features"), list) and len(attrs.get("features", [])) > 0
            
            premium_score = 0.0
            if has_marketvalue:
                premium_score += 0.4
            if has_history:
                premium_score += 0.4
            if has_features:
                premium_score += 0.2
            
            score += premium_score * premium_weight
            total_weight += premium_weight
            
            # Normalize score
            final_score = score / total_weight if total_weight > 0 else 0.0
            return min(1.0, max(0.0, final_score))
            
        except Exception as e:
            logger.error(f"Error calculating data richness: {e}")
            return 0.5  # Default to medium richness
