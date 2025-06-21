const { MeiliSearch } = require('meilisearch')

// Initialize Meilisearch client
const client = new MeiliSearch({
  host: process.env.MEILISEARCH_URL || 'https://your-meilisearch-instance.meilisearch.io',
  apiKey: process.env.MEILISEARCH_KEY || 'your-api-key'
})

export default async function handler(req, res) {
  // Set CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type')

  if (req.method === 'OPTIONS') {
    return res.status(200).end()
  }

  if (req.method !== 'GET') {
    return res.status(405).json({ success: false, error: 'Method not allowed' })
  }

  try {
    const { q: query, limit = 20 } = req.query

    if (!query || query.trim() === '') {
      return res.status(400).json({ 
        success: false, 
        error: 'Query parameter "q" is required' 
      })
    }

    // Perform search
    const index = client.index('documents')
    const searchResults = await index.search(query, {
      limit: parseInt(limit),
      attributesToHighlight: ['title', 'content'],
      highlightPreTag: '<mark>',
      highlightPostTag: '</mark>',
      attributesToCrop: ['content'],
      cropLength: 200,
      showMatchesPosition: true,
      attributesToRetrieve: ['*']
    })

    // Format results
    const results = searchResults.hits.map((hit, index) => ({
      id: hit.id || `result-${index}`,
      title: hit.title || 'Untitled',
      content: hit.content || '',
      url: hit.url || '#',
      score: searchResults.hits.length - index // Simple scoring
    }))

    return res.status(200).json({
      success: true,
      results: results,
      query: query,
      total: results.length,
      processingTimeMs: searchResults.processingTimeMs
    })

  } catch (error) {
    console.error('Search error:', error)
    return res.status(500).json({
      success: false,
      error: 'Search failed',
      message: error.message
    })
  }
} 