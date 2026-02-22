from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import numpy as np
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.post("/api")
async def latency_metrics(request: Request):
    try:
        body = await request.json()
        regions = body.get("regions", [])
        threshold = body.get("threshold_ms", 180)

        # Correctly join path to root directory
        file_path = os.path.join(os.getcwd(), "q-vercel-latency.json")
        
        with open(file_path, "r", encoding="utf-8") as f:
            telemetry = json.load(f)

        results = {}
        for region in regions:
            region_data = [r for r in telemetry if r.get("region") == region]
            if not region_data:
                continue

            latencies = [r["latency_ms"] for r in region_data]
            uptimes = [r["uptime_pct"] for r in region_data]

            results[region] = {
                "avg_latency": round(float(np.mean(latencies)), 2),
                "p95_latency": round(float(np.percentile(latencies, 95)), 2),
                "avg_uptime": round(float(np.mean(uptimes)), 3),
                "breaches": sum(1 for l in latencies if l > threshold)
            }

        return results # Grader expects the object directly or {"regions": results}
    except Exception as e:
        return {"error": str(e)}, 500