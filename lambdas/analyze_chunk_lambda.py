import json
import boto3
from datetime import datetime

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")


def analyze_chunk(text_chunk: str) -> dict:
    """
    Analyze a text chunk using an LLM and extract structured tasks and events.
    """
    today = datetime.utcnow().strftime("%Y-%m-%d")

    prompt = f"""
Today's date is: {today}
Extract structured scheduling information.

STRICT RULES:
- Output MUST be valid JSON
- Do NOT include explanation text
- Do NOT include markdown
- ONLY return JSON

- Separate TASKS and EVENTS correctly
- If a sentence contains both, split them into separate entries
- TASKS must include owner if mentioned
- If owner is not mentioned, default owner = "me"
- EVENTS must include participants if mentioned or implied
- Treat phrases like "review", "meeting", "call" as EVENTS
- Convert relative time (today, tomorrow) into date strings if possible
- Only include FUTURE or upcoming events
- Ignore past events (e.g., "yesterday", "last week")
- Tasks include actions assigned to people (e.g., "ask", "send", "talk", "prepare")
- Do NOT classify action verbs as events
- For meetings/events, include all participants including the speaker ("me") if implied
- For tasks, extract the action verb and object
- For events, extract the activity and participants
- If no date/time specified, leave fields empty
- If no participants specified, leave participants array empty
- Any action initiated by a person should be classified as a TASK
- EVENTS must represent scheduled or completed activities, not intentions
- Event titles should be concise but descriptive (e.g., "Meeting with John", "Design review"), not just generic verbs


FORMAT:
{{
  "events": [
    {{
      "title": "",
      "date": "",
      "time": "",
      "participants": []
    }}
  ],
  "tasks": [
    {{
      "task": "",
      "owner": "",
      "due": ""
    }}
  ]
}}

Text:
{text_chunk}
"""

    response = bedrock.invoke_model(
        modelId="amazon.nova-pro-v1:0",
        body=json.dumps({
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": prompt}]
                }
            ],
            "inferenceConfig": {
                "maxTokens": 300,
                "temperature": 0.2
            }
        }),
        contentType="application/json",
        accept="application/json"
    )

    result = json.loads(response["body"].read())
    output_text = result["output"]["message"]["content"][0]["text"]

    try:
        return json.loads(output_text)
    except Exception:
        return {"events": [], "tasks": []}


def lambda_handler(event, context):
    print("Analyzing chunk")

    text_chunk = event
    result = analyze_chunk(text_chunk)

    return {
        "analysis": result
    }