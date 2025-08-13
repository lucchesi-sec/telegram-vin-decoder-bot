# IntelAuto Web Dashboard - Primary Business Interface

## 📚 Related Documentation
- **[📖 Main README](README.md)** - All-in-One Vehicle Intelligence Platform overview
- **[🏗️ Architecture Guide](ARCHITECTURE.md)** - Multi-interface modular platform architecture
- **[📋 Documentation Hub](docs/README.md)** - Complete documentation index
- **[🔗 API Documentation](docs/api/README.md)** - Enterprise-grade REST API reference and integration guides
- **[🔌 Integrations Guide](docs/integrations/README.md)** - Data sources and third-party integrations
- **[🚀 Development Roadmap](FUTURE_PLANS.md)** - SaaS roadmap with premium package intelligence
- **[🧪 Testing Guide](README_TESTING.md)** - Quality assurance and testing strategies

## Overview
**The IntelAuto Web Dashboard is the primary business interface for our All-in-One Vehicle Intelligence Platform.** Built with Next.js 15, React 19, and shadcn/ui components, it provides automotive professionals with comprehensive vehicle analysis, premium package identification, and business intelligence through an intuitive, modern web experience. The dashboard is powered by our enterprise-grade REST API, delivering real-time vehicle intelligence, market valuations, and confidence-scored data.

## Technology Stack

### Frontend
- **Framework**: Next.js 15.4 (App Router)
- **UI Library**: React 19 with TypeScript
- **Component Library**: shadcn/ui (built on Radix UI primitives)
- **Styling**: Tailwind CSS 3.4
- **State Management**: React Hooks
- **Icons**: Lucide React
- **Animations**: Tailwind Animate

### Backend (API)
- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy
- **API Format**: RESTful JSON

### External Dependencies
- **Auto.dev API**: Primary data source for vehicle specifications and intelligence
- **NHTSA API**: Government vehicle safety database for basic specifications
- **Market Data Services**: Future pricing and valuation information integrations

## Core Features

### 🚗 Package Intelligence Dashboard (Primary Interface)
- **Comprehensive Vehicle Breakdown**: Detailed package information with specifications, equipment lists, and feature sets
- **Equipment Analysis**: Complete standard and optional equipment categorization with availability indicators (Std./Opt./N/A)
- **Confidence Scoring**: Data reliability indicators showing source confidence levels and data completeness
- **Multi-Source Integration**: Combines NHTSA and Auto.dev data sources for comprehensive vehicle coverage
- **Package Comparison**: Side-by-side vehicle package analysis and feature comparisons
- **Export Capabilities**: Download vehicle intelligence reports in multiple formats (PDF, CSV, JSON)

### 💰 Market Intelligence Panels
- **Market Valuation**: MSRP, invoice pricing, and delivery charges when available
- **Historical Pricing**: Price trends and market value analysis over time
- **Regional Variations**: Market-specific pricing and availability data
- **Warranty Information**: Complete warranty coverage details by type, miles, and duration

### 📊 Dashboard Analytics
- **Real-time Metrics**: Live vehicle count, manufacturer diversity, and recent activity
- **Intelligence Insights**: Data quality scores, source coverage, and confidence analytics
- **Visual Cards**: Beautiful gradient-styled statistics cards with intelligence KPIs
- **Auto-refresh**: Dynamic data updates with source reliability tracking

### 🔍 Advanced Vehicle Management
- **Intelligent Search**: Filter by VIN, manufacturer, model, equipment, or technical specifications
- **Smart Pagination**: Efficient data display with advanced filtering and sorting
- **Quick Actions**: View detailed intelligence, compare packages, or export data inline
- **Responsive Design**: Adapts perfectly to any screen size with mobile-optimized intelligence views

### 🎯 Enhanced VIN Decoder
- **Intelligence-First Interface**: Clean, focused VIN input with real-time package preview
- **Multi-API Validation**: 17-character VIN validation with fallback to international decoding
- **Smart Error Handling**: Context-aware error messages with alternative data suggestions
- **Success Analytics**: Detailed confirmation with data confidence scores and source attribution

### 📱 Comprehensive Vehicle Intelligence
- **Multi-Tab Intelligence Display**: Organized information with enhanced data depth
  - **Package Overview**: VIN, manufacturer, model, year, trim, and package details
  - **Equipment Intelligence**: Complete standard/optional equipment breakdown with categories
  - **Technical Specifications**: Engine, transmission, performance, and efficiency data
  - **Market Data**: Pricing, warranties, and availability information
  - **Color & Options**: Interior/exterior color options and trim selections
  - **Source Attribution**: Data confidence indicators and source reliability metrics
  - **Raw Intelligence**: Complete JSON response viewer with all API data
- **Modern Intelligence UI**: Clean card-based layout with shadcn/ui components optimized for data density

## Installation & Setup

### Prerequisites
- Node.js 20+ and npm
- Python 3.9+ (for backend API)
- PostgreSQL (optional, SQLite for development)

### Frontend Setup

1. Navigate to the dashboard directory:
```bash
cd src/presentation/web-dashboard-next
```

2. Install dependencies:
```bash
npm install
```

3. Create environment configuration:
```bash
# Create .env.local file
echo "NEXT_PUBLIC_API_URL=http://localhost:5000" > .env.local
```

4. Run development server:
```bash
npm run dev
```

The dashboard will be available at http://localhost:3000

### Backend API Setup

1. Ensure the main bot application is configured:
```bash
cp .env.example .env
# Edit .env with your configuration
```

2. Run the FastAPI backend:
```bash
python src/presentation/web_dashboard/run_dashboard.py
```

API will be available at http://localhost:5000

## API Dependencies & Configuration

### Data Source Integration
The Vehicle Intelligence Dashboard integrates with multiple data sources:

1. **Auto.dev API** (Primary): Enhanced vehicle specifications and premium data
2. **NHTSA API** (Fallback): Government vehicle database for basic specifications

**Configure environment variables**:
```bash
# Backend configuration (.env file)
AUTODEV_API_KEY=your_autodev_api_key_here

# NHTSA API (free, no key required)
DEFAULT_DECODER_SERVICE=autodev  # or 'nhtsa'

# Database
DATABASE_URL=postgresql://postgres:secret@localhost:5432/vinbot

# Cache (recommended)
UPSTASH_REDIS_REST_URL=https://your-upstash-url.upstash.io
UPSTASH_REDIS_REST_TOKEN=your_upstash_token_here
```

### Environment Configuration Requirements

#### Required Variables
| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | ✅ Yes |
| `NEXT_PUBLIC_API_URL` | Frontend API endpoint URL | ✅ Yes |

#### Recommended Variables
| Variable | Description | Default |
|----------|-------------|--------|
| `AUTODEV_API_KEY` | Auto.dev API key for enhanced data | *(none)* |
| `UPSTASH_REDIS_REST_URL` | Redis cache URL | *(none)* |
| `UPSTASH_REDIS_REST_TOKEN` | Redis cache token | *(none)* |
| `DEFAULT_DECODER_SERVICE` | Primary service selection | `autodev` |
| `LOG_LEVEL` | Application logging level | `INFO` |

### API Rate Limits & Best Practices
- **Auto.dev API**: Premium service with usage-based pricing
- **NHTSA API**: Free government service with reasonable limits
- **Caching**: Dashboard implements intelligent caching to minimize API calls
- **Fallback Strategy**: NHTSA used when Auto.dev is unavailable or not configured
- **Error Handling**: Comprehensive error handling with user-friendly messages

## Navigation & Documentation

### 📚 API Documentation
- **IntelAuto API Docs**: [http://localhost:5000/docs](http://localhost:5000/docs) - FastAPI Swagger UI
- **Auto.dev API Docs**: [https://auto.dev/docs](https://auto.dev/docs) - Premium automotive data
- **NHTSA API Docs**: [https://vpic.nhtsa.dot.gov/api/](https://vpic.nhtsa.dot.gov/api/) - Government vehicle data
- **ReDoc Interface**: [http://localhost:5000/redoc](http://localhost:5000/redoc) - Alternative API docs

### 🔗 Integration Resources
- **IntelAuto Dashboard**: [https://dashboard.intellauto.com](https://dashboard.intellauto.com) *(coming soon)*
- **Auto.dev Portal**: [https://auto.dev](https://auto.dev) - Get API keys for premium data
- **GitHub Repository**: [https://github.com/lucchesi-sec/telegram-vin-decoder-bot](https://github.com/lucchesi-sec/telegram-vin-decoder-bot)
- **Testing VINs**: Use `1HGBH41JXMN109186` (Honda) or `WBAFR7C57CC811956` (BMW) for testing

### 🎯 Quick Links
- **Main Dashboard**: `http://localhost:3000` (when running locally)
- **API Health Check**: `http://localhost:5000/health`
- **API Documentation**: `http://localhost:5000/docs` (FastAPI auto-generated docs)
- **Vehicle Intelligence**: Access comprehensive vehicle data with confidence scoring
- **Package Comparison**: Compare multiple vehicles side-by-side with detailed breakdowns

## Project Structure

```
web-dashboard-next/
├── app/                        # Next.js App Router
│   ├── page.tsx               # Main dashboard page (client component)
│   ├── layout.tsx             # Root layout with metadata
│   └── globals.css            # Global styles and Tailwind directives
├── components/
│   └── ui/                    # shadcn/ui components
│       ├── button.tsx         # Button variants and styles
│       ├── card.tsx           # Card container components
│       ├── dialog.tsx         # Modal dialog system
│       ├── table.tsx          # Data table components
│       ├── tabs.tsx           # Tab navigation
│       ├── input.tsx          # Form input fields
│       └── badge.tsx          # Status/tag badges
├── lib/
│   └── utils.ts               # Utility functions (cn for className merging)
├── public/                    # Static assets
├── .env.local                 # Environment variables
├── tailwind.config.ts         # Tailwind configuration
├── tsconfig.json              # TypeScript configuration
└── package.json               # Dependencies and scripts
```

## UI Components (shadcn/ui)

The dashboard uses shadcn/ui, a modern component library built on:
- **Radix UI**: Unstyled, accessible component primitives
- **Tailwind CSS**: Utility-first styling
- **Class Variance Authority**: Component variant management

### Component Usage Examples

```typescript
// Button with variants
<Button variant="default">Primary Action</Button>
<Button variant="outline">Secondary Action</Button>
<Button variant="destructive">Delete</Button>

// Card components
<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
    <CardDescription>Description</CardDescription>
  </CardHeader>
  <CardContent>Content here</CardContent>
</Card>

// Dialog (Modal)
<Dialog>
  <DialogTrigger>Open</DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Title</DialogTitle>
    </DialogHeader>
    {/* Content */}
  </DialogContent>
</Dialog>
```

## API Endpoints

The dashboard communicates with these REST endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/vehicles` | List vehicles (paginated) |
| GET | `/api/stats` | Dashboard statistics |
| POST | `/api/decode` | Decode new VIN |
| DELETE | `/api/vehicles/:id` | Delete vehicle |
| GET | `/health` | Health check |

### Request/Response Examples

```typescript
// Get vehicles (paginated)
GET /api/vehicles?page=1&limit=10
Response: {
  vehicles: Vehicle[],
  total_pages: number
}

// Decode VIN
POST /api/decode
Body: { vin: "1HGCM82633A004352" }
Response: { success: boolean, vehicle?: Vehicle }

// Get statistics
GET /api/stats
Response: {
  total_vehicles: number,
  unique_manufacturers: number,
  recent_decodes: number
}
```

## Development

### Available Scripts

```bash
# Development server with hot reload
npm run dev

# Production build
npm run build

# Start production server
npm start

# Run linting
npm run lint

# Type checking (if configured)
npm run type-check
```

### Adding New shadcn/ui Components

```bash
# Add individual components
npx shadcn@latest add [component-name]

# Examples
npx shadcn@latest add select
npx shadcn@latest add toast
npx shadcn@latest add dropdown-menu
```

## Styling & Theming

### Color Scheme
The dashboard uses a modern gradient theme:
- **Primary Gradient**: Purple (`#667eea`) to Pink (`#764ba2`)
- **Background**: White with subtle shadows
- **Accents**: Purple/blue for interactive elements

### Tailwind Configuration
Key customizations in `tailwind.config.ts`:
- CSS variables for dynamic theming
- Animation utilities via tailwind-animate
- Custom color palette
- Responsive breakpoints

### Dark Mode (Ready)
The infrastructure for dark mode is in place:
- CSS variables defined for both light and dark themes
- Toggle can be added using Next.js themes

## Performance Optimizations

### Next.js Features
- **Server Components**: Used by default for static content
- **Client Components**: Only for interactive features (marked with "use client")
- **Automatic Code Splitting**: Per-route JavaScript bundles
- **Image Optimization**: Next/Image component (when needed)
- **Font Optimization**: System fonts for fast loading

### Best Practices
- Minimal client-side JavaScript
- Efficient re-renders with React hooks
- Debounced search input
- Paginated data fetching
- Optimized bundle size with tree shaking

## Deployment

### Production Build

1. Build the Next.js application:
```bash
cd src/presentation/web-dashboard-next
npm run build
```

2. Start the production server:
```bash
npm start
```

### Docker Deployment

Create a `Dockerfile`:
```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package*.json ./
RUN npm ci --production
EXPOSE 3000
CMD ["npm", "start"]
```

Build and run:
```bash
docker build -t vin-dashboard .
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://api:5000 vin-dashboard
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:5000` |
| `PORT` | Server port | `3000` |

## Browser Support

The dashboard supports all modern browsers:
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Kill process on port 3000
   lsof -ti:3000 | xargs kill -9
   ```

2. **Module not found errors**
   ```bash
   # Clear cache and reinstall
   rm -rf node_modules .next
   npm install
   ```

3. **API connection issues**
   - Verify `NEXT_PUBLIC_API_URL` in `.env.local`
   - Ensure backend is running on correct port
   - Check CORS settings in FastAPI

## Migration from Legacy Dashboard

### What Changed
- **From**: Vanilla JS + HTML templates
- **To**: React + Next.js + TypeScript
- **UI**: Custom CSS → Tailwind CSS + shadcn/ui
- **State**: DOM manipulation → React hooks
- **Build**: None → Webpack (via Next.js)

### Benefits
- ✅ Type safety with TypeScript
- ✅ Component reusability
- ✅ Better performance
- ✅ Modern developer experience
- ✅ Easier maintenance
- ✅ Consistent UI with shadcn/ui

## Contributing

1. Follow the existing code style
2. Use shadcn/ui components when possible
3. Keep components small and focused
4. Write TypeScript interfaces for data models
5. Test on multiple screen sizes

## License

Same as main project - see root LICENSE file.

---

*Dashboard powered by Next.js, React, and shadcn/ui*