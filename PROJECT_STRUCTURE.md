backend/
├── README.md
│   └── Quick reference for backend setup
├── requirements.txt
│   └── Python dependencies:
│       - requests (HTTP client)
│       - beautifulsoup4 (HTML parsing)
│       - geopy (geocoding)
│       - python-dotenv (environment variables)
├── scrapers/
│   ├── __init__.py (empty, makes it a package)
│   ├── road_repairs_scraper.py
│   │   └── Main scraper class RoadsDisruptionScraper
│   │       - geocode_address() - Convert address to lat/lon
│   │       - fetch_html() - Download webpage
│   │       - parse_html_table() - Extract data from HTML
│   │       - scrape_demo_data() - Demo data for testing
│   │       - process_disruptions() - Enrich with coordinates
│   │       - save_to_json() - Write to output file
│   │       - run() - Main execution method
│   ├── utils.py
│   │   └── Utility functions:
│   │       - safe_get_text() - Extract text safely
│   │       - is_valid_date() - Validate date formats
│   │       - is_valid_coordinates() - Check lat/lon bounds
│   │       - remove_duplicates() - Deduplicate entries
│   │       - validate_disruption() - Validate data integrity
│   │       - retry_request() - HTTP with retry logic
│   └── water_outages_scraper.py (TODO)
│       └── Similar structure for water network data
└── data/
    ├── disruptions.json
    │   └── OUTPUT: Current disruptions (updated by scraper)
    │       {
    │         "timestamp": "2024-05-15T10:00:00",
    │         "count": 3,
    │         "disruptions": [
    │           {
    │             "id": "vasil_levski_blvd_...",
    │             "street": "Vasil Levski Blvd",
    │             "disruption_type": "Road works",
    │             "start_date": "2024-05-15",
    │             "end_date": "2024-05-20",
    │             "latitude": 42.6987,
    │             "longitude": 23.3213,
    │             "scraped_at": "2024-05-15T10:00:00"
    │           },
    │           ...
    │         ]
    │       }
    ├── locations.json (TODO)
    │   └── Reference data: Known streets with coordinates
    └── raw_html/ (TODO)
        └── Cache of downloaded HTML for debugging


frontend/
├── .env.example
│   └── Template environment variables
├── .gitignore
│   └── Excludes: .next/, node_modules/, *.log
├── .next/ (git-ignored)
│   └── Build output (generated)
├── node_modules/ (git-ignored)
│   └── Installed packages (generated)
├── public/ (optional)
│   └── Static assets (images, icons, etc.)
├── app/
│   ├── layout.tsx
│   │   └── Root HTML structure
│   │       - Metadata (title, description)
│   │       - Providers (context)
│   │       - children rendering
│   ├── page.tsx
│   │   └── Main map page (/)
│   │       - Header with title
│   │       - Dynamic Map component
│   │       - Loading state
│   ├── globals.css
│   │   └── Global Tailwind styles + Leaflet overrides
│   ├── providers.tsx
│   │   └── React context providers (currently empty)
│   └── api/
│       └── disruptions/
│           └── route.ts
│               ├── GET /api/disruptions
│               │   - Query: ?type=..., ?limit=...
│               │   - Response: DisruptionResponse JSON
│               │   - Caching: 5 minutes
│               └── POST /api/disruptions
│                   - Upload from scraper
│                   - Write to backend/data/disruptions.json
│                   - TODO: Add authentication
├── components/
│   ├── Map.tsx
│   │   └── Main Leaflet map component
│   │       - Centered on Sofia (42.6977, 23.3219)
│   │       - Fetches disruptions from /api
│   │       - Renders markers with color-coded icons
│   │       - Red markers: Road works
│   │       - Blue markers: Water-related
│   │       - Auto-refresh every 5 minutes
│   │       - Shows loading state
│   │       - Error handling
│   ├── Legend.tsx
│   │   └── Filter & legend panel
│   │       - "All" button to show/hide filter
│   │       - Type-specific filter buttons
│   │       - Color dots matching marker icons
│   │       - Count display (visible vs total)
│   └── DisruptionPopup.tsx
│       └── Content inside marker popup
│           - Street name (bold)
│           - Disruption type (badge)
│           - Start/end dates
│           - Last updated time
├── lib/ (optional, for future use)
│   └── supabase.ts (TODO)
│       └── Supabase client initialization
├── package.json
│   └── Dependencies:
│       - next (Next.js framework)
│       - react, react-dom (React)
│       - leaflet (mapping library)
│       - react-leaflet (Leaflet React wrapper)
│       - tailwindcss (styling)
│       - Dev: typescript, @types/*, autoprefixer, postcss
├── next.config.js
│   └── Next.js configuration (webpack, etc.)
├── tailwind.config.js
│   └── Tailwind CSS theme & plugins
├── tsconfig.json
│   └── TypeScript configuration
│       - Path aliases: @/* → ./*
│       - Strict mode enabled
│       - Target: ES2020
└── postcss.config.mjs
    └── PostCSS + Tailwind + Autoprefixer


docs/
├── ARCHITECTURE.md
│   └── System design & data flow
│       - Detailed architecture diagrams
│       - Step-by-step flow explanation
│       - Technology decisions
│       - Deployment strategy
│       - Key considerations
├── SETUP.md
│   └── Local development setup guide
│       - Prerequisites (Node, Python)
│       - Backend setup (venv, dependencies)
│       - Frontend setup (npm install, dev server)
│       - Testing the connection
│       - Common issues & fixes
│       - Advanced deployment options
└── DEPLOYMENT.md
    └── Production deployment guide
        - Architecture overview diagram
        - Option 1: Simple (MVP)
          * Vercel + GitHub Actions
          * Free tier
        - Option 2: Production
          * Vercel + Supabase + AWS Lambda
          * Monitoring & alerts
        - Option 3: Advanced
          * Multi-region, real-time updates
        - Checklist & monitoring
        - Performance optimization
        - Rollback plan
        - Cost estimation


ROOT FILES:
├── README.md
│   └── Project overview
│       - Features & tech stack
│       - Quick start (3 commands)
│       - API endpoint documentation
│       - Configuration
│       - Next steps & roadmap
│       - Links to docs/
└── .gitignore
    └── Excludes: backend/.next, backend/node_modules, __pycache__, .env.local

---

KEY FILES TO START WITH:

1. **First-time setup:** docs/SETUP.md
2. **Understand the architecture:** docs/ARCHITECTURE.md
3. **Run the scraper:** python backend/scrapers/road_repairs_scraper.py
4. **Start the frontend:** npm run dev (from frontend/)
5. **Check output:** backend/data/disruptions.json
6. **View the map:** http://localhost:3000

---

DATA FLOW:

1. Python Scraper (backend/scrapers/road_repairs_scraper.py)
   ↓ (processes data)
2. JSON Output (backend/data/disruptions.json)
   ↓ (via git push or direct API call)
3. Next.js API Route (frontend/app/api/disruptions/route.ts)
   ↓ (reads from backend or Supabase)
4. React Component (frontend/components/Map.tsx)
   ↓ (fetches from API)
5. Leaflet Map (rendered in browser)
   ↓ (user interacts)
6. Browser (Sofia Civic Tech app displayed)

---

NEXT STEPS:

[ ] Run local setup (SETUP.md step 1-3)
[ ] Test scraper with demo data
[ ] View demo map at http://localhost:3000
[ ] Customize scraper for real websites
[ ] Deploy to Vercel
[ ] Set up Supabase (optional)
[ ] Deploy scraper to Lambda (optional)

Good luck! 🚀
