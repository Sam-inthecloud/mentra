import boto3
import json

model_id = "arn:aws:bedrock:us-east-1:713881818082:inference-profile/us.anthropic.claude-3-7-sonnet-20250219-v1:0"
region = "us-east-1"

client = boto3.client("bedrock-runtime", region_name=region)

def query_claude(prompt):
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 500,
        "temperature": 0.7,
        "messages": [
            {
                "role": "user",
                "content": prompt
                }
        ]

    }

    response = client.invoke_model(
    modelId=model_id,
    body=json.dumps(body),
    contentType="application/json",
    accept="application/json"
    )

    result = json.loads(response['body'].read())


    if "content" in result and len(result["content"]) > 0:
        return result["content"][0].get("text", "[No test found]")
    else:
        return "[No content returned from Claude]"

if __name__ == "__main__":
    prompt = "What are the key benefits of using Amazon CloudWatch?"
    response = query_claude(prompt)
    print("\nClaude says:\n", response)
