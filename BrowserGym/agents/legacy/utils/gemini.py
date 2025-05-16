import time
import os
import base64
import io
from PIL import Image
import numpy as np
from typing import List, Dict, Union
from langchain.schema import SystemMessage, HumanMessage, AIMessage
import google.generativeai as genai
from google.generativeai.protos import Part, Content
from typing import Optional
from google.generativeai.types.safety_types import HarmCategory, HarmBlockThreshold




class ChatGemini:
    """
    A chat class compatible with the Gemini API (image support)
    """

    def __init__(
        self,
        model_name: str = "gemini-2.0-flash",
        temperature: float = 0.5,
        max_tokens: Optional[int] = None, 
        system_prompt: Optional[str] = "You are a helpful assistant.",
        top_p: float = 0.95,
        top_k: Optional[int] = None,
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.system_prompt = system_prompt
        self.top_p = top_p
        self.top_k = top_k
        self.api_key = os.environ.get("GEMINI_API_KEY")

        if self.api_key is None:
            raise ValueError(
                "Google API Key is missing. Set GEMINI_API_KEY in environment variables."
            )

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)
        self.chat_session = None

    def _image_to_part(self, image_input: Union[str, np.ndarray, Image.Image]) -> Part:
        """
        Convert image input to Gemini API Part object
        """
        if isinstance(image_input, str):
            image = Image.open(image_input)
        elif isinstance(image_input, np.ndarray):
            image = Image.fromarray(image_input)
        elif isinstance(image_input, Image.Image):
            image = image_input
        else:
            raise ValueError("Invalid image input. Provide a file path, a NumPy array, or a PIL Image object.")

        image_bytes_io = io.BytesIO()
        image.save(image_bytes_io, format="JPEG")
        image_bytes = image_bytes_io.getvalue()

        return Part(
            data=image_bytes,
            mime_type="image/jpeg"
        )
    
    def start_or_get_chat(self, messages: List[Union[SystemMessage, HumanMessage, AIMessage, Dict]]):
        """
        Start a new chat session or reuse an existing one.
        If a system message is present, it is added to the beginning of the history.
        """
        
        history = []
        system_message_content = None
        
        for msg in messages:
            if isinstance(msg, SystemMessage):
                system_message_content = msg.content
                break
            elif isinstance(msg, dict) and msg.get("role") == "system":
                 system_message_content = msg["content"]
                 break
            
        for i, msg in enumerate(messages):
            if isinstance(msg, (HumanMessage, AIMessage)):
                history = [self._convert_message_to_content(m) for m in messages[i:]]
                break
            elif isinstance(msg, dict) and msg.get("role") in ("user", "model"):
                history = [self._convert_message_to_content(m) for m in messages[i:]]
                break
    

        if system_message_content:
            if not self.chat_session or not self.chat_session.history:
                # Start a new chat session with the system message
                initial_history = [
                    Content(role='user', parts=[Part(text=system_message_content)]),
                    Content(role='model', parts=[Part(text="OK")]),
                ]
                initial_history.extend(history)
                self.chat_session = self.model.start_chat(history=initial_history)
            else:
                initial_history = [
                    Content(role='user', parts=[Part(text=system_message_content)]),
                    Content(role='model', parts=[Part(text="OK")]),
                    ]
                initial_history.extend(history)
                self.chat_session = self.model.start_chat(history=initial_history)

        else:
            if not self.chat_session or not self.chat_session.history:
                self.chat_session = self.model.start_chat(history=history)        
        
        
    def _convert_message_to_content(self, message: Union[SystemMessage, HumanMessage, AIMessage, Dict]) -> Content:
        """
        Convert LangChain/Dict format message to Gemini API Content object
        """
        if isinstance(message, SystemMessage):
            return None
        elif isinstance(message, HumanMessage):
            role = "user"
            content_parts = self._process_message_content(message.content)
        elif isinstance(message, AIMessage):
            role = "model"
            content_parts = self._process_message_content(message.content)
        elif isinstance(message, dict):
            role = message["role"]
            content_parts = self._process_message_content(message["content"])
        else:
            raise ValueError(f"Invalid message format: {message}")

        return Content(role=role, parts=content_parts)


    def _process_message_content(self, content: Union[str, List[Dict], Dict]) -> List[Part]:
        """
        Convert message content (string, image, or list of them) to a list of Part objects
        """
        parts = []
        if isinstance(content, str):
            parts.append(Part(text=content))
        elif isinstance(content, list):
            for item in content:
                if isinstance(item, str):
                    parts.append(Part(text=item))
                elif isinstance(item, dict) and item.get("type") == "text":
                     parts.append(Part(text=item["text"]))
                elif isinstance(item, dict) and item.get("type") == "image_url":
                    if item['image_url'].get("url").startswith("data:image"):
                        base64_data = item["image_url"]["url"].split(",")[1]
                        image_bytes = base64.b64decode(base64_data)
                        parts.append(Part(
                            inline_data={
                                "mime_type": "image/jpeg",
                                "data": image_bytes
                            }
                        ))
                    else:
                        image_part = self._image_to_part(item["image_url"]["url"])
                        parts.append(image_part)

                elif isinstance(item, dict) and item.get("type") == "image":
                    parts.append(Part(data=item["source"]["data"], mime_type=item["source"]["media_type"]))

                else:
                    raise ValueError(f"Unsupported content item: {item}")

        elif isinstance(content, dict) and content.get("type") == "image":
            image_data = self._image_to_part(content["data"])
            parts.append(image_data)

        else:
            raise ValueError(f"Unsupported content type: {type(content)}")
        return parts

    def chat(self, messages: List[Union[SystemMessage, HumanMessage, AIMessage, Dict]]) -> str:
        """
        Send a request to the Gemini API (new session each time)
        """
        num_attempts = 0
        history = []
        system_message_content = None
        
        for msg in messages:
            if isinstance(msg, SystemMessage):
                system_message_content = msg.content
                break
            elif isinstance(msg, dict) and msg.get("role") == "system":
                 system_message_content = msg["content"]
                 break

        if system_message_content:
            history.append(Content(role='user', parts=[Part(text=system_message_content)]))
            history.append(Content(role='model', parts=[Part(text="OK")]))

        for msg in messages:
            if isinstance(msg, (SystemMessage, Dict)) and (isinstance(msg, SystemMessage) or msg.get("role") == "system"):
                continue
            content = self._convert_message_to_content(msg)
            if content:
                history.append(content)
                
        last_message = None
        for msg in reversed(messages):
            if isinstance(msg, (HumanMessage, AIMessage, Dict)):
                if isinstance(msg, Dict) and msg["role"] not in ("user", "model"):
                    continue
                last_message = msg
                break

        if not last_message:
          raise ValueError("No valid user or model message found for sending.")
          
        chat_session = self.model.start_chat(history=history)


        while num_attempts < 20:
            try:
                if isinstance(last_message, (HumanMessage, AIMessage)):
                    last_message_content = last_message.content
                else:
                    last_message_content = last_message["content"]

                response = chat_session.send_message(
                    content=self._process_message_content(last_message_content),
                    generation_config=genai.types.GenerationConfig(
                        temperature=self.temperature,
                        top_p=self.top_p,
                        top_k=self.top_k,
                        max_output_tokens=self.max_tokens,
                    ),
                    safety_settings={
                        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    },
                )
                return response.text.strip()
            except Exception as e:
                if "400" in str(e) and "invalid" in str(e).lower():
                    print(f"API Error (Invalid Request): {e}")
                    if "Please ensure that `messages` is a list of non-empty `content`" in str(e):
                        print("The error indicates an empty or invalid message. Check your message formatting.")
                    return None
                elif "429" in str(e):
                     print(f"Rate limit exceeded: {e}")
                     print("Sleeping for 30s...")
                     time.sleep(30)
                     num_attempts += 1

                else:
                    print(f"API Error: {e}")
                    print("Sleeping for 30s...")
                    time.sleep(30)
                    num_attempts += 1

        raise ValueError("Gemini API request failed after multiple attempts.")

    def invoke(self, messages: List[Union[SystemMessage, HumanMessage, AIMessage, Dict]]) -> str:
        """
        Provide the same interface as LangChain's `invoke()`
        """
        return self.chat(messages)


if __name__ == "__main__":
    chat_gemini = ChatGemini()
    response = chat_gemini.chat([
        SystemMessage(content="Hello, Gemini!"),
        HumanMessage(content="How are you?"),
        AIMessage(content="I'm fine, thank you!"),
    ])
    print(response)