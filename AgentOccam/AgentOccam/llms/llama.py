import boto3
import json

DEFAULT_SYSTEM_PROMPT = '''You are an AI assistant. Your goal is to provide informative and substantive responses to queries.'''


def call_llama(prompt, model_id = "meta.llama3-8b-instruct-v1:0", system_prompt=DEFAULT_SYSTEM_PROMPT):
    client = boto3.client("bedrock-runtime", region_name="us-east-1")

    formatted_prompt = f'''\n<|begin_of_text|>\n<|start_header_id|>user<|end_header_id|>\n{system_prompt}\n{prompt}\n<|eot_id|>\n<|start_header_id|>assistant<|end_header_id|>\n'''

    native_request = {
        "prompt": formatted_prompt,
        "max_gen_len": 512,
        "temperature": 0.5,
    }

    request = json.dumps(native_request)

    try:
        response = client.invoke_model(modelId=model_id, body=request)

    except Exception as e:
        raise KeyError(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")

    model_response = json.loads(response["body"].read())

    response_text = model_response["generation"]
    return response_text


def arrange_message_for_llama(item_list):
    for item in item_list:
        if item[0] == "image":
            raise NotImplementedError()
    prompt = "".join([item[1] for item in item_list])
    return prompt


def call_llama_with_messages(messages, model_id="meta.llama3-8b-instruct-v1:0", system_prompt=DEFAULT_SYSTEM_PROMPT):
    return call_llama(prompt=messages, model_id=model_id, system_prompt=system_prompt)


if __name__ == "__main__":
    print(call_llama('''Hi'''))