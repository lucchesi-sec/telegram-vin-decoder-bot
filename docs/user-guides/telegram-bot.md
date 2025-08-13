# IntelAuto Telegram Bot User Guide

The IntelAuto Telegram Bot provides instant access to our premium vehicle intelligence platform directly through Telegram. Perfect for quick VIN lookups on mobile devices.

## Getting Started

### Finding the Bot

1. Open Telegram
2. Search for `@IntelAutoBot` (or your configured bot name)
3. Start a conversation by clicking "Start" or sending `/start`

### Basic Commands

- `/start` - Initialize the bot and get welcome message
- `/help` - Display available commands and usage instructions
- `/about` - Learn about IntelAuto and our premium features
- `/stats` - View your usage statistics (premium feature)

## VIN Decoding

### Quick VIN Lookup

Simply send any valid VIN to get instant results:

```
1HGBH41JXMN109186
```

The bot will respond with:
- ✅ Basic vehicle information (Make, Model, Year)
- 🎯 **Premium Package Identification** (trim, options)
- 📊 Confidence scores and data sources
- 💰 Estimated market value (premium users)

### Batch Processing

Premium users can process multiple VINs at once:

```
/batch
1HGBH41JXMN109186
WBANE53578CT12345
JH4NA1157MT123456
```

## Premium Features

### Account Linking

Link your Telegram account to your IntelAuto dashboard:

```
/link YOUR_API_KEY
```

This unlocks:
- 📈 Enhanced analytics and history
- 🔍 Advanced vehicle comparisons
- 💾 VIN lookup history and exports
- ⚡ Higher rate limits

### Advanced Queries

Premium users can use natural language queries:

```
/analyze Tell me about luxury packages for 2023 BMW X5
```

### Export Options

Export your lookup history:

```
/export csv
/export json
/export pdf
```

## Understanding Results

### Basic Information
- **Make, Model, Year**: From NHTSA database
- **Body Type**: Sedan, SUV, Coupe, etc.
- **Engine**: Displacement, cylinders, fuel type

### Premium Package Intelligence
- **Trim Level**: Exact trim identification (e.g., "M340i xDrive")
- **Option Packages**: Specific packages (e.g., "Premium Package", "M Sport")
- **Equipment**: Individual options and features
- **Confidence Score**: How certain we are (0-100%)

### Market Intelligence (Premium)
- **Market Value**: Current estimated value
- **Value Trends**: Price movement over time
- **Comparable Vehicles**: Similar vehicles in market

## Data Sources & Accuracy

Our results combine multiple authoritative sources:

- 🏛️ **NHTSA**: Official government database
- 🔧 **Auto.dev**: Technical specifications
- 📊 **Market Data**: Auction and retail prices
- 🤖 **AI Analysis**: Our proprietary algorithms

### Confidence Levels

- **90-100%**: Highly confident - multiple sources agree
- **70-89%**: Good confidence - some discrepancies resolved
- **50-69%**: Moderate confidence - limited data available
- **Below 50%**: Low confidence - requires verification

## Rate Limits & Usage

### Free Tier
- 10 VIN lookups per day
- Basic vehicle information
- Standard response time

### Premium Tiers
- **Professional**: 100 VINs/day, package intelligence
- **Business**: 500 VINs/day, batch processing, exports
- **Enterprise**: Unlimited, priority support, custom features

## Privacy & Security

- 🔒 VIN lookups are encrypted in transit
- 🗑️ Chat history automatically deleted after 24 hours
- 👤 No personal information stored beyond Telegram user ID
- 📊 Usage statistics are anonymized

## Troubleshooting

### Common Issues

**"Invalid VIN format"**
- Ensure VIN is exactly 17 characters
- Use only letters and numbers (no special characters)
- Check for common mistakes (0 vs O, 1 vs I)

**"Rate limit exceeded"**
- Free users: Wait until tomorrow or upgrade
- Premium users: Contact support if limits seem incorrect

**"Service temporarily unavailable"**
- Our servers may be under maintenance
- Try again in a few minutes
- Check @IntelAutoStatus for updates

### Getting Help

- 💬 Send `/help` for quick assistance
- 📧 Contact support: support@intellauto.com
- 🌐 Visit our [Dashboard](https://dashboard.intellauto.com) for more tools
- 📚 Read our [FAQ](../technical/faq.md)

## Migration to Other Interfaces

Ready for more advanced features?

### Web Dashboard
- Visual vehicle comparisons
- Detailed analytics and reports
- Team collaboration features
- **[Get Started](web-dashboard.md)**

### REST API
- Integrate into your applications
- Bulk processing capabilities
- Real-time webhooks
- **[API Documentation](api-usage.md)**

## Community & Updates

- 📢 Follow @IntelAutoNews for platform updates
- 🎯 Join our [Community Group](https://t.me/IntelAutoCommunity)
- 🐛 Report bugs: /feedback followed by your message
- ⭐ Rate us in the [Telegram Bot Directory](https://core.telegram.org/bots)

---

*The IntelAuto Telegram Bot is part of the comprehensive IntelAuto Vehicle Intelligence Platform. For advanced features, visit our [Web Dashboard](https://dashboard.intellauto.com) or explore our [REST API](api-usage.md).*
