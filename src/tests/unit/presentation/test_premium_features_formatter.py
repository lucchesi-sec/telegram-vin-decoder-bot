"""Unit tests for premium features formatter."""

from src.presentation.telegram_bot.formatters.premium_features_formatter import PremiumFeaturesFormatter


class TestPremiumFeaturesFormatter:
    """Tests for PremiumFeaturesFormatter."""
    
    def test_categorize_feature_safety(self):
        """Test categorizing safety features."""
        assert PremiumFeaturesFormatter.categorize_feature("Airbag System") == "safety"
        assert PremiumFeaturesFormatter.categorize_feature("ABS Brakes") == "safety"
        assert PremiumFeaturesFormatter.categorize_feature("Blind Spot Monitoring") == "safety"
        assert PremiumFeaturesFormatter.categorize_feature("Lane Departure Warning") == "safety"
    
    def test_categorize_feature_comfort(self):
        """Test categorizing comfort features."""
        assert PremiumFeaturesFormatter.categorize_feature("Heated Seats") == "comfort"
        assert PremiumFeaturesFormatter.categorize_feature("Cooled Seats") == "comfort"
        assert PremiumFeaturesFormatter.categorize_feature("Memory Seats") == "comfort"
        assert PremiumFeaturesFormatter.categorize_feature("Climate Control") == "comfort"
    
    def test_categorize_feature_technology(self):
        """Test categorizing technology features."""
        assert PremiumFeaturesFormatter.categorize_feature("Navigation System") == "technology"
        assert PremiumFeaturesFormatter.categorize_feature("Apple CarPlay") == "technology"
        assert PremiumFeaturesFormatter.categorize_feature("Android Auto") == "technology"
        assert PremiumFeaturesFormatter.categorize_feature("Digital Display") == "technology"
    
    def test_categorize_feature_performance(self):
        """Test categorizing performance features."""
        assert PremiumFeaturesFormatter.categorize_feature("Sport Mode") == "performance"
        assert PremiumFeaturesFormatter.categorize_feature("Turbo Engine") == "performance"
        assert PremiumFeaturesFormatter.categorize_feature("AWD System") == "performance"
        assert PremiumFeaturesFormatter.categorize_feature("Performance Exhaust") == "performance"
    
    def test_categorize_feature_default(self):
        """Test default categorization."""
        assert PremiumFeaturesFormatter.categorize_feature("Unknown Feature") == "convenience"
        assert PremiumFeaturesFormatter.categorize_feature("") == "convenience"
    
    def test_extract_features_from_attributes(self):
        """Test extracting features from attributes."""
        data = {
            "attributes": {
                "features": ["Navigation", "Heated Seats", "Sunroof"]
            }
        }
        features = PremiumFeaturesFormatter.extract_features(data)
        assert features == ["Navigation", "Heated Seats", "Sunroof"]
    
    def test_extract_features_from_options(self):
        """Test extracting features from options structure."""
        data = {
            "options": [
                {
                    "category": "Safety",
                    "options": [
                        {"name": "ABS Brakes"},
                        {"name": "Airbags"}
                    ]
                },
                {
                    "category": "Comfort",
                    "options": [
                        {"name": "Heated Seats"}
                    ]
                }
            ]
        }
        features = PremiumFeaturesFormatter.extract_features(data)
        assert features == ["ABS Brakes", "Airbags", "Heated Seats"]
    
    def test_extract_features_removes_duplicates(self):
        """Test that duplicate features are removed."""
        data = {
            "attributes": {
                "features": ["Navigation", "Heated Seats", "Navigation"]
            },
            "features": ["Heated Seats", "Sunroof"]
        }
        features = PremiumFeaturesFormatter.extract_features(data)
        assert features == ["Navigation", "Heated Seats", "Sunroof"]
    
    def test_format_premium_badge(self):
        """Test premium badge generation."""
        assert PremiumFeaturesFormatter.format_premium_badge(25) == "💎 *FULLY LOADED*"
        assert PremiumFeaturesFormatter.format_premium_badge(20) == "💎 *FULLY LOADED*"
        assert PremiumFeaturesFormatter.format_premium_badge(15) == "🏆 *PREMIUM PLUS*"
        assert PremiumFeaturesFormatter.format_premium_badge(10) == "⭐ *PREMIUM*"
        assert PremiumFeaturesFormatter.format_premium_badge(5) == "✨ *ENHANCED*"
        assert PremiumFeaturesFormatter.format_premium_badge(3) == ""
    
    def test_format_premium_summary(self):
        """Test premium summary generation."""
        data = {
            "attributes": {
                "features": [
                    "ABS Brakes",
                    "Airbags",
                    "Lane Departure Warning",
                    "Heated Seats",
                    "Navigation System"
                ]
            }
        }
        summary, count = PremiumFeaturesFormatter.format_premium_summary(data)
        assert count == 5
        assert "safety" in summary.lower() or "🛡️" in summary
    
    def test_format_features_section_empty(self):
        """Test formatting empty features list."""
        result = PremiumFeaturesFormatter.format_features_section([])
        assert result == ""
    
    def test_format_features_section_with_features(self):
        """Test formatting features section."""
        features = [
            "ABS Brakes",
            "Heated Seats",
            "Navigation System",
            "Sport Mode",
            "Leather Interior"
        ]
        result = PremiumFeaturesFormatter.format_features_section(features)
        
        assert "🌟 *PREMIUM FEATURES*" in result
        assert "🛡️" in result  # Safety icon
        assert "🛋️" in result  # Comfort icon
        assert "📱" in result  # Technology icon
        assert "⚡" in result  # Performance icon
        assert "ABS Brakes" in result
        assert "Heated Seats" in result
    
    def test_format_features_section_truncates_long_names(self):
        """Test that long feature names are truncated."""
        features = [
            "This is a very long feature name that should be truncated to fit the display"
        ]
        result = PremiumFeaturesFormatter.format_features_section(features)
        assert "..." in result
    
    def test_format_features_section_limits_per_category(self):
        """Test that features are limited per category."""
        features = [
            "ABS Brakes",
            "Airbags",
            "Lane Departure Warning",
            "Blind Spot Monitoring",
            "Collision Warning",
            "Parking Sensors",
            "Backup Camera"  # More than 5 safety features
        ]
        result = PremiumFeaturesFormatter.format_features_section(features)
        
        # Should only show 5 safety features
        lines = result.split("\n")
        safety_lines = [line for line in lines if line.strip().startswith("•")]
        assert len(safety_lines) <= 5
    
    def test_format_features_section_shows_more_indicator(self):
        """Test that a 'more features' indicator is shown for many features."""
        features = ["Feature " + str(i) for i in range(20)]
        result = PremiumFeaturesFormatter.format_features_section(features)
        assert "more premium features" in result