# Brightside Light Sync - Qdrant Product Data with Shopify

This project synchronizes product data from Shopify to Qdrant, a vector database, with added metadata processing.

## Features

- Fetches product data from Shopify
- Processes and adds metadata to products
- Uploads processed data to Qdrant vector database

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your environment variables:
- Create a `.env` file with your Shopify and Qdrant credentials

## Usage

Run the main script:
```bash
python "Get shopify data + add metadata + upload to qdrant.py"
```

## Project Structure

- `Get shopify data + add metadata + upload to qdrant.py` - Main script for data synchronization
- `product_metadata_mapping.json` - Configuration for metadata mapping
- `requirements.txt` - Project dependencies 