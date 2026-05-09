# Civic Tech App - Sofia Road & Water Network Tracker

A clean, user-friendly web application for citizens to track road repairs and water network outages in Sofia, Bulgaria.

## 🏗️ Project Structure

```
civic-tech-app/
├── docs/
│   └── ARCHITECTURE.md          # Detailed architecture & data flow
├── backend/
│   ├── scrapers/
│   │   ├── road_repairs_scraper.py   # Main scraper logic
│   │   └── utils.py (TODO)           # Geocoding, helpers
│   ├── data/
│   │   ├── disruptions.json          # Output data file
│   │   └── locations.json (TODO)     # Reference locations
│   └── requirements.txt              # Python dependencies
└── frontend/
    ├── app/
    │   ├── page.tsx                  # Main map page
    │   ├── layout.tsx                # Root layout
    │   ├── globals.css               # Global styles
    │   └── api/
    │       └── disruptions/route.ts  # API endpoint
    ├── components/
    │   ├── Map.tsx                   # React-Leaflet map
    │   ├── Legend.tsx                # Filter & legend
    │   └── DisruptionPopup.tsx       # Popup content
    ├── package.json
    ├── next.config.js
    ├── tailwind.config.js
    └── tsconfig.json
```

---

## 🚀 Quick Start

### 1. Backend Setup (Python Scraper)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python scrapers/road_repairs_scraper.py
```

This generates `backend/data/disruptions.json` with sample data.

### 2. Frontend Setup (Next.js)

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 📡 API Endpoints

### GET `/api/disruptions`
Fetches all current disruptions.

**Query Parameters:**
- `type` - Filter by disruption type (e.g., `?type=Road%20works`)
- `limit` - Max results to return (default: 100)

**Response:**
```json
{
  "timestamp": "2024-05-15T10:00:00",
  "count": 3,
  "disruptions": [
    {
      "id": "vasil_levski_blvd_1715760000",
      "street": "Vasil Levski Blvd",
      "disruption_type": "Road works",
      "start_date": "2024-05-15",
      "end_date": "2024-05-20",
      "latitude": 42.6987,
      "longitude": 23.3213,
      "scraped_at": "2024-05-15T10:00:00"
    }
  ]
}
```

### POST `/api/disruptions`
Upload new disruption data (called by Python scraper).

**Request Body:**
```json
{
  "disruptions": [
    {
      "id": "...",
      "street": "...",
      "disruption_type": "...",
      "start_date": "...",
      "end_date": "...",
      "latitude": 42.6977,
      "longitude": 23.3219,
      "scraped_at": "..."
    }
  ]
}
```

---

## 🗺️ Features

- **Interactive Leaflet Map** - Centered on Sofia with color-coded markers
- **Real-time Data** - Refreshes every 5 minutes
- **Filter by Type** - Road works, water repairs, etc.
- **Responsive Design** - Works on desktop & mobile
- **Dark/Light Mode** (TODO)
- **Export Data** (TODO)

---

## 🔧 Configuration

### Modify Sofia Center Point
Edit [frontend/components/Map.tsx](frontend/components/Map.tsx):
```typescript
const SOFIA_CENTER: [number, number] = [42.6977, 23.3219];
```

### Change Scraper Settings
Edit [backend/scrapers/road_repairs_scraper.py](backend/scrapers/road_repairs_scraper.py):
```python
CONFIG = {
    "output_file": "data/disruptions.json",
    "geocoder_timeout": 10,
    "request_timeout": 10,
}
```

---

## 📝 Next Steps

1. **Implement Real Scrapers**
   - Add actual URLs for Sofia's utility websites
   - Handle HTML parsing for each source

2. **Database Integration**
   - Replace JSON files with Supabase PostgreSQL
   - Add real-time subscriptions

3. **Authentication** (if needed)
   - Secure the POST `/api/disruptions` endpoint
   - Add API key or JWT validation

4. **Deployment**
   - Deploy frontend to Vercel
   - Host scraper on AWS Lambda or Render cron job
   - Set up automated updates

5. **UI Enhancements**
   - Add more filter options
   - Implement dark mode
   - Add statistics dashboard
   - Mobile app version

---

## 📄 License

MIT

## 👥 Contributing

Contributions welcome! Please open an issue or PR.

---

## ⚠️ Disclaimer

This application is for tracking public disruptions only. Always verify critical information from official sources before making decisions based on this data.
