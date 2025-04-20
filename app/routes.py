from flask import Blueprint, render_template
import boto3
import json
import re
import os
from dotenv import load_dotenv

main = Blueprint('main', __name__)

# Claude model + region info
load_dotenv()
model_id = os.getenv("CLAUDE_MODEL_ID")
region = "us-east-1"
client = boto3.client("bedrock-runtime", region_name=region)

# Claude interaction function
def query_claude(prompt):
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 500,
        "temperature": 0.7,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = client.invoke_model(
        modelId=model_id,
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json"
    )

    response_json = json.loads(response['body'].read().decode("utf-8"))
    print("Claude RAW:", response_json)

    # Extract the actual content string
    content_text = response_json.get("content", [])[0].get("text", "")
    print("Claude TEXT Block:", content_text)

    # Extract JSON inside ```json ... ``` from the content text
    match = re.search(r'```json\s*(\{.*?\})\s*```', content_text, re.DOTALL)
    if match:
        json_str = match.group(1)
        print("CLEANED JSON STRING:", json_str)
        return json_str
    else:
        raise ValueError("❌ Claude response did not contain valid JSON inside ```json ... ``` block.")

# Home route with daily Claude tip
@main.route("/")
def home():
    tip_prompt = "Give me one practical AWS SysOps Administrator tip with an example."
    tip = query_claude(tip_prompt)
    return render_template("home.html", message="Mentra is live!", tip=tip)

# Quiz route with Claude-generated MCQ
@main.route("/quiz")
def quiz():
    prompt = (
        "Generate one multiple-choice quiz question related to the AWS Certified SysOps Administrator - Associate exam (SOA-C02). "
        "Use real AWS topics from the exam guide or whitepapers. "
        "Format strictly as JSON with the following keys: "
        "'question', 'choices' (list of 4), 'correct_index' (0-based), and 'explanation'. "
        "Return only the JSON object and no extra text."
    )
    try:
        quiz_raw = query_claude(prompt)
        data = json.loads(quiz_raw)

        return render_template(
            "quiz.html",
            question=data.get("question"),
            choices=data.get("choices"),
            correct_index=data.get("correct_index"),
            explanation=data.get("explanation")
        )
    except Exception as e:
        return f"❌ Failed to load quiz: {e}"

