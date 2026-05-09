# Quick Reference - Civic Tech App

## 🎯 Project Summary

**Civic Tech App**: Interactive map of road repairs & water outages in Sofia, Bulgaria.

| Aspect | Technology |
|--------|-----------|
| **Frontend** | Next.js 14 + React 18 + Tailwind CSS |
| **Mapping** | React-Leaflet + OpenStreetMap |
| **Backend** | Python 3.10+ (BeautifulSoup scraper) |
| **Database** | JSON files (MVP) / Supabase PostgreSQL (prod) |
| **Deployment** | Vercel (frontend) + Lambda/Cron (scraper) |

---

## ⚡ Quick Start (5 minutes)

### 1️⃣ Backend - Run Scraper

```bash
# 1. Start the scraper (backend)
cd backend
python -m venv venv
source venv/bin/activate           # Windows: venv\Scripts\activate
pip install -r requirements.txt
python scrapers/road_repairs_scraper.py

# 2. Start frontend (new terminal)
cd frontend
npm install
npm run dev

# 3. Open browser to http://localhost:3000
# You'll see: Sofia map with 3 demo markers + interactive legend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python scrapers/road_repairs_scraper.py
```

**Output:** Creates `backend/data/disruptions.json` with 3 sample disruptions.

### 2️⃣ Frontend - Start Dev Server

```bash
cd frontend
npm install
npm run dev
```

**Open:** http://localhost:3000

You should see:
- ✅ Sofia map with 3 markers
- ✅ Legend panel (bottom-left)
- ✅ Clickable markers with popup details

---

## 📁 File Structure (Most Important)

```
civic-tech-app/
├── backend/
│   ├── scrapers/road_repairs_scraper.py  ← EDIT THIS to add real websites
│   └── data/disruptions.json              ← OUTPUT from scraper
├── frontend/
│   ├── app/page.tsx                       ← Main page
│   ├── components/Map.tsx                 ← Leaflet map component
│   └── app/api/disruptions/route.ts       ← API endpoint
├── docs/
│   ├── ARCHITECTURE.md                    ← Read this first!
│   ├── SETUP.md                           ← Setup guide
│   └── DEPLOYMENT.md                      ← Deploy to prod
└── README.md                              ← Overview
```

---

## 🔑 Key Concepts

### Data Flow
```
Public Websites
    ↓ (HTTP)
Python Scraper (road_repairs_scraper.py)
    ↓ (Parse HTML)
backend/data/disruptions.json
    ↓ (Fetch)
Next.js API (/api/disruptions)
    ↓ (JSON response)
React Component (Map.tsx)
    ↓ (Render)
Interactive Leaflet Map (Browser)
```

### Disruption Object
```json
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
```

---

## 🛠️ Common Tasks

### ✏️ Customize Map Center
**File:** `frontend/components/Map.tsx`
```typescript
const SOFIA_CENTER: [number, number] = [42.6977, 23.3219];  // Edit these
```

### 📍 Add Marker Color
**File:** `frontend/components/Map.tsx`
```typescript
const roadWorksIcon = L.icon({
  iconUrl: "https://...",  // URL to marker icon
});
```

### 🌐 Add Real Website Scraper
**File:** `backend/scrapers/road_repairs_scraper.py`
```python
def run(self, use_demo: bool = True):
    if use_demo:
        raw_data = self.scrape_demo_data()  # ← Change this
    else:
        raw_data = self.scrape_from_svp()   # ← Add your scraper
```

### 🗄️ Switch to Supabase Database
**See:** `docs/DEPLOYMENT.md` → Option 2: Production Deployment

### 📤 Deploy to Vercel
```bash
git push origin main  # Auto-deploys via GitHub integration
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| **"No module named bs4"** | Run `pip install -r requirements.txt` in activated venv |
| **Map doesn't load** | Check browser console (F12). Ensure `/api/disruptions` returns JSON |
| **"Port 3000 already in use"** | Use `npm run dev -- -p 3001` |
| **Markers not showing** | Verify coordinates: lat [-90,90], lon [-180,180] |
| **Scraper is slow** | Add `time.sleep(1)` between requests to respect rate limits |

---

## 📊 API Endpoints

### GET `/api/disruptions`
Fetch all disruptions.

```bash
curl http://localhost:3000/api/disruptions
```

**Query Parameters:**
- `type=Road%20works` - Filter by type
- `limit=10` - Max results

### POST `/api/disruptions`
Upload disruptions (from scraper).

```bash
curl -X POST http://localhost:3000/api/disruptions \
  -H "Content-Type: application/json" \
  -d @backend/data/disruptions.json
```

---

## 🚀 Deployment Steps

### Step 1: Deploy Frontend (5 min)
1. Push code to GitHub
2. Go to [vercel.com](https://vercel.com)
3. Connect your repo
4. Vercel auto-deploys (done!)

### Step 2: Set Up Scraper (15 min)
**Option A: GitHub Actions** (free, simple)
- Create `.github/workflows/scraper.yml`
- Runs on schedule, commits to Git
- See `docs/DEPLOYMENT.md` for code

**Option B: AWS Lambda** (free tier, scalable)
- Package scraper as Lambda
- Trigger with EventBridge
- See `docs/DEPLOYMENT.md` for details

### Step 3: Add Database (optional)
Replace JSON with Supabase PostgreSQL:
- Sign up at [supabase.com](https://supabase.com)
- Create table
- Update API route
- See `docs/DEPLOYMENT.md` for SQL

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **ARCHITECTURE.md** | System design, data flow, tech decisions |
| **SETUP.md** | Local development setup guide |
| **DEPLOYMENT.md** | Production deployment options & costs |
| **PROJECT_STRUCTURE.md** | Detailed folder structure explanation |
| **README.md** | Project overview & quick start |

---

## 🎓 Learning Resources

### Next.js
- [Next.js Docs](https://nextjs.org/docs)
- [App Router Guide](https://nextjs.org/docs/app)
- [API Routes](https://nextjs.org/docs/app/building-your-application/routing/route-handlers)

### React-Leaflet
- [Documentation](https://react-leaflet.js.org/)
- [Examples](https://react-leaflet.js.org/docs/start-setup/)

### BeautifulSoup
- [Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [CSS Selectors](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#css-selectors)

### Tailwind CSS
- [Documentation](https://tailwindcss.com/docs)
- [Component Examples](https://tailwindcss.com/docs/guides/nextjs)

---

## ✅ Checklist

### MVP (This Week)
- [ ] Run local scraper with demo data
- [ ] View map at localhost:3000
- [ ] Verify 3 markers appear on map
- [ ] Test clicking markers for details
- [ ] Test legend filter buttons

### Phase 1 (Next Week)
- [ ] Find real websites to scrape
- [ ] Implement HTML parsing for each site
- [ ] Test scraper on real data
- [ ] Deploy frontend to Vercel
- [ ] Set up GitHub Actions for scraper

### Phase 2 (Next Month)
- [ ] Migrate to Supabase
- [ ] Add more filter options
- [ ] Implement search functionality
- [ ] Add statistics dashboard
- [ ] Performance optimization

---

## 💡 Pro Tips

1. **Test scraper with demo data first** - Don't hit real sites until you're ready
2. **Use Nominatim for free geocoding** - No API key needed
3. **Cache map data** - Reduces API calls & improves speed
4. **Start with 1 data source** - Add more once working
5. **Monitor scraper failures** - Log errors for debugging
6. **Use Vercel Preview URLs** - Test before merging to main

---

## 🔗 Useful Links

- **GitHub**: Your repo URL
- **Vercel Dashboard**: https://vercel.com/dashboard
- **Supabase Console**: https://app.supabase.com
- **OpenStreetMap**: https://www.openstreetmap.org/
- **Nominatim Geocoder**: https://nominatim.org/

---

## 🆘 Get Help

1. **Check docs/** folder first
2. **Search browser console** for errors (F12)
3. **Check terminal output** for Python/Node errors
4. **Try demo data first** - Verify setup works
5. **Read ARCHITECTURE.md** - Understand the flow

---

**Last Updated:** May 2026  
**Status:** ✅ MVP Ready  
**Next Action:** Run `python backend/scrapers/road_repairs_scraper.py`
