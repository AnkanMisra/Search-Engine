package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"github.com/meilisearch/meilisearch-go"
)

// SearchResult represents a search result document
type SearchResult struct {
	ID      string  `json:"id"`
	Title   string  `json:"title"`
	Content string  `json:"content"`
	URL     string  `json:"url"`
	Score   float64 `json:"score"`
}

// SearchResponse represents the API response
type SearchResponse struct {
	Success bool           `json:"success"`
	Results []SearchResult `json:"results,omitempty"`
	Error   string         `json:"error,omitempty"`
	Query   string         `json:"query,omitempty"`
	Total   int            `json:"total,omitempty"`
}

// Config holds the application configuration
type Config struct {
	MeilisearchURL string
	MeilisearchKey string
	Port           string
	IndexName      string
}

func loadConfig() *Config {
	return &Config{
		MeilisearchURL: getEnv("MEILISEARCH_URL", "http://meilisearch:7700"),
		MeilisearchKey: getEnv("MEILISEARCH_KEY", "masterKey123"),
		Port:           getEnv("PORT", "8080"),
		IndexName:      getEnv("INDEX_NAME", "documents"),
	}
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func main() {
	config := loadConfig()

	// Initialize Meilisearch client
	client := meilisearch.NewClient(meilisearch.ClientConfig{
		Host:   config.MeilisearchURL,
		APIKey: config.MeilisearchKey,
	})

	// Test connection to Meilisearch
	if err := testMeilisearchConnection(client); err != nil {
		log.Printf("Warning: Could not connect to Meilisearch: %v", err)
	} else {
		log.Println("Successfully connected to Meilisearch")
	}

	// Initialize Gin router
	router := gin.Default()

	// CORS middleware
	router.Use(cors.New(cors.Config{
		AllowOrigins:     []string{"*"},
		AllowMethods:     []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowHeaders:     []string{"*"},
		ExposeHeaders:    []string{"*"},
		AllowCredentials: true,
	}))

	// Health check endpoint
	router.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status":      "healthy",
			"service":     "search-engine-backend",
			"meilisearch": config.MeilisearchURL,
		})
	})

	// Search endpoint
	router.GET("/search", func(c *gin.Context) {
		query := c.Query("q")
		if query == "" {
			c.JSON(http.StatusBadRequest, SearchResponse{
				Success: false,
				Error:   "Query parameter 'q' is required",
			})
			return
		}

		// Parse limit parameter
		limitStr := c.DefaultQuery("limit", "20")
		limit, err := strconv.Atoi(limitStr)
		if err != nil {
			limit = 20
		}

		// Perform search
		results, err := performSearch(client, config.IndexName, query, limit)
		if err != nil {
			log.Printf("Search error: %v", err)
			c.JSON(http.StatusInternalServerError, SearchResponse{
				Success: false,
				Error:   fmt.Sprintf("Search failed: %v", err),
				Query:   query,
			})
			return
		}

		c.JSON(http.StatusOK, SearchResponse{
			Success: true,
			Results: results,
			Query:   query,
			Total:   len(results),
		})
	})

	// Index stats endpoint
	router.GET("/stats", func(c *gin.Context) {
		index := client.Index(config.IndexName)
		stats, err := index.GetStats()
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{
				"error": fmt.Sprintf("Failed to get stats: %v", err),
			})
			return
		}

		c.JSON(http.StatusOK, gin.H{
			"index_name":     config.IndexName,
			"document_count": stats.NumberOfDocuments,
			"is_indexing":    stats.IsIndexing,
		})
	})

	log.Printf("Starting server on port %s", config.Port)
	log.Fatal(router.Run(":" + config.Port))
}

func testMeilisearchConnection(client *meilisearch.Client) error {
	_, err := client.Health()
	return err
}

func performSearch(client *meilisearch.Client, indexName, query string, limit int) ([]SearchResult, error) {
	index := client.Index(indexName)

	// Search request
	searchRes, err := index.Search(query, &meilisearch.SearchRequest{
		Limit:                    int64(limit),
		AttributesToHighlight:    []string{"title", "content"},
		HighlightPreTag:          "<mark>",
		HighlightPostTag:         "</mark>",
		AttributesToCrop:         []string{"content"},
		CropLength:               200,
		ShowMatchesPosition:      true,
		AttributesToRetrieve:     []string{"*"},
	})

	if err != nil {
		return nil, err
	}

	var results []SearchResult
	for i, hit := range searchRes.Hits {
		hitBytes, err := json.Marshal(hit)
		if err != nil {
			continue
		}

		var doc map[string]interface{}
		if err := json.Unmarshal(hitBytes, &doc); err != nil {
			continue
		}

		result := SearchResult{
			ID:      getString(doc, "id"),
			Title:   getString(doc, "title"),
			Content: getString(doc, "content"),
			URL:     getString(doc, "url"),
			Score:   float64(len(searchRes.Hits) - i), // Simple scoring based on position
		}

		results = append(results, result)
	}

	return results, nil
}

func getString(m map[string]interface{}, key string) string {
	if val, ok := m[key]; ok {
		if str, ok := val.(string); ok {
			return str
		}
	}
	return ""
} 