import openai
import re
import copy
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    AutoModelForSeq2SeqLM,
)
import ctranslate2
from time import sleep
import tiktoken
from openai import OpenAI

import warnings
warnings.simplefilter("ignore")

input_token_cost_usd_by_model = {
    "gpt-4-1106-preview": 0.01 / 1000,
    "gpt-4": 0.03 / 1000,
    "gpt-4-32k": 0.06 / 1000,
    "gpt-3.5-turbo": 0.001 / 1000,
    "gpt-3.5-turbo-instruct": 0.0015 / 1000,
    "gpt-3.5-turbo-16k": 0.003 / 1000,
    "babbage-002": 0.0016 / 1000,
    "davinci-002": 0.012 / 1000,
    "ada-v2": 0.0001 / 1000,
}

output_token_cost_usd_by_model = {
    "gpt-4-1106-preview": 0.03 / 1000,
    "gpt-4": 0.06 / 1000,
    "gpt-4-32k": 0.12 / 1000,
    "gpt-3.5-turbo": 0.002 / 1000,
    "gpt-3.5-turbo-instruct": 0.002 / 1000,
    "gpt-3.5-turbo-16k": 0.004 / 1000,
    "babbage-002": 0.0016 / 1000,
    "davinci-002": 0.012 / 1000,
    "ada-v2": 0.0001 / 1000,
}

def fill_prompt_template(prompt_template, objective, observation, url, previous_history):
    prompt = copy.deepcopy(prompt_template)
    prompt["input"] = prompt["input"].replace("{objective}", objective)
    if isinstance(observation, dict):
        prompt["input"] = prompt["input"].replace("{observation}", observation["text"])
    else:
        prompt["input"] = prompt["input"].replace("{observation}", observation)
    prompt["input"] = prompt["input"].replace("{url}", url)   
    prompt["input"] = prompt["input"].replace("{previous_actions}", previous_history)   
    return prompt

def filter_quotes_if_matches_template(action):
    if action is None:
        return None

    # Regex pattern to match the entire 'type [X] ["Y"]' template, allowing for Y to be digits as well
    pattern = r'^type \[\d+\] \["([^"\[\]]+)"\]$'
    # Check if the action matches the specific template
    match = re.match(pattern, action)
    if match:
        # Extract the matched part that needs to be unquoted
        y_part = match.group(1)
        # Reconstruct the action string without quotes around Y
        filtered_action = f'type [{match.group(0).split("[")[1].split("]")[0]}] [{y_part}]'
        return filtered_action.strip() # filtered_action.split("\n")[0].strip()
    else:
        # Return the original action if it doesn't match the template
        return action.strip() # action.split("\n")[0].strip()

def parse_action_reason(model_response):
    reason_match = re.search(r'REASON:\s*(.*?)\s*(?=\n[A-Z]|$)', model_response, re.DOTALL) 
    reason = reason_match.group(1) if reason_match else None

    # action_match = re.search(r'ACTION:\s*(.*?)\s*(?=\n[A-Z]|$)', model_response, re.DOTALL) 
    action_match = re.search(r'(?:ACTION|ACTIONS):\s*(.*?)\s*(?=\n[A-Z]|$)', model_response, re.DOTALL) 
    action = action_match.group(1) if action_match else None
    
    action = filter_quotes_if_matches_template(action)
    
    return action, reason

def construct_llm_message_hf(prompt, prompt_mode, model_type="llama2"):
    if model_type == "llama2":
        instruction = "<s>[INST] " + prompt["instruction"]
    else:
        instruction = prompt["instruction"]
    
    messages = [{"role": "system", "content": instruction}]
    
    if prompt["examples"]:
        messages.append({"role": "system", "content": "Here are a few examples:"})
        for example in prompt["examples"]:
            messages.append({"role": "system", "content": f"\n### Input:\n{example['input']}\n\n### Response:\n{example['response']}"})
    
    if model_type == "llama2":
        query = f"\nHere is the current Input. Please respond with REASON and ACTION.\n### Input:\n{prompt['input']}\n[/INST]\n"
    else:
        query = f"\nHere is the current Input. Please respond with REASON and ACTION.\n### Input:\n{prompt['input']}\n\n### Response:"
    
    messages.append({"role": "user", "content": query})
    if prompt_mode == "chat":
        return messages
    elif prompt_mode == "completion":
        all_content = ''.join(message['content'] for message in messages)
        messages_completion = [{"role": "user", "content": all_content}]
        return messages_completion

def construct_llm_message_anthropic(prompt, plan_list=None, action_list=None):
    if plan_list and action_list:
        import os
        from global_utils import CURRENT_DIR

        assert len(plan_list) > 0 and len(action_list) > 0
        plan_instructions = "\n".join(["".join(open(os.path.join(CURRENT_DIR, "prompts", "plan_instructions", f"{p}.txt"), "r").readlines()) for p in plan_list])
        action_instructions = "\n".join(["".join(open(os.path.join(CURRENT_DIR, "prompts", "action_instructions", f"{a}.txt"), "r").readlines()) for a in action_list])
        prompt["instruction"] = prompt["instruction"].replace("{plan_instructions}", plan_instructions)
        prompt["instruction"] = prompt["instruction"].replace("{action_instructions}", action_instructions)

    system_message = prompt["instruction"]
        
    if prompt["examples"]:
        system_message += "\n\n## Here are a few examples:"
        for i, example in enumerate(prompt["examples"]):
            example_input = example["input"]
            example_response = example["response"]
            if "example_format" in prompt.keys():
                system_message += "\n\n"
                system_message += prompt["example_format"].replace("{i}", i).replace("{example_input}", example_input).replace("{example_response}", example_response)
            else:
                system_message += f"\n\n| Example {i}\n\n### Input:\n{example_input}\n\n### Response: Let's think step by step.\n{example_response}"

    if "input_format" in prompt.keys():
        if "{visual_observation}" in prompt.keys():
            from claude import arrange_message_for_claude
            text = prompt["input_format"].replace("{input}", prompt['input'])
            text_prior, text_subsequent = text.split("{visual_observation}")
            messages = arrange_message_for_claude([("text", text_prior), ("image", prompt["{visual_observation}"]), ("text", text_subsequent)])
        else:
            messages = [{"role": "user", "content": [{"type": "text", "text": prompt["input_format"].replace("{input}", prompt['input'])}]}]
    else:
        if "{visual_observation}" in prompt.keys():
            pass
        else:
            messages = [{"role": "user", "content": [{"type": "text", "text": f"## Here is the current Input. Please respond with REASON and ACTION.\n### Input:\n{prompt['input']}\n\n### Response:"}]}]

    return system_message, messages

def construct_llm_message_openai(prompt, prompt_mode, plan_list=None, action_list=None):
    if not (plan_list and action_list):
        messages = [{"role": "system", "content": prompt["instruction"]}]
            
        if prompt["examples"]:
            messages.append({"role": "system", "content": "Here are a few examples:"})
            for example in prompt["examples"]:
                messages.append({"role": "system", "content": f"\n### Input:\n{example['input']}\n\n### Response:\n{example['response']}"})
        
        messages.append({"role": "user", "content": f"Here is the current Input. Please respond with REASON and ACTION.\n### Input:\n{prompt['input']}\n\n### Response:"})
        if prompt_mode == "chat":
            return messages
        elif prompt_mode == "completion":
            all_content = ''.join(message['content'] for message in messages)
            messages_completion = [{"role": "user", "content": all_content}]
            return messages_completion
    import os
    from global_utils import CURRENT_DIR

    assert len(plan_list) > 0 and len(action_list) > 0
    plan_instructions = "\n".join(["".join(open(os.path.join(CURRENT_DIR, "prompts", "plan_instructions", f"{p}.txt"), "r").readlines()) for p in plan_list])
    action_instructions = "\n".join(["".join(open(os.path.join(CURRENT_DIR, "prompts", "action_instructions", f"{a}.txt"), "r").readlines()) for a in action_list])
    prompt["instruction"] = prompt["instruction"].replace("{plan_instructions}", plan_instructions)
    prompt["instruction"] = prompt["instruction"].replace("{action_instructions}", action_instructions)

    messages = [{"role": "system", "content": prompt["instruction"]}]

    if prompt["examples"]:
        messages.append({"role": "system", "content": "## Here are a few examples:"})
        for i, example in enumerate(prompt["examples"]):
            example_input = example["input"]
            example_response = example["response"]
            messages.append({"role": "system", "content": f"| Example {i}\n\n### Input:\n{example_input}\n\n### Response: Let's think step by step.\n{example_response}"})

    if "input_format" in prompt.keys():
        messages.append({"role": "user", "content": prompt["input_format"].replace("{input}", prompt['input'])})
    else:
        messages.append({"role": "user", "content": f"## Here is the current Input. Please respond with PLAN, REASON and ACTION.\n### Input:\n{prompt['input']}\n\n### Response:"})
    if prompt_mode == "chat":
        return messages
    elif prompt_mode == "completion":
        all_content = ''.join(message['content'] for message in messages)
        messages_completion = [{"role": "user", "content": all_content}]
        return messages_completion

def call_anthropic_llm(system_message, messages, model="anthropic.claude-3-haiku-20240307-v1:0", **model_kwargs):
    # Use the native inference API to send a text message to Anthropic Claude.

    import boto3
    import json

    # Create a Bedrock Runtime client in the AWS Region of your choice.
    client = boto3.client("bedrock-runtime", region_name="us-east-1")
    print(system_message, file=open("trash.txt", "a"))
    print("\n".join(item["content"][0]["text"] for item in messages), end="\n"+"#"*100+"\n", file=open("trash.txt", "a"))
    native_request = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 512,
        "temperature": 0.5,
        "system": system_message,
        "messages": messages,
    }

    # Convert the native request to JSON.
    request = json.dumps(native_request)

    try:
        # Invoke the model with the request.
        response = client.invoke_model(modelId=model, body=request)

    except Exception as e:
        raise KeyError(f"ERROR: Can't invoke '{model}'. Reason: {e}")

    # Decode the response body.
    model_response = json.loads(response["body"].read())

    # Extract and print the response text.
    response_text = model_response["content"][0]["text"]
    return response_text

def call_openai_llm(messages, model="gpt-3.5-turbo", **model_kwargs):
    """
    Sends a request with a chat conversation to OpenAI's chat API and returns a response.

    Parameters:
        messages (list)
            A list of dictionaries containing the messages to send to the chatbot.
        model (str)
            The model to use for the chatbot. Default is "gpt-3.5-turbo".
        temperature (float)
            The temperature to use for the chatbot. Defaults to 0. Note that a temperature
            of 0 does not guarantee the same response (https://platform.openai.com/docs/models/gpt-3-5).
    
    Returns:
        response (Optional[dict])
            The response from OpenAI's chat API, if any.
    """
    # client = OpenAI()
    temperature = model_kwargs.get('temperature', 0.7)
    top_p = model_kwargs.get('top_p', 1.0)
    n = model_kwargs.get('n', 1)

    for m in messages:
        print(m["content"], file=open("trash.txt", "a"))
    print("*"*100, file=open("trash.txt", "a"))
    
    num_attempts = 0
    while True:
        if num_attempts >= 10:
            raise ValueError("OpenAI request failed.")
        try:
            if model=="text-davinci-003":
                response = openai.Completion.create(
                model=model,
                prompt=messages[0]["content"],
                temperature=temperature,
                top_p=top_p,
                n=n,
                max_tokens=128)
                return response.choices[0].text.strip()
                        
            response = OpenAI().chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                top_p=top_p,
                n=n
            )
            return response.choices[0].message.content.strip()
        except openai.AuthenticationError as e:
            print(e)
            return None
        except openai.RateLimitError as e:
            print(e)
            print("Sleeping for 10 seconds...")
            sleep(10)
            num_attempts += 1
        except Exception as e:
            print(e)
            print("Sleeping for 10 seconds...")
            sleep(10)
            num_attempts += 1

def get_num_tokens(text: str, model_name: str) -> int:
    tokenizer = tiktoken.encoding_for_model(model_name=model_name)
    return len(tokenizer.encode_ordinary(text))

def calculate_cost_openai(messages: str, response: str, model_name: str) -> int:
    input_text = " ".join([msg["content"] for msg in messages]) 
    num_input_tokens = get_num_tokens(input_text, model_name)
    num_output_tokens = get_num_tokens(response, model_name)
    
    input_token_cost = input_token_cost_usd_by_model.get(model_name, None)
    output_token_cost = output_token_cost_usd_by_model.get(model_name, None)
    if input_token_cost is None or output_token_cost is None:
        print(f"[calculate_cost_openai] unknown model {model_name}")
        return 0
    return num_input_tokens * input_token_cost + num_output_tokens * output_token_cost

def load_tokenizer(mpath, context_size):
    tokenizer = AutoTokenizer.from_pretrained(mpath, return_token_type_ids=False)
    # tokenizer.pad_token = tokenizer.eos_token
    # tokenizer.pad_token_id = tokenizer.eos_token_id
    # tokenizer.model_max_length = context_size
    # tokenizer.padding_side = "right"
    # tokenizer.truncation_side = "left"
    # tokenizer.add_eos_token = True
    return tokenizer

def load_model(mpath, dtype, device="cuda", context_len=4096, is_seq2seq=False, ct2_mpath=None):
    if is_seq2seq:
        model_loader = AutoModelForSeq2SeqLM
    else:
        model_loader = AutoModelForCausalLM

    if dtype == "bf16":
        model = model_loader.from_pretrained(
            mpath,
            max_position_embeddings=context_len,
            low_cpu_mem_usage=True,
            torch_dtype=torch.bfloat16,
            device_map="balanced_low_0",
        )
    elif dtype == "4bit":
        model = model_loader.from_pretrained(
            mpath,
            max_position_embeddings=context_len,
            low_cpu_mem_usage=True,
            load_in_4bit=True,
            device_map="auto",
        )
    elif dtype == "4bit-optimized":
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
        )
        model = model_loader.from_pretrained(
            mpath,
            use_cache=True,
            device_map="auto",
            quantization_config=bnb_config,
            max_position_embeddings=context_len,
        )
    elif dtype == "8bit":
        model = model_loader.from_pretrained(
            mpath,
            max_position_embeddings=context_len,
            low_cpu_mem_usage=True,
            load_in_8bit=True,
            device_map="auto",
        )
    elif dtype == "ct2":
        assert ct2_mpath is not None
        model = ctranslate2.Generator(ct2_mpath, device=device)

    return model

# @torch.no_grad()
# def generate_prediction(
#     inputs,
#     model,
#     tokenizer,
#     max_new_tokens,
#     is_seq2seq=False,
#     **kwargs,
#     # num_beams,
#     # do_sample,
#     # no_repeat_ngram_size,
#     # temperature,
#     # top_k,
#     # top_p,
# ):
#     input_ids = tokenizer(inputs, return_tensors="pt", truncation=True, max_length=tokenizer.model_max_length - max_new_tokens).input_ids
    
#     outputs = model.generate(
#         input_ids=input_ids.cuda(),
#         max_new_tokens=max_new_tokens,
#         **kwargs,
#     ).cpu()

#     torch.cuda.empty_cache()
#     if not is_seq2seq:
#         outputs = outputs[:, input_ids.shape[1] :]

#     prediction = [
#         p.split(tokenizer.pad_token, 1)[0]
#         for p in tokenizer.batch_decode(outputs, skip_special_tokens=True)
#     ][0].strip()
        
#     return prediction

def generate_prediction(
    inputs,
    model,
    tokenizer,
    **kwargs,
):
    inputs = tokenizer([inputs], return_tensors='pt', truncation=True, add_special_tokens=False).to(model.device)
    
    # if torch.cuda.is_available():
    #     inputs = inputs.to('cuda')
    outputs = model.generate(
        input_ids=inputs['input_ids'],
        attention_mask=inputs['attention_mask'],
        **kwargs,
    )
    
    outputs = outputs[:, inputs.input_ids.shape[1] :]
    prediction = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
    return prediction