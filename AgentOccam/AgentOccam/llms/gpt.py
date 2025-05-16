import openai
from openai import OpenAI, AzureOpenAI
import time
import numpy as np
from PIL import Image
import base64
import io
import os
AZURE_OPENAI_API_KEY = os.environ.get("AZURE_OPENAI_API_KEY", None)
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT", None)
headers = {
  "Content-Type": "application/json",
  "Authorization": f"Bearer {AZURE_OPENAI_API_KEY}"
}
DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant."


def call_gpt(prompt, model_id="gpt-3.5-turbo", system_prompt=DEFAULT_SYSTEM_PROMPT):
    num_attempts = 0
    while True:
        if num_attempts >= 10:
            raise ValueError("OpenAI request failed.")
        try:
            response = OpenAI().chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.95,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None
            )   
            return response.choices[0].message.content.strip()
        except openai.AuthenticationError as e:
            print(e)
            return None
        except openai.RateLimitError as e:
            print(e)
            print("Sleeping for 10s...")
            time.sleep(10)
            num_attempts += 1
        except Exception as e:
            print(e)
            print("Sleeping for 10s...")
            time.sleep(10)
            num_attempts += 1


def arrange_message_for_gpt(item_list):
    def image_path_to_bytes(file_path):
        with open(file_path, "rb") as image_file:
            image_bytes = image_file.read()
        return image_bytes
    combined_item_list = []
    previous_item_is_text = False
    text_buffer = ""
    for item in item_list:
        if item[0] == "image":
            if len(text_buffer) > 0:
                combined_item_list.append(("text", text_buffer))
                text_buffer = ""
            combined_item_list.append(item)
            previous_item_is_text = False
        else:
            if previous_item_is_text:
                text_buffer += item[1]
            else:
                text_buffer = item[1]
            previous_item_is_text = True
    if item_list[-1][0] != "image" and len(text_buffer) > 0:
        combined_item_list.append(("text", text_buffer))
    content = []
    for item in combined_item_list:
        item_type = item[0]
        if item_type == "text":
            content.append({
                "type": "text",
                "text": item[1]
            })
        elif item_type == "image":
            if isinstance(item[1], str):
                image_bytes = image_path_to_bytes(item[1])
                image_data = base64.b64encode(image_bytes).decode("utf-8")
            elif isinstance(item[1], np.ndarray):
                image = Image.fromarray(item[1]).convert("RGB")
                width, height = image.size
                image = image.resize((int(0.5*width), int(0.5*height)), Image.LANCZOS)
                image_bytes = io.BytesIO()
                image.save(image_bytes, format='JPEG')
                image_bytes = image_bytes.getvalue()
                image_data = base64.b64encode(image_bytes).decode("utf-8")
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_data}"
                },
            })
    messages = [
        {
            "role": "user",
            "content": content
        }
    ]
    return messages


def call_gpt_with_messages(messages, model_id="gpt-3.5-turbo", system_prompt=DEFAULT_SYSTEM_PROMPT):
    client = OpenAI() if not AZURE_OPENAI_ENDPOINT else AzureOpenAI(azure_endpoint = AZURE_OPENAI_ENDPOINT, api_key=AZURE_OPENAI_API_KEY, api_version="2024-05-01-preview")
    num_attempts = 0
    while True:
        if num_attempts >= 10:
            raise ValueError("OpenAI request failed.")
        try:
            if any("image" in c["type"] for m in messages for c in m["content"]):
                # print("messages:", messages)
                response = client.chat.completions.create(
                    model=model_id,
                    messages=messages if messages[0]["role"] == "system" else [{"role": "system", "content": system_prompt}] + messages,
                    temperature=0.5,
                    top_p=0.95,
                    frequency_penalty=0,
                    presence_penalty=0,
                    stop=None
                )
                return response.choices[0].message.content.strip()
            else:
                response = client.chat.completions.create(
                    model=model_id,
                    messages=messages if messages[0]["role"] == "system" else [{"role": "system", "content": system_prompt}] + messages,
                    temperature=0.5,
                    top_p=0.95,
                    frequency_penalty=0,
                    presence_penalty=0,
                    stop=None
                )
                return response.choices[0].message.content.strip()
        except openai.AuthenticationError as e:
            print(e)
            return None
        except openai.RateLimitError as e:
            print(e)
            print("Sleeping for 10s...")
            time.sleep(10)
            num_attempts += 1
        except Exception as e:
            print(e)
            print("Sleeping for 10s...")
            time.sleep(10)
            num_attempts += 1


if __name__ == "__main__":
    prompt = '''CURRENT OBSERVATION:
RootWebArea [2634] 'My Account'
	link [3987] 'My Account'
	link [3985] 'My Wish List'
	link [3989] 'Sign Out'
	text 'Welcome to One Stop Market'
	link [3800] 'Skip to Content'
	link [3809] 'store logo'
	link [3996] 'My Cart'
	combobox [4190] 'Search' [required: False]
	link [4914] 'Advanced Search'
	button [4193] 'Search' [disabled: True]
	tablist [3699]
		tabpanel
			menu "[3394] 'Beauty & Personal Care'; [3459] 'Sports & Outdoors'; [3469] 'Clothing, Shoes & Jewelry'; [3483] 'Home & Kitchen'; [3520] 'Office Products'; [3528] 'Tools & Home Improvement'; [3533] 'Health & Household'; [3539] 'Patio, Lawn & Garden'; [3544] 'Electronics'; [3605] 'Cell Phones & Accessories'; [3620] 'Video Games'; [3633] 'Grocery & Gourmet Food'"
	main
		heading 'My Account'
		text 'Contact Information'
		text 'Emma Lopez'
		text 'emma.lopezgmail.com'
		link [3863] 'Change Password'
		text 'Newsletters'
		text "You aren't subscribed to our newsletter."
		link [3877] 'Manage Addresses'
		text 'Default Billing Address'
		group [3885]
			text 'Emma Lopez'
			text '101 S San Mateo Dr'
			text 'San Mateo, California, 94010'
			text 'United States'
			text 'T:'
			link [3895] '6505551212'
		text 'Default Shipping Address'
		group [3902]
			text 'Emma Lopez'
			text '101 S San Mateo Dr'
			text 'San Mateo, California, 94010'
			text 'United States'
			text 'T:'
			link [3912] '6505551212'
		link [3918] 'View All'
		table 'Recent Orders'
			row '| Order | Date | Ship To | Order Total | Status | Action |'
			row '| --- | --- | --- | --- | --- | --- |'
			row "| 000000170 | 5/17/23 | Emma Lopez | 365.42 | Canceled | View OrderReorder\tlink [4110] 'View Order'\tlink [4111] 'Reorder' |"
			row "| 000000189 | 5/2/23 | Emma Lopez | 754.99 | Pending | View OrderReorder\tlink [4122] 'View Order'\tlink [4123] 'Reorder' |"
			row "| 000000188 | 5/2/23 | Emma Lopez | 2,004.99 | Pending | View OrderReorder\tlink [4134] 'View Order'\tlink [4135] 'Reorder' |"
			row "| 000000187 | 5/2/23 | Emma Lopez | 1,004.99 | Pending | View OrderReorder\tlink [4146] 'View Order'\tlink [4147] 'Reorder' |"
			row "| 000000180 | 3/11/23 | Emma Lopez | 65.32 | Complete | View OrderReorder\tlink [4158] 'View Order'\tlink [4159] 'Reorder' |"
		link [4165] 'My Orders'
		link [4166] 'My Downloadable Products'
		link [4167] 'My Wish List'
		link [4169] 'Address Book'
		link [4170] 'Account Information'
		link [4171] 'Stored Payment Methods'
		link [4173] 'My Product Reviews'
		link [4174] 'Newsletter Subscriptions'
		heading 'Compare Products'
		text 'You have no items to compare.'
		heading 'My Wish List'
		text 'You have no items in your wish list.'
	contentinfo
		textbox [4177] 'Sign Up for Our Newsletter:' [required: False]
		button [4072] 'Subscribe'
		link [4073] 'Privacy and Cookie Policy'
		link [4074] 'Search Terms'
		link [4075] 'Advanced Search'
		link [4076] 'Contact Us'
		text 'Copyright 2013-present Magento, Inc. All rights reserved.'
		text 'Help Us Keep Magento Healthy'
		link [3984] 'Report All Bugs'
Today is 6/12/2023. Base on the aforementioned webpage, tell me how many fulfilled orders I have over the past month, and the total amount of money I spent over the past month.'''
    print(call_gpt(prompt=prompt, model_id="gpt-4-turbo"))