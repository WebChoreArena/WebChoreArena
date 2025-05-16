import google.generativeai as genai
import os
import time
from google.generativeai.protos import Part
from PIL import Image
import io
import numpy as np

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
genai.configure(api_key=GEMINI_API_KEY)


def _image_to_part(image_input):
    print("before image to part")
    print("type", type(image_input))
    if isinstance(image_input, str):
        image = Image.open(image_input)
    elif isinstance(image_input, Image.Image):
        image = image_input
    # numpy.ndarray
    elif isinstance(image_input, np.ndarray):
        image = Image.fromarray(image_input)
        image = image.convert("RGB")  # Convert to RGB if needed
    else:
        raise ValueError("Unsupported image input type")
    # print("after image to part")
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    image_bytes = buffer.getvalue()

    return Part(
        inline_data={
            "mime_type": "image/jpeg",
            "data": image_bytes,
        }
    )


def arrange_message_for_gemini(item_list):
    has_image = any(item[0] == "image" for item in item_list)
    if not has_image:
        return "".join([item[1] for item in item_list])

    # print("before image append")
    parts = []
    for item in item_list:
        if item[0] == "text":
            # print("before text append")
            parts.append(Part(text=item[1]))
        elif item[0] == "image":
            # print("before image append")
            parts.append(_image_to_part(item[1]))
            # print("after image append")
        else:
            raise ValueError(f"Unsupported item type: {item[0]}")
    return parts


def call_gemini(prompt, model_id="gemini-2.5-pro-preview-03-25", system_prompt=None):
    model = genai.GenerativeModel(model_id)
    num_attempts = 0
    while True:
        if num_attempts >= 10:
            raise ValueError("Gemini request failed.")
        try:
            if isinstance(prompt, str):
                full_prompt = system_prompt + "\n" + prompt if system_prompt else prompt
                response = model.generate_content(full_prompt)
            else:  # List[Part]
                parts = []
                if system_prompt:
                    parts.append(Part(text=system_prompt))
                parts.extend(prompt)
                response = model.generate_content(parts)
            return response.text
        except Exception:
            time.sleep(30)
            num_attempts += 1


def call_gemini_with_messages(messages, model_id="gemini-2.5-pro-preview-03-25", system_prompt=None):
    return call_gemini(prompt=messages, model_id=model_id, system_prompt=system_prompt)


if __name__ == "__main__":
    print(call_gemini('''CURRENT OBSERVATION:
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
Today is 6/12/2023. Base on the aforementioned webpage, tell me how many fulfilled orders I have over the past month, and the total amount of money I spent over the past month.'''))
