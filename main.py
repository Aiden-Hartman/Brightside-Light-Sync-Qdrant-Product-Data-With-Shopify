from fastapi import FastAPI, Request, HTTPException, Header, Depends
from starlette.responses import JSONResponse
from sync_script import sync_all
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get API key from environment variable
SYNC_API_KEY = os.getenv("SYNC_API_KEY", "brightside_9843fksl2A3")  # Default for development

app = FastAPI(
    title="Shopify-Qdrant Sync Service",
    description="Webhook service to sync Shopify products with Qdrant vector database",
    version="1.0.0"
)

async def verify_api_key(x_api_key: str = Header(None)):
    """Verify the API key from the request header."""
    if x_api_key is None:
        raise HTTPException(
            status_code=401,
            detail="API key is missing"
        )
    if x_api_key != SYNC_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    return x_api_key

@app.get("/")
async def root():
    return {"status": "healthy", "message": "Shopify-Qdrant sync service is running"}

@app.post("/sync-products")
async def sync_products(
    request: Request,
    api_key: str = Depends(verify_api_key)
):
    try:
        # Log the incoming webhook
        logger.info("Received sync request")
        
        # Optional: Read and validate webhook payload if needed
        payload = await request.json()
        logger.info(f"Webhook payload: {payload}")
        
        # Run the sync process
        sync_all()
        
        return JSONResponse(
            {"status": "success", "message": "Products synchronized successfully"},
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error during sync: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to sync products: {str(e)}"
        ) 