import requests
import json
import time
import re
import os
import numpy as np
from uuid import uuid4
from tqdm import tqdm
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

# --- Configuration ---
SHOPIFY_STORE = os.getenv("SHOPIFY_STORE")
API_VERSION = os.getenv("API_VERSION")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
QDRANT_URL = os.getenv("QDRANT_API_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME")
VECTOR_SIZE = 1536
METADATA_FILE = "product_metadata_mapping.json"  # ← place this JSON file in same directory

HEADERS = {"X-Shopify-Access-Token": ACCESS_TOKEN}

# --- Load mapping file ---
def load_metadata_mapping(filename=METADATA_FILE):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

METADATA_LOOKUP = load_metadata_mapping()

# --- Shopify Fetch ---
def fetch_products(limit=250):
    print("📦 Fetching products from Shopify...")
    products = []
    base_url = f"https://{SHOPIFY_STORE}/admin/api/{API_VERSION}/products.json"
    params = {"limit": limit}
    while True:
        response = requests.get(base_url, headers=HEADERS, params=params)
        if response.status_code != 200:
            print("❌ Error:", response.status_code, response.text)
            break
        data = response.json()
        products.extend(data.get("products", []))
        link_header = response.headers.get("Link")
        if link_header and 'rel="next"' in link_header:
            next_page_info = link_header.split("page_info=")[1].split(">")[0]
            params = {"limit": limit, "page_info": next_page_info}
            time.sleep(0.5)
        else:
            break
    return products

# --- Utilities ---
def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

def clean_html(raw_html):
    """
    Takes raw HTML content and returns plain text without tags.
    Uses BeautifulSoup's parser for robust handling of nested tags.
    """
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text(separator=" ", strip=True)

def enrich_product(product):
    title = product.get("title", "")
    slug_id = slugify(title)
    variant = product["variants"][0]
    image_url = product["images"][0]["src"] if product.get("images") else ""
    raw_html = product.get("body_html", "")
    clean_description = clean_html(raw_html)
    meta = METADATA_LOOKUP.get(title.strip(), {})
    category = meta.get("category", "unclassified")
    tier = meta.get("tier", "unranked")
    return {
        "id": slug_id,
        "title": title,
        "description": clean_description,
        "price": float(variant.get("price", 0)),
        "image_url": image_url,
        "category": category,
        "tier": tier,
        "variant_id": variant["id"]
    }

def get_random_embeddings(texts):
    vectors = []
    for _ in texts:
        vec = np.random.normal(0, 1, VECTOR_SIZE)
        vec = vec / np.linalg.norm(vec)
        vectors.append(vec.tolist())
    return vectors

# --- Qdrant Upload ---
def upload_to_qdrant(products):
    print("🔗 Connecting to Qdrant...")
    client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        prefer_grpc=False,
        timeout=30,
    )

    print(f"🧹 Recreating collection '{COLLECTION_NAME}'...")
    collections = client.get_collections().collections
    if COLLECTION_NAME in [c.name for c in collections]:
        client.delete_collection(collection_name=COLLECTION_NAME)

    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )

    print("📊 Generating embeddings and uploading...")
    BATCH_SIZE = 100
    all_points = []
    product_texts = [f"{p['title']}. {p['description']}" for p in products]
    for i in tqdm(range(0, len(product_texts), BATCH_SIZE), desc="Embedding batches"):
        batch_texts = product_texts[i:i+BATCH_SIZE]
        batch_vectors = get_random_embeddings(batch_texts)
        for j, vec in enumerate(batch_vectors):
            p = products[i + j]
            point = PointStruct(
                id=str(uuid4()),
                vector=vec,
                payload=p
            )
            all_points.append(point)

    for i in tqdm(range(0, len(all_points), BATCH_SIZE), desc="Uploading batches"):
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=all_points[i:i+BATCH_SIZE],
            wait=True,
        )

    print(f"\n✅ Uploaded {len(products)} products to Qdrant collection '{COLLECTION_NAME}'.")

# --- Run everything ---
if __name__ == "__main__":
    raw_products = fetch_products()
    enriched = [enrich_product(p) for p in raw_products]
    upload_to_qdrant(enriched)
