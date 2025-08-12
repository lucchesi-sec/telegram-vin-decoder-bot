"""Premium features formatter for enhanced vehicle display."""

from typing import Dict, Any, List, Tuple


class PremiumFeaturesFormatter:
    """Formatter for premium vehicle features with categorization and styling."""
    
    # Feature category mappings
    CATEGORY_ICONS = {
        "safety": "🛡️",
        "comfort": "🛋️",
        "technology": "📱",
        "performance": "⚡",
        "exterior": "✨",
        "interior": "🎨",
        "entertainment": "🎵",
        "convenience": "🔧",
        "luxury": "💎",
        "eco": "🌿"
    }
    
    # Keywords for categorizing features
    CATEGORY_KEYWORDS = {
        "safety": ["airbag", "abs", "brake", "safety", "collision", "assist", "warning", "sensor", "camera", "blind spot", "lane", "parking"],
        "comfort": ["seat", "climate", "heated", "cooled", "ventilated", "massage", "memory", "lumbar", "adjustable"],
        "technology": ["navigation", "gps", "bluetooth", "android", "apple", "carplay", "display", "screen", "digital", "smart"],
        "performance": ["sport", "turbo", "supercharged", "performance", "exhaust", "suspension", "differential", "awd", "4wd"],
        "exterior": ["wheel", "rim", "paint", "metallic", "pearl", "roof", "spoiler", "mirror", "chrome", "led", "xenon"],
        "interior": ["leather", "wood", "carbon", "aluminum", "trim", "ambient", "lighting", "carpet", "floor"],
        "entertainment": ["audio", "speaker", "sound", "radio", "cd", "mp3", "usb", "aux", "premium sound", "bose", "harman"],
        "convenience": ["keyless", "power", "automatic", "electric", "remote", "hands-free", "sensor", "auto"],
        "luxury": ["premium", "luxury", "exclusive", "executive", "prestige", "elite"],
        "eco": ["hybrid", "electric", "eco", "fuel", "efficiency", "start-stop", "regenerative"]
    }
    
    @classmethod
    def categorize_feature(cls, feature: str) -> str:
        """Categorize a feature based on keywords.
        
        Args:
            feature: Feature name/description
            
        Returns:
            Category name
        """
        feature_lower = feature.lower()
        
        for category, keywords in cls.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in feature_lower:
                    return category
        
        return "convenience"  # Default category
    
    @classmethod
    def format_features_section(cls, features: List[str]) -> str:
        """Format features into categorized sections.
        
        Args:
            features: List of feature names
            
        Returns:
            Formatted features text for Telegram
        """
        if not features:
            return ""
        
        # Categorize features
        categorized: Dict[str, List[str]] = {}
        for feature in features:
            category = cls.categorize_feature(feature)
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(feature)
        
        # Sort categories by importance
        category_order = ["safety", "luxury", "technology", "performance", "comfort", 
                         "entertainment", "convenience", "exterior", "interior", "eco"]
        
        lines = []
        lines.append("\n🌟 *PREMIUM FEATURES*")
        lines.append("━" * 25)
        
        for category in category_order:
            if category in categorized:
                icon = cls.CATEGORY_ICONS.get(category, "•")
                category_title = category.capitalize()
                lines.append(f"\n{icon} *{category_title}*")
                
                # Format features in this category - show ALL features
                for feature in categorized[category]:  # Remove the [:5] limit
                    # Truncate long feature names
                    if len(feature) > 40:
                        feature = feature[:37] + "..."
                    lines.append(f"  • {feature}")
        
        # Add total feature count summary
        total_features = len(features)
        if total_features > 0:
            lines.append(f"\n✨ _Total: {total_features} premium features_")
        
        return "\n".join(lines)
    
    @classmethod
    def format_premium_summary(cls, data: Dict[str, Any]) -> Tuple[str, int]:
        """Generate a premium features summary with count.
        
        Args:
            data: Vehicle data dictionary
            
        Returns:
            Tuple of (summary text, feature count)
        """
        features = cls.extract_features(data)
        
        if not features:
            return "", 0
        
        # Count features by category
        category_counts: Dict[str, int] = {}
        for feature in features:
            category = cls.categorize_feature(feature)
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Generate summary
        top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        summary_parts = []
        for category, count in top_categories:
            icon = cls.CATEGORY_ICONS.get(category, "•")
            summary_parts.append(f"{icon} {count} {category}")
        
        summary = " • ".join(summary_parts)
        
        return summary, len(features)
    
    @classmethod
    def extract_features(cls, data: Dict[str, Any]) -> List[str]:
        """Extract features from vehicle data.
        
        Args:
            data: Vehicle data from decoder
            
        Returns:
            List of feature names
        """
        features = []
        
        # Handle different data structures
        if isinstance(data, dict):
            # Check for features in attributes
            if "attributes" in data:
                attrs = data["attributes"]
                if "features" in attrs and isinstance(attrs["features"], list):
                    features.extend(attrs["features"])
            
            # Check for options
            if "options" in data and isinstance(data["options"], list):
                for category in data["options"]:
                    if isinstance(category, dict) and "options" in category:
                        for option in category["options"]:
                            if isinstance(option, dict) and "name" in option:
                                features.append(option["name"])
            
            # Check for features directly in data
            if "features" in data and isinstance(data["features"], list):
                features.extend(data["features"])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_features = []
        for feature in features:
            if feature not in seen:
                seen.add(feature)
                unique_features.append(feature)
        
        return unique_features
    
    @classmethod
    def format_premium_badge(cls, feature_count: int) -> str:
        """Generate a premium badge based on feature count.
        
        Args:
            feature_count: Number of premium features
            
        Returns:
            Badge text
        """
        if feature_count >= 20:
            return "💎 *FULLY LOADED*"
        elif feature_count >= 15:
            return "🏆 *PREMIUM PLUS*"
        elif feature_count >= 10:
            return "⭐ *PREMIUM*"
        elif feature_count >= 5:
            return "✨ *ENHANCED*"
        else:
            return ""
    
    @classmethod
    def get_feature_categories(cls, features: List[str]) -> Dict[str, List[str]]:
        """Get features organized by categories.
        
        Args:
            features: List of feature names
            
        Returns:
            Dictionary with categories as keys and feature lists as values
        """
        if not features:
            return {}
        
        categorized: Dict[str, List[str]] = {}
        for feature in features:
            category = cls.categorize_feature(feature)
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(feature)
        
        return categorized
    
    @classmethod
    def format_features_summary_with_buttons(cls, features: List[str]) -> str:
        """Format a summary of features with button navigation prompt.
        
        Args:
            features: List of feature names
            
        Returns:
            Formatted summary text for Telegram
        """
        if not features:
            return ""
        
        categorized = cls.get_feature_categories(features)
        
        lines = []
        lines.append("\n🌟 *PREMIUM FEATURES*")
        lines.append("━" * 25)
        
        # Show category counts
        category_order = ["safety", "luxury", "technology", "performance", "comfort", 
                         "entertainment", "convenience", "exterior", "interior", "eco"]
        
        feature_summary = []
        for category in category_order:
            if category in categorized:
                count = len(categorized[category])
                icon = cls.CATEGORY_ICONS.get(category, "•")
                feature_summary.append(f"{icon} {count} {category}")
        
        if feature_summary:
            lines.append("\n" + " • ".join(feature_summary[:3]))
            if len(feature_summary) > 3:
                lines.append(" • ".join(feature_summary[3:6]))
        
        lines.append(f"\n✨ _Total: {len(features)} premium features_")
        lines.append("\n👇 *Select a category to view features:*")
        
        return "\n".join(lines)
    
    @classmethod
    def format_category_features(cls, category: str, features: List[str]) -> str:
        """Format features for a specific category.
        
        Args:
            category: Category name
            features: List of features in this category
            
        Returns:
            Formatted text for Telegram
        """
        icon = cls.CATEGORY_ICONS.get(category, "•")
        lines = []
        lines.append(f"{icon} *{category.upper()} FEATURES*")
        lines.append("━" * 25)
        
        for feature in features:
            # Truncate long feature names
            if len(feature) > 50:
                feature = feature[:47] + "..."
            lines.append(f"• {feature}")
        
        lines.append(f"\n_Total: {len(features)} {category} features_")
        
        return "\n".join(lines)
    
    @classmethod
    def format_category_features_paginated(
        cls, category: str, features: List[str], page: int, total_pages: int, total_features: int
    ) -> str:
        """Format features for a specific category with pagination info.
        
        Args:
            category: Category name
            features: List of features in this page
            page: Current page number
            total_pages: Total number of pages
            total_features: Total number of features in category
            
        Returns:
            Formatted text for Telegram
        """
        icon = cls.CATEGORY_ICONS.get(category, "•")
        lines = []
        lines.append(f"{icon} *{category.upper()} FEATURES*")
        lines.append("━" * 25)
        
        for feature in features:
            # Truncate long feature names
            if len(feature) > 50:
                feature = feature[:47] + "..."
            lines.append(f"• {feature}")
        
        # Add pagination info
        if total_pages > 1:
            lines.append(f"\n📄 _Page {page} of {total_pages}_")
        lines.append(f"_Total: {total_features} {category} features_")
        
        return "\n".join(lines)