from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import numpy as np
import os

app = FastAPI()

# Enable CORS for POST requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.post("/")
async def latency_endpoint(request: Request):
    try:
        body = await request.json()
    except Exception:
        return {"error": "Invalid JSON body"}, 400

    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 180)

    # Path to the JSON file in the root directory
    # Vercel's root for open() is the project root
    file_path = os.path.join(os.getcwd(), "q-vercel-latency.json")

    if not os.path.exists(file_path):
        return {"error": f"File not found at {file_path}"}, 500

    with open(file_path, "r") as f:
        data = json.load(f)

    result = {}
    for region in regions:
        # Filter for the specific region
        region_data = [d for d in data if d.get("region") == region]

        if not region_data:
            continue

        latencies = [d["latency_ms"] for d in region_data]
        # IMPORTANT: The JSON uses 'uptime_pct', not 'uptime'
        uptimes = [d["uptime_pct"] for d in region_data]

        result[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": int(sum(1 for l in latencies if l > threshold))
        }

    return result

# Vercel needs this 'app' object