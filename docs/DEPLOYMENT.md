# Deployment Guide - Civic Tech App

Complete guide to deploying the Civic Tech App to production.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    USER (Browser)                            │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP
                     ▼
┌─────────────────────────────────────────────────────────────┐
│            Next.js Frontend (Vercel)                         │
│  - React Components                                          │
│  - Leaflet Map                                               │
│  - API Routes (/api/disruptions)                             │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┼───────────┐
         │           │           │
         ▼           ▼           ▼
    ┌────────┐  ┌──────────┐  ┌──────────────┐
    │ JSON   │  │Supabase  │  │ S3 / KV      │
    │Files   │  │Database  │  │ Caching      │
    └────────┘  └──────────┘  └──────────────┘
         ▲           ▲           ▲
         │           │           │
         └───────────┼───────────┘
                     │ API POST
                     │
    ┌────────────────┴─────────────────┐
    │                                  │
    ▼                                  ▼
┌─────────────┐                  ┌──────────────────┐
│Python Script│                  │Lambda / Cron Job │
│(Scraper)    │                  │(Scheduler)       │
└─────────────┘                  └──────────────────┘
    │
    ▼
Public Websites (SVP, etc.)
```

---

## Option 1: Simple Deployment (MVP)

**Cost: Free to $10/month**
**Setup Time: 30 minutes**

### 1.1 Deploy Frontend to Vercel

1. **Create account** at [vercel.com](https://vercel.com)
2. **Connect GitHub repository**
3. **Vercel auto-detects** Next.js and deploys
4. **Environment variables:**
   - No special config needed for MVP
5. **Your app is live** at `civic-tech-app.vercel.app`

### 1.2 Store Scraper Output

Option A: **Commit to Git (Simple)**
```bash
# After scraper runs, commit JSON file
git add backend/data/disruptions.json
git commit -m "Update disruptions"
git push
```

Then Vercel reads from repo automatically.

Option B: **Vercel KV (Better)**
```bash
# Install Vercel KV CLI
npm install @vercel/kv

# Store data in KV
NEXT_PUBLIC_KV_REST_API_URL=...
NEXT_PUBLIC_KV_REST_API_TOKEN=...
```

Update scraper to use KV instead of local JSON.

### 1.3 Run Scraper with GitHub Actions

Create `.github/workflows/scraper.yml`:
```yaml
name: Run Scraper Daily
on:
  schedule:
    - cron: '0 6 * * *'  # Every day at 6 AM

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      
      - name: Run scraper
        run: python backend/scrapers/road_repairs_scraper.py
      
      - name: Commit and push
        run: |
          git config --local user.name "bot"
          git config --local user.email "bot@example.com"
          git add backend/data/disruptions.json
          git commit -m "Update disruptions $(date)" || true
          git push
```

**Result:** Scraper runs automatically, pushes updates to Git, Vercel deploys instantly.

---

## Option 2: Production Deployment

**Cost: $20-50/month**
**Setup Time: 2-3 hours**

### 2.1 Frontend on Vercel (same as above)

### 2.2 Database: Supabase

1. **Create account** at [supabase.com](https://supabase.com)
2. **Create new project** (free tier: 500 MB, 2 GB bandwidth)
3. **Create table:**

```sql
CREATE TABLE disruptions (
  id BIGSERIAL PRIMARY KEY,
  street TEXT NOT NULL,
  disruption_type TEXT NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  latitude DECIMAL(9, 6) NOT NULL,
  longitude DECIMAL(9, 6) NOT NULL,
  scraped_at TIMESTAMP DEFAULT NOW(),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(street, disruption_type, start_date)
);

CREATE INDEX idx_disruption_type ON disruptions(disruption_type);
CREATE INDEX idx_coordinates ON disruptions(latitude, longitude);
```

4. **Get API credentials:**
   - URL: `https://xxxxx.supabase.co`
   - Key: Found in Settings → API

5. **Update Next.js:**

Create `frontend/lib/supabase.ts`:
```typescript
import { createClient } from '@supabase/supabase-js'

export const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)
```

Update `frontend/app/api/disruptions/route.ts`:
```typescript
import { supabase } from "@/lib/supabase"

export async function GET(request: NextRequest) {
  const { data, error } = await supabase
    .from("disruptions")
    .select("*")
    .limit(100)
  
  if (error) throw new Error(error.message)
  return NextResponse.json(data)
}
```

6. **Add environment variables to Vercel:**
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`

### 2.3 Scraper on AWS Lambda

1. **Create AWS account** (free tier: 1M requests/month)
2. **Create Lambda function:**

```bash
# Create deployment package
cd backend
mkdir lambda_layer
pip install -r requirements.txt -t lambda_layer/python/
zip -r layer.zip lambda_layer/

# Upload to Lambda
```

3. **Add Lambda layer** with dependencies
4. **Upload scraper code** as Lambda function
5. **Create EventBridge rule:**
   - Trigger: `cron(0 */4 * * * ?)`  (every 4 hours)
   - Target: Lambda function

Lambda scraper code:
```python
import json
import supabase

def lambda_handler(event, context):
    # Initialize Supabase
    client = supabase.create_client(
        url=os.environ["SUPABASE_URL"],
        key=os.environ["SUPABASE_KEY"]
    )
    
    # Run scraper (as before)
    scraper = RoadsDisruptionScraper()
    disruptions = scraper.scrape_demo_data()
    
    # Insert to Supabase
    for disruption in disruptions:
        client.table("disruptions").upsert(disruption).execute()
    
    return {
        "statusCode": 200,
        "body": json.dumps({"status": "success"})
    }
```

### 2.4 Monitoring & Alerts

**CloudWatch (AWS):**
- Monitor Lambda executions
- Set up alerts for failures

**Vercel Analytics:**
- Built-in performance monitoring
- Error tracking

**Sentry (Optional):**
```bash
npm install @sentry/nextjs
```

---

## Option 3: Advanced (Multi-Region)

**Cost: $50-200/month**

- Vercel Edge Functions for low-latency API responses
- Cloudflare Workers for caching & filtering
- Multiple regional scrapers (distributed)
- Real-time Supabase subscriptions
- Mobile app (React Native)

---

## Deployment Checklist

### Before Going Live

- [ ] Test all API endpoints locally
- [ ] Add error logging (Sentry or LogRocket)
- [ ] Set up monitoring (Vercel, CloudWatch)
- [ ] Test scraper on staging environment
- [ ] Verify geocoding works for all streets
- [ ] Test map performance with 1000+ markers
- [ ] Add rate limiting to API endpoint
- [ ] Secure the POST endpoint with authentication
- [ ] Create backup strategy for database
- [ ] Add terms of service and privacy policy
- [ ] Set up automated backups (Supabase)

### Monitoring in Production

1. **API Response Times**
   - Track `/api/disruptions` latency
   - Alert if > 5 seconds

2. **Scraper Success Rate**
   - Monitor failed scrapes
   - Alert if fails 3x in a row

3. **Data Freshness**
   - Ensure data updates every 4-6 hours
   - Show "last updated" timestamp to users

4. **Error Rates**
   - Map rendering errors
   - Database connection errors
   - Geocoding failures

---

## Performance Optimization

### Frontend Caching
```typescript
// In Next.js API route
response.headers.set(
  "Cache-Control", 
  "public, max-age=300, s-maxage=3600"
)
```

### Database Indexing (Supabase)
```sql
CREATE INDEX idx_search ON disruptions (street, disruption_type);
```

### Map Rendering
- Use Leaflet.markercluster for 1000+ markers
- Implement virtual scrolling for lists
- Lazy-load popup content

---

## Rollback Plan

If something breaks:

1. **Frontend:** Vercel automatically keeps previous deployments
   - Click "Rollback" button in Vercel dashboard
   
2. **Database:** Supabase auto-backups daily
   - Restore from backup in Settings

3. **Scraper:** Keep previous JSON file in Git
   - Revert commit

---

## Cost Estimation (Monthly)

| Service | MVP | Production |
|---------|-----|------------|
| Vercel | Free | $20 |
| Supabase | Free | $25 |
| AWS Lambda | Free (tier) | $10 |
| Domain | - | $12 |
| **Total** | **~$15** | **~$67** |

---

## Questions?

See [ARCHITECTURE.md](ARCHITECTURE.md) for design details or [SETUP.md](SETUP.md) for local development.
