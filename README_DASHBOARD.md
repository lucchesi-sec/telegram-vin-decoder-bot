# VIN Decoder Web Dashboard (Next.js + shadcn/ui)

## Overview
A modern, responsive web dashboard built with Next.js 15, React 19, and shadcn/ui components. The dashboard provides a beautiful, user-friendly interface to visualize and manage VIN data with real-time updates and a sleek design.

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

## Features

### 📊 Dashboard Statistics
- **Real-time Metrics**: Live vehicle count, manufacturer diversity, and recent activity
- **Visual Cards**: Beautiful gradient-styled statistics cards
- **Auto-refresh**: Dynamic data updates

### 🔍 Vehicle Management
- **Advanced Search**: Filter by VIN, manufacturer, or model
- **Paginated Table**: Efficient data display with navigation
- **Quick Actions**: View details or delete records inline
- **Responsive Design**: Adapts perfectly to any screen size

### ➕ VIN Decoder
- **Modal Interface**: Clean, distraction-free VIN input
- **Validation**: Real-time 17-character VIN validation
- **Error Handling**: User-friendly error messages
- **Success Feedback**: Clear confirmation on successful decode

### 📱 Vehicle Details
- **Tabbed Interface**: Organized information display
  - **Basic Info**: VIN, manufacturer, model, year
  - **Technical**: Engine specs, fuel type
  - **Raw Data**: Complete JSON response viewer
- **Modern UI**: Clean card-based layout with shadcn/ui components

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