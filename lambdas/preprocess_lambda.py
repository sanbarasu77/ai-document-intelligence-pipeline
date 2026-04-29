import boto3

"""
Preprocess Lambda:
Reads input document from S3 and splits it into chunks
for parallel LLM processing.
"""

s3 = boto3.client("s3")

CHUNK_SIZE = 10
MAX_LINES = 2000


def lambda_handler(event, context):
    print(f"Reading file from S3: {event.get('bucket')}/{event.get('key')}")

    bucket = event["bucket"]
    key = event["key"]

    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        text = response["Body"].read().decode("utf-8")
    except Exception as e:
        print("Error reading from S3:", e)
        return {"chunks": []}

    lines = text.splitlines()[:MAX_LINES]

    chunks = []
    for i in range(0, len(lines), CHUNK_SIZE):
        chunk = "\n".join(lines[i:i+CHUNK_SIZE])
        chunks.append(chunk)

    print(f"Total lines: {len(lines)}, Total chunks: {len(chunks)}")

    return {
        "chunks": chunks
    }