import json
import numpy as np
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

# Enable CORS for POST from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Load the static telemetry data (in real apps, this could be from a DB)
with open("q-vercel-latency.json", "r") as f:
    telemetry_data = json.load(f)

@app.post("/")
async def analytics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold_ms = body.get("threshold_ms", 180)
    
    results = {}
    for region in regions:
        region_data = [r for r in telemetry_data if r.get("region") == region]
        if not region_data:
            results[region] = {"avg_latency": 0, "p95_latency": 0, "avg_uptime": 0, "breaches": 0}
            continue
        
        latencies = np.array([r.get("latency_ms", 0) for r in region_data])
        uptimes = np.array([r.get("uptime", 0) for r in region_data])
        
        results[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": int(np.sum(latencies > threshold_ms))
        }
    
    return JSONResponse(content=results)
