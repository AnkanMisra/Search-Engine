# Search Engine MVP

A full-stack search engine built with React, Go, Python, and Meilisearch.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React App     │    │   Go Backend    │    │   Meilisearch   │
│   (Frontend)    │───▶│   (API Server)  │───▶│   (Search DB)   │
│   Port: 3000    │    │   Port: 8080    │    │   Port: 7700    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                ▲
                                │
                       ┌─────────────────┐
                       │ Python Crawler  │
                       │   (Indexer)     │
                       └─────────────────┘
```

## Components

- **Frontend** (`/frontend`): React with TypeScript for search interface
- **Backend API** (`/backend`): Go server with Gin framework
- **Crawler** (`/crawler`): Python script for web crawling and indexing
- **Search Engine**: Meilisearch container for full-text search

## Quick Start

1. **Prerequisites**: Docker and Docker Compose installed

2. **Start all services**:
   ```bash
   docker-compose up --build
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8080
   - Meilisearch: http://localhost:7700

4. **Run the crawler** (after services are up):
   ```bash
   docker-compose exec crawler python crawler.py
   ```

## Development

### Frontend Development
```bash
cd frontend
npm install
npm start
```

### Backend Development
```bash
cd backend
go mod tidy
go run main.go
```

### Crawler Development
```bash
cd crawler
pip install -r requirements.txt
python crawler.py
```

## API Endpoints

- `GET /search?q=<query>` - Search for documents
- `GET /health` - Health check

## Project Structure

```
search-engine/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── SearchBar.tsx
│   │   │   ├── SearchBar.css
│   │   │   ├── SearchResults.tsx
│   │   │   └── SearchResults.css
│   │   ├── App.tsx
│   │   ├── App.css
│   │   └── index.tsx
│   ├── public/
│   │   └── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── Dockerfile
│   └── nginx.conf
├── backend/
│   ├── main.go
│   ├── go.mod
│   ├── go.sum
│   └── Dockerfile
├── crawler/
│   ├── crawler.py
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml
├── setup.sh
├── .gitignore
└── README.md
```

## Configuration

- Meilisearch master key: `masterKey123`
- All services are configured to work together via Docker networking

## Next Steps

1. Add more sophisticated ranking algorithms
2. Implement real-time indexing
3. Add user authentication
4. Enhance UI/UX
5. Add monitoring and logging 