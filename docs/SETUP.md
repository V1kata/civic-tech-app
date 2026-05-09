# Setup Guide

This guide walks you through setting up the Civic Tech App on your local machine.

## Prerequisites

- **Node.js 18+** - [Download](https://nodejs.org/)
- **Python 3.8+** - [Download](https://www.python.org/)
- **Git** - [Download](https://git-scm.com/)

## Step 1: Clone or Initialize the Project

```bash
# If starting from scratch:
mkdir civic-tech-app && cd civic-tech-app
git init
```

## Step 2: Backend Setup

### 2.1 Create Python Virtual Environment

```bash
cd backend
python -m venv venv
```

Activate the virtual environment:

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 2.2 Install Dependencies

```bash
pip install -r requirements.txt
```

### 2.3 Run the Scraper

Test with demo data:
```bash
python scrapers/road_repairs_scraper.py
```

You should see:
```
🚀 Starting Road Disruptions Scraper...
📋 Using demo data for testing...
🔄 Processing data (geocoding addresses)...
✅ Saved 3 disruptions to data/disruptions.json
✅ Scraper complete!
```

Check the output:
```bash
cat data/disruptions.json
```

## Step 3: Frontend Setup

### 3.1 Install Dependencies

```bash
cd frontend
npm install
```

### 3.2 Create Environment File (Optional)

```bash
cp .env.example .env.local
```

Or create `.env.local`:
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:3000
```

### 3.3 Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

You should see:
- **Sofia Civic Tech** header
- **Interactive map** centered on Sofia with 3 demo markers
- **Legend** at the bottom-left with filter options

## Step 4: Connect Backend to Frontend

The Next.js API route at `frontend/app/api/disruptions/route.ts` automatically reads from `backend/data/disruptions.json`.

To send updates from the scraper:

```bash
# Option A: Use the provided API route
curl -X POST http://localhost:3000/api/disruptions \
  -H "Content-Type: application/json" \
  -d @backend/data/disruptions.json

# Option B: Update scraper to call API
# (See advanced setup below)
```

---

## Common Issues

### Issue: "ModuleNotFoundError: No module named 'bs4'"
**Solution:** Make sure venv is activated and dependencies installed
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Issue: Map doesn't load / markers don't appear
**Solution:** Check the browser console (F12 → Console tab)
- Ensure `/api/disruptions` returns valid JSON
- Check that coordinates are valid (lat: -90 to 90, lon: -180 to 180)

### Issue: "Port 3000 already in use"
**Solution:** Use a different port
```bash
npm run dev -- -p 3001
```

### Issue: Geopy geocoding is slow
**Solution:** Use Nominatim's rate-limiting best practices:
```python
# Add to scrapers/road_repairs_scraper.py
time.sleep(1)  # Wait 1 second between requests
```

---

## Advanced: Deploy to Production

### Frontend (Vercel)

1. Push code to GitHub
2. Connect repo to [Vercel](https://vercel.com)
3. Vercel auto-deploys on push

### Backend Scraper

**Option A: AWS Lambda + EventBridge**
- Containerize scraper
- Deploy to Lambda
- Schedule with EventBridge (every 4 hours)

**Option B: Render Cron Jobs**
- Deploy Python app to [Render](https://render.com)
- Add cron job trigger

**Option C: GitHub Actions**
- Run scraper on schedule
- Commit results to repo or upload to API

Example `.github/workflows/scraper.yml`:
```yaml
name: Run Scraper
on:
  schedule:
    - cron: '0 */4 * * *'  # Every 4 hours
jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r backend/requirements.txt
      - run: python backend/scrapers/road_repairs_scraper.py
      - run: |
          curl -X POST https://your-app.vercel.app/api/disruptions \
            -H "Authorization: Bearer ${{ secrets.API_TOKEN }}" \
            -d @backend/data/disruptions.json
```

### Database (Supabase)

Replace `backend/data/disruptions.json` with Supabase PostgreSQL:

```python
import supabase

client = supabase.create_client(
    url="https://YOUR_PROJECT.supabase.co",
    key="YOUR_API_KEY"
)

# Update a table
client.table("disruptions").upsert([
    {
        "street": "Vasil Levski Blvd",
        "latitude": 42.6987,
        "longitude": 23.3213,
    }
]).execute()
```

---

## Testing

### Test Backend Scraper

```bash
cd backend
python -m pytest scrapers/test_scrapers.py  # (if tests exist)
```

### Test Frontend Build

```bash
cd frontend
npm run build
npm start
```

---

## Getting Help

1. Check [ARCHITECTURE.md](docs/ARCHITECTURE.md) for design details
2. Review code comments in source files
3. Open an issue on GitHub

---

Happy building! 🚀
