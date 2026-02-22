from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import numpy as np
import os

app = FastAPI()

# Enable CORS for POST requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.post("/api/latency")  # Explicitly match the Vercel path
async def get_latency(request: Request):
    try:
        body = await request.json()
    except:
        return {"error": "Invalid JSON"}, 400

    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 180)

    # Use absolute path to find JSON in the project root
    base_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_path, "..", "q-vercel-latency.json")

    with open(file_path, "r") as f:
        data = json.load(f)

    result = {}
    for region in regions:
        region_data = [d for d in data if d.get("region") == region]

        if not region_data:
            continue

        latencies = [d["latency_ms"] for d in region_data]
        # FIXED: Changed 'uptime' to 'uptime_pct'
        uptimes = [d["uptime_pct"] for d in region_data]

        result[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": int(sum(1 for l in latencies if l > threshold))
        }

    return result