import boto3
import json
from botocore.exceptions import ClientError

DEFAULT_SYSTEM_PROMPT = '''You are an AI assistant. Your goal is to provide informative and substantive responses to queries.'''

def call_cohere(prompt, model_id="cohere.command-r-plus-v1:0", system_prompt=DEFAULT_SYSTEM_PROMPT):
    client = boto3.client("bedrock-runtime", region_name="us-east-1")

    formatted_prompt = f"{system_prompt}\n{prompt}"

    native_request = {
        "message": formatted_prompt,
        "max_tokens": 512,
        "temperature": 0.5,
    }

    request = json.dumps(native_request)
    try:
        response = client.invoke_model(modelId=model_id, body=request)

    except (ClientError, Exception) as e:
        print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")

    model_response = json.loads(response["body"].read())

    response_text = model_response["text"]
    return response_text

def arrange_message_for_cohere(item_list):
    for item in item_list:
        if item[0] == "image":
            raise NotImplementedError()
    prompt = "".join([item[1] for item in item_list])
    return prompt

def call_cohere_with_messages(messages, model_id="cohere.command-r-plus-v1:0", system_prompt=DEFAULT_SYSTEM_PROMPT):
    return call_cohere(prompt=messages, model_id=model_id, system_prompt=system_prompt)

if __name__ == "__main__":
    print(call_cohere('''Hi'''))
    