# Shopify-Qdrant Sync Service

A FastAPI web service that syncs Shopify products with a Qdrant vector database. This service is designed to be triggered via webhooks from Make.com when Shopify products are updated.

## Features

- Fetches products from Shopify Admin API
- Enriches product data with metadata from a local JSON mapping
- Cleans HTML content from product descriptions
- Generates vector embeddings (currently random, can be replaced with real embeddings)
- Uploads enriched product data to Qdrant vector database
- Exposes a webhook endpoint for automated triggering
- Secured with API key authentication

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with the following variables:
   ```
   SHOPIFY_STORE=your-store.myshopify.com
   API_VERSION=2024-01  # or your preferred version
   ACCESS_TOKEN=your_shopify_access_token
   QDRANT_API_URL=your_qdrant_url
   QDRANT_API_KEY=your_qdrant_api_key
   QDRANT_COLLECTION_NAME=your_collection_name
   SYNC_API_KEY=your_sync_api_key  # Required for webhook authentication
   ```

## Running Locally

Start the service with:
```bash
uvicorn main:app --reload
```

The service will be available at `http://localhost:8000`

## API Endpoints

- `GET /`: Health check endpoint
- `POST /sync-products`: Webhook endpoint for triggering product sync
  - Requires `x-api-key` header with valid API key
  - Example: `curl -X POST http://localhost:8000/sync-products -H "x-api-key: your_api_key"`

## Security

The `/sync-products` endpoint is protected with API key authentication:
- All requests must include an `x-api-key` header
- The API key must match the value in the `SYNC_API_KEY` environment variable
- Invalid or missing API keys will result in a 401 Unauthorized response

## Deployment to Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set the following:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add your environment variables in the Render dashboard, including `SYNC_API_KEY`

## Make.com Integration

1. In Make.com, create a new scenario
2. Add a Shopify webhook trigger for product updates
3. Add an HTTP module that POSTs to your Render service's `/sync-products` endpoint
   - Don't forget to add the `x-api-key` header with your API key

## Development

The codebase consists of two main files:
- `main.py`: FastAPI application and webhook endpoint
- `sync_script.py`: Core sync logic and utilities

## License

MIT 