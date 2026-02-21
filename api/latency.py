import json
import numpy as np

def handler(request):
    if request.method != "POST":
        return {
            "statusCode": 405,
            "body": "Method Not Allowed"
        }

    body = request.get_json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 0)

    with open("q-vercel-latency.json") as f:
        data = json.load(f)

    result = {}

    for region in regions:
        region_data = [d for d in data if d["region"] == region]

        if not region_data:
            continue

        latencies = [d["latency_ms"] for d in region_data]
        uptimes = [d["uptime"] for d in region_data]

        result[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": sum(1 for l in latencies if l > threshold)
        }

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
            "Content-Type": "application/json"
        },
        "body": json.dumps(result)
    }