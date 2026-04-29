"""
Reduce Lambda:
Aggregates results from multiple LLM chunk analyses
into a single structured output.
Handles both dict and JSON-string formats for robustness.
"""

import json


def lambda_handler(event, context):
    print("Reduce results started")

    results = event

    if not results:
        return {"events": [], "tasks": []}

    final = {
        "events": [],
        "tasks": []
    }

    for item in results:
        try:
            # Extract analysis field
            parsed = item.get("analysis", {})

            # Handle both string and dict formats
            if isinstance(parsed, str):
                parsed = json.loads(parsed)

            # Merge results
            final["events"].extend(parsed.get("events", []))
            final["tasks"].extend(parsed.get("tasks", []))

        except Exception as e:
            print("Error processing item:", e)
            continue

    print(f"Total events: {len(final['events'])}, Total tasks: {len(final['tasks'])}")

    return final