import time
import anthropic
import os
import base64
import io
from PIL import Image
import numpy as np
from typing import List, Dict, Union
from langchain.schema import SystemMessage, HumanMessage, AIMessage


class ChatClaude:
    """
    A chat class compatible with the Claude API (image support)
    """

    def __init__(
        self,
        model_name: str = "claude-3-7-sonnet-20250219",
        temperature: float = 0.5,
        max_tokens: int = 4096,
        system_prompt: str = "You are a helpful assistant.",
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.system_prompt = system_prompt
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")

        if self.api_key is None:
            raise ValueError("Anthropic API Key is missing. Set ANTHROPIC_API_KEY in environment variables.")

        self.client = anthropic.Anthropic(api_key=self.api_key)

    def _image_to_base64(self, image_input: Union[str, np.ndarray]) -> str:
        """
        Convert image to base64 encoded string
        """
        if isinstance(image_input, str):
            # read image from file path
            with open(image_input, "rb") as image_file:
                image_bytes = image_file.read()
        elif isinstance(image_input, np.ndarray):
            # EN: Convert NumPy array (image) to PIL image and encode as JPEG
            image = Image.fromarray(image_input).convert("RGB")
            image_bytes_io = io.BytesIO()
            image.save(image_bytes_io, format="JPEG")
            image_bytes = image_bytes_io.getvalue()
        else:
            raise ValueError("Invalid image input. Provide a file path or a NumPy array.")

        # encode the image bytes
        return base64.b64encode(image_bytes).decode("utf-8")

    def _format_messages(self, messages: List[Union[SystemMessage, HumanMessage, AIMessage, Dict[str, Union[str, Dict]]]]) -> List[Dict[str, Union[str, Dict]]]:
        """
        Convert LangChain message format to Claude API format (with image support)
        """
        claude_messages = []

        for message in messages:
            if isinstance(message, SystemMessage):
                self.system_prompt = message.content
                continue
            elif isinstance(message, HumanMessage):
                role = "user"
                content = message.content
            elif isinstance(message, AIMessage):
                role = "assistant"
                content = message.content
            elif isinstance(message, dict):
                role = message["role"]
                content = message["content"]
            elif isinstance(message, str):
                role = "assistant"
                content = message
            else:
                raise ValueError(f"Invalid message format: {message}")

            # if it contains text data, add it as is
            if isinstance(content, str):
                claude_messages.append({"role": role, "content": content})
            # if it contains image data, convert to base64
            elif isinstance(content, dict) and content.get("type") == "image":
                image_data = self._image_to_base64(content["data"])
                claude_messages.append({
                    "role": role,
                    "content": {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image_data
                        }
                    }
                })
            elif isinstance(content, list):
                base64_data = content[1]['image_url']["url"].replace("data:image/jpeg;base64,", "")
                text = content[0]['text']
                content = [
                    {
                        "type": "text",
                        "text": text
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": base64_data
                        }
                    },
                ]
                claude_messages.append({"role": role, "content": content})
            else:
                raise ValueError("Invalid message format: must be str or image dict.")

        return claude_messages

    def chat(self, messages: List[Dict[str, Union[str, Dict]]]) -> str:
        """
        Send a request to the Claude API and have a conversation with text or images
        """
        num_attempts = 0
        formatted_messages = self._format_messages(messages)

        while num_attempts < 10:
            try:
                response = self.client.messages.create(
                    model=self.model_name,
                    system=self.system_prompt,
                    messages=formatted_messages,
                    temperature=self.temperature,
                    top_p=0.95,
                    max_tokens=self.max_tokens,
                )
                return response.content[0].text.strip()
            except anthropic.AuthenticationError as e:
                print(e)
                return None
            except anthropic.RateLimitError as e:
                print(f"Rate limit exceeded: {e}")
                print("Sleeping for 10s...")
                time.sleep(10)
                num_attempts += 1
            except Exception as e:
                print(f"Error: {e}")
                print("Sleeping for 10s...")
                time.sleep(10)
                num_attempts += 1

        raise ValueError("Claude API request failed after multiple attempts.")

    def invoke(self, messages: List[Dict[str, Union[str, Dict]]]) -> str:
        """
        Provide the same interface as LangChain's `invoke()`
        """
        return self.chat(messages)
