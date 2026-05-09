# Civic Tech App - Architecture Plan

## Overview
A real-time map application tracking road repairs and water network outages in Sofia, Bulgaria. Data flows from public utility websites → Python scraper → Persistent storage → Next.js frontend → Interactive map visualization.

---

## Data Flow Architecture

### Phase 1: Data Collection (Backend)
```
Public Utility Websites
    ↓ (HTTP requests)
Python Scraper (BeautifulSoup)
    ↓ (Parse HTML)
Data Cleaning & Validation
    ↓ (Geocode addresses → lat/lon)
Persistent Storage (JSON file or Supabase)
```

### Phase 2: Frontend Display (Next.js)
```
Next.js API Route (fetches from storage)
    ↓ (JSON response)
React Component (parses data)
    ↓ (Renders map markers)
React-Leaflet + OpenStreetMap
    ↓ (Interactive map with tooltips)
User Browser
```

---

## Step-by-Step Flow

### 1. **Python Scraper Execution** (Manual or Cron Job)
   - Scraper script (`scrapers/road_repairs_scraper.py`) runs on a schedule
   - Sends HTTP requests to target utility websites
   - Parses HTML tables/pages using BeautifulSoup
   - Extracts: street name, disruption type, start date, expected end date
   - Geocodes addresses to latitude/longitude coordinates
   - Validates data quality (removes duplicates, incomplete entries)
   - Saves to `data/disruptions.json`

### 2. **Data Storage**
   - **MVP Option**: Static JSON file (`data/disruptions.json`)
   - **Scaling Option**: Supabase PostgreSQL table with real-time subscriptions
   - Timestamp added to track when data was last updated

### 3. **Frontend Data Retrieval**
   - Next.js API route reads from storage (e.g., `/api/disruptions`)
   - Returns paginated or filtered results based on query parameters
   - Adds caching headers for performance

### 4. **Map Rendering**
   - React component fetches data from API route on mount
   - Creates Leaflet markers grouped by disruption type (colors/icons)
   - Users can click markers to see details in popup
   - Map is centered on Sofia (42.6977°N, 23.3219°E)
   - Optional: Add filters by disruption type, neighborhood

---

## Technology Decisions

### Why This Architecture?
- **Separated Python Backend**: Keeps scraper logic independent; can run as Cron job on any server
- **JSON MVP**: Simple, no database setup required for initial launch
- **React-Leaflet**: Light, open-source, great for customization
- **OpenStreetMap**: Free, no API keys needed
- **Next.js API Routes**: Unified backend; no separate Express server
- **Supabase Path**: Ready for real-time features later (subscriptions)

---

## Deployment Strategy

### Option A: Minimal Deployment (MVP)
1. Host Next.js frontend on **Vercel** (free tier)
2. Store `data/disruptions.json` in repo or Vercel KV
3. Run Python scraper locally or on a cheap VPS with cron job
4. Scraper pushes updates to Git or direct API call

### Option B: Production-Ready
1. Next.js frontend on **Vercel**
2. Supabase PostgreSQL for data
3. Python scraper on **AWS Lambda** or **Render Cron Job**
4. Real-time updates via Supabase subscriptions

---

## File Structure

```
civic-tech-app/
├── docs/
│   └── ARCHITECTURE.md (this file)
├── backend/
│   ├── requirements.txt
│   ├── scrapers/
│   │   ├── road_repairs_scraper.py
│   │   ├── water_outages_scraper.py
│   │   └── utils.py (geocoding, helpers)
│   └── data/
│       ├── disruptions.json (output)
│       └── locations.json (reference data)
├── frontend/
│   ├── app/
│   │   ├── page.tsx (home/map page)
│   │   ├── api/disruptions.ts (API route)
│   │   └── layout.tsx
│   ├── components/
│   │   ├── Map.tsx (React-Leaflet wrapper)
│   │   ├── Legend.tsx
│   │   └── DisruptionPopup.tsx
│   ├── public/
│   └── next.config.js
└── README.md
```

---

## Key Considerations

### Data Freshness
- Run scraper every **4-6 hours** to balance freshness vs. rate limits
- Add `last_updated` timestamp to data for UI display

### Geocoding
- Use **Nominatim** (OpenStreetMap's free geocoding service) via `geopy` library
- Cache results to reduce API calls

### Rate Limiting
- Implement delays between HTTP requests in scraper (use `time.sleep()`)
- Respect `robots.txt` and utility sites' ToS

### Error Handling
- Gracefully handle missing/malformed HTML
- Log scraper errors to a file for monitoring
- Fallback to cached data if scrape fails

### Privacy & Legal
- No personal data collected; only public disruption info
- Ensure compliance with Bulgaria's data protection laws

---

## Next Steps
1. Set up Next.js project with Tailwind CSS
2. Create Python virtual environment and install dependencies
3. Build and test Python scraper on demo HTML
4. Implement React-Leaflet map component
5. Connect scraper output to frontend API route
6. Deploy to Vercel and add cron job
