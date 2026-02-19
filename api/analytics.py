import json
import os
import statistics


DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "telemetry.json")


def handler(request, context):
    # Handle CORS preflight
    if request.method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": cors_headers()
        }

    if request.method != "POST":
        return {
            "statusCode": 405,
            "headers": cors_headers(),
            "body": json.dumps({"error": "Method not allowed"})
        }

    try:
        body = json.loads(request.body)
    except:
        return {
            "statusCode": 400,
            "headers": cors_headers(),
            "body": json.dumps({"error": "Invalid JSON"})
        }

    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 0)

    with open(DATA_FILE) as f:
        data = json.load(f)

    result = {}

    for region in regions:
        region_records = [r for r in data if r["region"] == region]

        if not region_records:
            continue

        latencies = [r["latency_ms"] for r in region_records]
        uptimes = [r["uptime_pct"] for r in region_records]

        result[region] = {
            "avg_latency": statistics.mean(latencies),
            "p95_latency": percentile(latencies, 95),
            "avg_uptime": statistics.mean(uptimes),
            "breaches": sum(1 for l in latencies if l > threshold)
        }

    return {
        "statusCode": 200,
        "headers": cors_headers(),
        "body": json.dumps(result)
    }


def percentile(data, p):
    sorted_data = sorted(data)
    k = (len(sorted_data) - 1) * (p / 100)
    f = int(k)
    c = min(f + 1, len(sorted_data) - 1)
    if f == c:
        return sorted_data[int(k)]
    return sorted_data[f] + (sorted_data[c] - sorted_data[f]) * (k - f)


def cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
        "Content-Type": "application/json"
    }
