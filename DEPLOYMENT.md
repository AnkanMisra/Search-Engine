# 🚀 Deploy Search Engine to Vercel

This guide shows how to deploy your search engine MVP to production using Vercel and cloud services.

## 📋 Prerequisites

1. GitHub repository with your code
2. Vercel account
3. Meilisearch Cloud account (or alternative hosting)

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Vercel        │    │ Vercel Functions│    │ Meilisearch     │
│   (Frontend)    │───▶│   (API Proxy)   │───▶│   Cloud         │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                ▲
                                │
                       ┌─────────────────┐
                       │ GitHub Actions  │
                       │   (Crawler)     │
                       └─────────────────┘
```

## 🔧 Step-by-Step Deployment

### Step 1: Set up Meilisearch Cloud

1. **Sign up** at [Meilisearch Cloud](https://cloud.meilisearch.com/)
2. **Create a project** and get:
   - **Host URL**: `https://your-project.meilisearch.io`
   - **API Key**: Your admin API key
3. **Save these credentials** - you'll need them later

### Step 2: Configure Your Repository

1. **Push your changes** to GitHub:
   ```bash
   git add .
   git commit -m "Add Vercel deployment configuration"
   git push origin main
   ```

### Step 3: Deploy Frontend to Vercel

1. **Connect to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Sign in with GitHub
   - Click "New Project"
   - Import your repository

2. **Configure Build Settings**:
   - **Framework Preset**: Create React App
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`

3. **Add Environment Variables**:
   ```
   MEILISEARCH_URL=https://your-project.meilisearch.io
   MEILISEARCH_KEY=your-api-key
   ```

4. **Deploy**: Click "Deploy"

### Step 4: Set up GitHub Actions (Crawler)

1. **Add Repository Secrets**:
   - Go to your GitHub repo → Settings → Secrets and variables → Actions
   - Add secrets:
     ```
     MEILISEARCH_URL=https://your-project.meilisearch.io
     MEILISEARCH_KEY=your-api-key
     ```

2. **Test the crawler**:
   - Go to Actions tab in GitHub
   - Find "Update Search Index" workflow
   - Click "Run workflow" to test

### Step 5: Initial Data Population

Run the crawler manually to populate your search index:

```bash
# Option 1: Run locally and push to cloud
MEILISEARCH_URL=https://your-project.meilisearch.io \
MEILISEARCH_KEY=your-api-key \
python crawler/crawler.py

# Option 2: Trigger GitHub Action manually
# Go to GitHub Actions → Update Search Index → Run workflow
```

## ✅ Verification

1. **Frontend**: Visit your Vercel URL (e.g., `https://your-app.vercel.app`)
2. **API**: Test API endpoint: `https://your-app.vercel.app/api/search?q=test`
3. **Search**: Try searching for indexed content
4. **Crawler**: Check GitHub Actions for successful runs

## 🔧 Configuration Options

### Custom Domains
- **Vercel**: Add custom domain in Vercel dashboard
- **SSL**: Automatically handled by Vercel

### Environment Variables
```bash
# Frontend (.env)
REACT_APP_API_URL=https://your-app.vercel.app

# GitHub Actions (Repository Secrets)
MEILISEARCH_URL=https://your-project.meilisearch.io
MEILISEARCH_KEY=your-api-key
MAX_PAGES=100
CRAWL_DELAY=1.0
```

### Crawler Schedule
Edit `.github/workflows/crawler.yml`:
```yaml
schedule:
  - cron: '0 */6 * * *'  # Every 6 hours
  - cron: '0 0 * * *'    # Daily at midnight
  - cron: '0 0 * * 0'    # Weekly on Sunday
```

## 💰 Cost Estimation

- **Vercel**: Free tier (100GB bandwidth, 1000 serverless function invocations)
- **Meilisearch Cloud**: $0/month for hobby tier (100K documents, 10K searches)
- **GitHub Actions**: 2000 minutes/month free

## 🚀 Production Optimizations

### Performance
- **CDN**: Enabled by default on Vercel
- **Caching**: Add cache headers to API responses
- **Compression**: Enabled by default

### Monitoring
- **Vercel Analytics**: Built-in performance monitoring
- **Error Tracking**: Add Sentry or similar
- **Search Analytics**: Track popular queries

### Scaling
- **Search Index**: Upgrade Meilisearch plan as needed
- **API Rate Limits**: Implement rate limiting
- **Crawler Limits**: Adjust crawl frequency and scope

## 🔧 Troubleshooting

### Common Issues

1. **API not working**: Check environment variables in Vercel
2. **Search returns no results**: Verify Meilisearch connection and data
3. **Crawler failing**: Check GitHub Actions logs and secrets
4. **CORS errors**: Verify API function CORS headers

### Debug Commands
```bash
# Test Meilisearch connection
curl -X GET 'https://your-project.meilisearch.io/health' \
  -H 'Authorization: Bearer your-api-key'

# Test Vercel API
curl 'https://your-app.vercel.app/api/search?q=test'

# Check index stats
curl -X GET 'https://your-project.meilisearch.io/indexes/documents/stats' \
  -H 'Authorization: Bearer your-api-key'
```

## 🎯 Next Steps

1. **Custom Domain**: Add your own domain
2. **Analytics**: Track user behavior and popular searches
3. **Enhanced UI**: Add filters, pagination, autocomplete
4. **More Content**: Expand crawler to more websites
5. **API Rate Limiting**: Implement proper rate limiting

---

**🎉 Congratulations!** Your search engine is now live on the internet!

Visit your deployed search engine and start searching! 🔍 