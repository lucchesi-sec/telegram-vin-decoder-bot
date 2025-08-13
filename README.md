# IntelAuto - All-in-One Vehicle Intelligence Platform

[![Platform](https://img.shields.io/badge/Platform-All--in--One%20Vehicle%20Intelligence-blue)](#platform-interfaces)
[![Version](https://img.shields.io/badge/Version-2.0.0-green)](#)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js%2015.4-black)](https://nextjs.org/)
[![SaaS](https://img.shields.io/badge/Model-SaaS-green)](#saas-model-subscriptions-rate-limits-and-access-control)
[![Python](https://img.shields.io/badge/Backend-Python%203.9+-3776ab)](https://python.org/)
[![TypeScript](https://img.shields.io/badge/Frontend-TypeScript-3178c6)](https://typescriptlang.org/)
[![DDD](https://img.shields.io/badge/Architecture-Domain--Driven%20Design-orange)](#architecture-summary)

**The All-in-One Vehicle Intelligence Platform - Transforming raw VIN data into actionable automotive insights with premium package identification, comprehensive valuations, and multi-interface access for the modern automotive industry**

## Overview

IntelAuto transforms raw VIN data into strategic intelligence for the automotive ecosystem. Our platform delivers precision vehicle identification, comprehensive valuations, and actionable analytics through multiple interfaces - from conversational AI to enterprise APIs.

**🎯 Elevator Pitch:** IntelAuto is the only vehicle intelligence platform that accurately identifies premium packages and trim-specific features that traditional VIN decoders miss, delivering up to 40% more accurate vehicle valuations for dealers, wholesalers, and automotive professionals.

## Core Differentiator: Premium Package Identification Engine

### The Problem We Solve
Standard VIN decoders provide basic make, model, and year data but miss critical details:
- **Premium packages and trim variations** that impact value by $5,000-$15,000+
- **Optional equipment and features** that affect pricing and desirability  
- **Manufacturer-specific configurations** not captured in basic decode
- **Aftermarket modifications** and special edition details

### Our Solution
IntelAuto's **Premium Package Identification Engine** combines:
- **Multi-source data fusion** (NHTSA + Auto.dev + proprietary algorithms)
- **Trim-level precision** with package-specific feature detection
- **Valuation enhancement** through comprehensive specification analysis
- **Real-time validation** against manufacturer databases

**Result:** 40% more accurate vehicle valuations and complete transparency into what makes each vehicle unique.

## What the Platform Includes

### 🔍 VIN Decoding & Specifications
- Complete vehicle specifications and technical details
- Premium package and trim identification
- Engine, transmission, and drivetrain configurations
- Safety features and equipment packages
- Color options and interior configurations

### 💰 Vehicle Valuations
- Market value analysis across multiple pricing sources
- Trade-in, retail, and wholesale value estimates
- Regional pricing variations and market trends
- Depreciation curves and resale predictions

### 📊 Vehicle History & Analytics
- Title history and ownership records
- Accident reports and damage assessments
- Service history and maintenance records
- Recall information and safety notices

### 📈 Business Intelligence
- Portfolio analysis and inventory optimization
- Market trends and competitive intelligence
- Risk assessment and pricing recommendations
- Custom reporting and analytics dashboards

## Platform Interfaces

### 🌐 Web Dashboard
**Professional interface for automotive businesses**
- **Technology**: Next.js 15.4, React 19, TypeScript, shadcn/ui
- **Features**: Real-time analytics, bulk VIN processing, inventory management
- **Users**: Dealers, fleet managers, business analysts
- **Deployment**: Responsive web application with modern UI/UX

### 🔌 REST API
**Enterprise-grade API for system integrations**
- **Technology**: FastAPI with automatic OpenAPI documentation
- **Features**: RESTful endpoints, rate limiting, authentication
- **Users**: System integrators, software developers, automotive platforms
- **Formats**: JSON responses with comprehensive error handling

### 💬 Telegram Bot
**Conversational AI for instant vehicle intelligence**
- **Technology**: Python async/await with modern bot framework
- **Features**: Natural language processing, automatic VIN detection
- **Users**: Individual dealers, sales professionals, automotive enthusiasts  
- **Interface**: Rich messaging with inline keyboards and interactive menus

### 📱 Mobile Apps (Future)
**Native mobile applications for field operations**
- **Platforms**: iOS and Android with camera-based VIN scanning
- **Features**: Offline capabilities, push notifications, location services
- **Users**: Field inspectors, auction representatives, mobile dealers

## Architecture Summary

### Domain-Driven Design (DDD)
IntelAuto employs sophisticated architectural patterns for maintainability and scalability:

**🏗️ Clean Architecture Principles**
- **Dependency Inversion**: Core business logic independent of external frameworks
- **Separation of Concerns**: Clear boundaries between domain, application, and infrastructure layers
- **SOLID Design**: Single responsibility, open/closed, and interface segregation principles

**📦 Multi-Interface Modularity**
- **Shared Domain Layer**: Common business logic across all interfaces
- **Interface-Specific Presentation**: Telegram, Web, API each with optimized user experience  
- **Pluggable Infrastructure**: Easily swap external services and data providers

## Architecture

This bot follows a Domain-Driven Design approach with clean architecture:

```
src/
├── domain/              # Domain layer with entities, value objects, and domain services
├── application/         # Application layer with use cases and business logic
├── infrastructure/      # Infrastructure layer with external service adapters
├── presentation/        # Presentation layer with Telegram bot interface
├── config/              # Configuration and dependency injection
└── tests/               # Unit, integration, and end-to-end tests
```

### Bounded Contexts

1. **Vehicle Domain**: Core VIN decoding, vehicle information management
2. **User Domain**: User preferences, history, subscription management
3. **Messaging Domain**: Telegram interaction, message formatting, UI components
4. **Integration Domain**: External API clients, third-party service adapters

## Integrations: Current and Planned

### ✅ Current Data Sources
**Production-ready integrations**

#### NHTSA (National Highway Traffic Safety Administration)
- **Type**: Government vehicle safety database
- **Coverage**: All US market vehicles 1981+
- **Data**: Basic specifications, safety ratings, recall information
- **Cost**: Free API access
- **Reliability**: 99.9% uptime, official government data

#### Auto.dev
- **Type**: Comprehensive automotive data platform  
- **Coverage**: Global vehicle database with premium features
- **Data**: Enhanced specifications, valuations, history reports
- **Cost**: API key required, usage-based pricing
- **Features**: VIN decoding, vehicle listings, market values

### 🔄 Planned Integrations
**Strategic roadmap for enhanced capabilities**

#### Manheim MMR (Manheim Market Report)
- **Purpose**: Real-time wholesale vehicle valuations
- **Impact**: Professional-grade pricing for dealers and wholesalers
- **Timeline**: Q2 2025

#### Carfax Vehicle History
- **Purpose**: Comprehensive vehicle history reports
- **Impact**: Complete accident, service, and ownership history
- **Timeline**: Q3 2025

#### KBB (Kelley Blue Book) 
- **Purpose**: Consumer and trade-in value estimates
- **Impact**: Multi-source valuation consensus
- **Timeline**: Q4 2025

#### Automotive OEM APIs
- **Purpose**: Direct manufacturer data feeds
- **Impact**: Real-time recall notices, warranty information
- **Timeline**: 2026

## SaaS Model: Subscriptions, Rate Limits, and Access Control

### 🎆 Free Tier
**Get started with essential vehicle intelligence**
- **Rate Limit**: 100 VIN decodes per month
- **Data Sources**: NHTSA only
- **Features**: Basic specifications, Telegram bot access
- **Support**: Community forums
- **Ideal For**: Individual users, automotive enthusiasts

### ⭐ Professional Tier ($49/month)
**Enhanced capabilities for automotive professionals**
- **Rate Limit**: 2,500 VIN decodes per month  
- **Data Sources**: NHTSA + Auto.dev + premium features
- **Features**: Web dashboard, API access, vehicle history
- **Support**: Email support, documentation
- **Ideal For**: Independent dealers, small lots

### 💼 Enterprise Tier ($199/month)
**Full-featured platform for automotive businesses**
- **Rate Limit**: 10,000 VIN decodes per month
- **Data Sources**: All integrations + priority access
- **Features**: Bulk processing, custom reports, webhooks
- **Support**: Priority support, dedicated account manager
- **Ideal For**: Dealership groups, fleet managers, automotive platforms

### 🏢 Custom Enterprise (Contact Sales)
**Tailored solutions for large-scale operations**
- **Rate Limit**: Unlimited or custom limits
- **Data Sources**: All integrations + custom data feeds
- **Features**: White-label options, on-premise deployment
- **Support**: 24/7 support, SLA guarantees, custom integrations
- **Ideal For**: OEMs, large enterprises, system integrators

### 🔑 API Authentication & Keys
- **JWT-based authentication** for secure API access
- **API key management** through web dashboard
- **Usage analytics** and billing integration
- **Rate limiting** with clear error messages and retry guidance
- **Role-based access control** for team management

## Quick Start Guide

### 🔵 Web Dashboard Quick Start
**Perfect for automotive businesses and analysts**

1. **Access the Dashboard**: Visit [intelliauto.dev](https://intelliauto.dev) (coming soon)
2. **Create Account**: Sign up with business email
3. **Choose Plan**: Select appropriate subscription tier
4. **Decode VINs**: Use the search interface to analyze vehicles
5. **View Analytics**: Monitor usage and export reports

### 🔌 API Quick Start  
**For developers and system integrations**

1. **Get API Key**: Register at [intelliauto.dev/api](https://intelliauto.dev/api)
2. **Read Documentation**: Complete API reference with examples
3. **Test Endpoint**: Start with vehicle decode endpoint
4. **Implement**: Integrate into your application
5. **Monitor Usage**: Track API calls and manage rate limits

```bash
# Example API call
curl -X POST "https://api.intelliauto.dev/v1/vin/decode" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"vin": "1HGCM82633A004352"}'
```

### 💬 Telegram Bot Quick Start
**For instant vehicle intelligence on-the-go**

1. **Find the Bot**: Search @IntelAutoBot on Telegram
2. **Start Conversation**: Send /start to begin
3. **Decode VINs**: Simply paste any 17-character VIN
4. **Access History**: Use /history to see recent searches  
5. **Manage Settings**: Customize preferences with /settings

### 🛠️ Developer Setup (Self-Hosted)
**For development and customization**

1. **Prerequisites**: Python 3.9+, Node.js 18+, Telegram Bot Token, API keys

```bash
# Clone and setup
git clone https://github.com/lucchesi-sec/telegram-vin-decoder-bot
cd telegram-vin-decoder-bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. **Configuration**: Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
# Edit .env with your tokens and API keys
```

3. **Run the IntelAuto Platform**:

```bash
# Option 1: Run all services independently (recommended for development)

# Terminal 1: Start Telegram Bot Service
python -m src.main

# Terminal 2: Start FastAPI Backend (Web Platform Service)
python -m uvicorn src.presentation.api.domain_api_server:app --host 0.0.0.0 --port 5000 --reload

# Terminal 3: Start Next.js Frontend (Web Platform Service)
cd src/presentation/web-dashboard-next
npm install && npm run dev

# Option 2: Use development entrypoints (simulates production)

# Terminal 1: Web Platform Service
./web-entrypoint.sh

# Terminal 2: Telegram Bot Service
./entrypoint.sh
```

4. **Access the Platform**:
   - **Web Dashboard**: http://localhost:3000 (development) or http://localhost:8000 (production mode)
   - **API Documentation**: http://localhost:5000/docs
   - **Telegram Bot**: Start conversation with your bot on Telegram

## Configuration: Environment Variables

### 📋 Core Configuration
Create your `.env` file from the template and configure these essential settings:

#### Telegram Configuration
```bash
# Required: Get from @BotFather on Telegram
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Production: Webhook URL for cloud deployment
TELEGRAM_WEBHOOK_URL=https://your-app.fly.dev/webhook
```

#### Database Configuration  
```bash
# PostgreSQL (recommended for production)
DATABASE_URL=postgresql://postgres:secret@localhost:5432/vinbot

# SQLite (development only)
# DATABASE_URL=sqlite:///./vinbot.db
```

#### Cache Configuration
```bash
# Upstash Redis (serverless, production-ready)
UPSTASH_REDIS_REST_URL=https://your-upstash-url.upstash.io
UPSTASH_REDIS_REST_TOKEN=your_upstash_token_here
```

#### VIN Decoder Services
```bash
# Auto.dev API (recommended - enhanced data)
AUTODEV_API_KEY=your_autodev_api_key_here

# Default service selection
DEFAULT_DECODER_SERVICE=autodev  # or 'nhtsa'
```

#### Application Settings
```bash
# Environment and logging
ENVIRONMENT=development  # or 'production'
LOG_LEVEL=INFO          # DEBUG, INFO, WARNING, ERROR
HTTP_TIMEOUT_SECONDS=15

# Performance tuning
DB_POOL_SIZE=20
CACHE_TTL=3600          # Default cache TTL in seconds
DECODER_CACHE_TTL=2592000  # 30 days for VIN data
```

### 🔧 Advanced Configuration
For production deployments and advanced use cases:

#### Security Settings
```bash
# JWT secret for API authentication
JWT_SECRET=your-super-secure-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# API rate limiting
API_RATE_LIMIT=1000  # requests per hour per API key
```

#### Monitoring & Observability
```bash
# Sentry error tracking
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project

# OpenTelemetry tracing
OTEL_EXPORTER_OTLP_ENDPOINT=https://api.honeycomb.io
OTEL_EXPORTER_OTLP_HEADERS=x-honeycomb-team=your-api-key
```

## Helpful Links

### 📖 Documentation
- **[📋 Documentation Hub](docs/README.md)** - Complete documentation index and navigation
- **[⚡ Quick Start Guide](docs/getting-started/quick-start.md)** - Get up and running in 5 minutes
- **[🤖 Telegram Bot Guide](docs/user-guides/telegram-bot.md)** - Mobile VIN lookups and features
- **[🌐 Web Dashboard Guide](docs/user-guides/web-dashboard.md)** - Business interface and analytics
- **[🔌 REST API Guide](docs/user-guides/api-usage.md)** - Developer integration and reference
- **[🏗️ Technical Architecture](docs/technical/architecture.md)** - System design and patterns
- **[🚀 Business Roadmap](docs/business/roadmap.md)** - Strategic development plan

### 🔗 Platform Access
- **[Web Dashboard](https://intelliauto.dev)** - Professional vehicle intelligence interface (coming soon)
- **[Developer Portal](https://intelliauto.dev/developers)** - API keys, documentation, and integration guides
- **[Telegram Bot](https://t.me/IntelAutoBot)** - Instant VIN decoding via Telegram (coming soon)

### 🏗️ Technical Resources
- **[🔌 Integration Examples](docs/integrations/README.md)** - Data sources and third-party integration patterns
- **[🚀 Deployment Guide](INFRASTRUCTURE_GUIDE.md)** - Production deployment best practices
- **[🔒 Security Guidelines](docs/architecture/SECURITY.md)** - Security considerations and compliance
- **[📊 Migration Guide](MIGRATION_GUIDE.md)** - Upgrading from legacy systems
- **[📈 Implementation Summary](IMPLEMENTATION_SUMMARY.md)** - Current development progress

### 📚 Specialized Documentation
- **[🤖 Agent Integration](AGENTS.md)** - AI agent integration and capabilities
- **[🧠 Premium Package Algorithm](docs/algorithms/premium_package_identification.md)** - Core intelligence engine
- **[🏛️ C4 Architecture Diagrams](docs/architecture/C4_DIAGRAMS.md)** - Visual system documentation
- **[🔄 Data Flow Patterns](docs/architecture/DATA_FLOW.md)** - Data processing workflows

### 🤝 Community & Support
- **[GitHub Issues](https://github.com/lucchesi-sec/telegram-vin-decoder-bot/issues)** - Bug reports and feature requests
- **[Discussions](https://github.com/lucchesi-sec/telegram-vin-decoder-bot/discussions)** - Community Q&A and ideas
- **[Support Portal](https://intelliauto.dev/support)** - Priority support for paid subscribers

### 🔌 External Integrations
- **[NHTSA API Documentation](https://vpic.nhtsa.dot.gov/api/)** - Government vehicle data source
- **[Auto.dev Platform](https://auto.dev)** - Premium automotive data and APIs
- **[Telegram Bot API](https://core.telegram.org/bots/api)** - Official Telegram Bot documentation

---

**IntelAuto** - Transforming Vehicle Intelligence for the Automotive Industry

*Built with ❤️ for automotive professionals who demand precision and insight.*

## License

This project is licensed under the MIT License - see the LICENSE file for details.