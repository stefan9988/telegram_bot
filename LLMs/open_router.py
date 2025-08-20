import requests
import json
import time
import logging
from typing import Tuple, Dict, Optional
from .llm_interface import LLM

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class OpenRouterLLM(LLM):
    """
    A concrete implementation of the LLM interface for the OpenRouter API.
    """
    API_URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(
        self,
        api_key: str,
        model_id: str,
        system_message: str = "You are a helpful assistant.",
        max_tokens: int = 1024,
        temperature: float = 0.7,
        top_p: float = 1.0
    ):
        """
        Initializes the OpenRouter client.

        Args:
            api_key (str): Your OpenRouter API key.
            model_id (str): The model identifier (e.g., 'deepseek/deepseek-chat-v3-0324:free').
            system_message (str): A system message to set context.
            max_tokens (int): The maximum number of tokens for the response.
            temperature (float): The sampling temperature.
            top_p (float): The nucleus sampling parameter.
        """
        super().__init__(model_id, system_message, max_tokens, temperature, top_p)
        if not api_key:
            raise ValueError("OpenRouter API key is required.")
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def conv(self, message: str, max_retries: int = 3) -> Tuple[str, Optional[Dict[str, int]]]:
        """
        Sends a message to the OpenRouter API and retrieves the response.
        Implements retry logic for handling transient errors.
        """
        messages = [
            {"role": "system", "content": self.system_message},
            {"role": "user", "content": message}
        ]

        data = {
            "model": self.model_id,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
        }

        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.API_URL,
                    headers=self.headers,
                    data=json.dumps(data)
                )
                # Raise an exception for bad status codes (4xx or 5xx)
                response.raise_for_status()

                json_response = response.json()

                # Check for an error key in the successful (200 OK) response
                if 'error' in json_response:
                    error_details = json_response.get('error', {})
                    error_code = error_details.get('code', 'Unknown code')
                    error_message = error_details.get('message', 'Unknown API error')

                    # Include metadata if available for easier debugging
                    metadata = error_details.get('metadata')
                    if isinstance(metadata, dict):
                        meta_info = ", ".join(f"{k}={v}" for k, v in metadata.items())
                        error_message = f"{error_message} ({meta_info})"

                    raise requests.exceptions.HTTPError(
                        f"OpenRouter API Error [{error_code}]: {error_message}"
                    )
                

                # Extract the response text
                response_text = json_response['choices'][0]['message']['content']

                # Extract token usage and map to the interface's expected keys
                token_usage = None
                if 'usage' in json_response and json_response['usage']:
                    usage_data = json_response['usage']
                    token_usage = {
                        'input_tokens': usage_data.get('prompt_tokens'),
                        'output_tokens': usage_data.get('completion_tokens'),
                        'total_tokens': usage_data.get('total_tokens')
                    }
                
                return response_text, token_usage

            except requests.exceptions.RequestException as e:
                logger.warning(
                    f"Request failed on attempt {attempt + 1}/{max_retries}: {e}"
                )
                if 'OpenRouter API Error' in str(e):
                    raise
                if attempt + 1 == max_retries:
                    raise  # Re-raise the exception after the last retry
                time.sleep(2 ** attempt)  # Exponential backoff

        # This part should not be reached if max_retries > 0
        raise Exception("Failed to get a response after all retries.")
