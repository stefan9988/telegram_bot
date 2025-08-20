from openai import AzureOpenAI, RateLimitError, APIError
from typing import Optional, Dict, Tuple, List
import time
import random
import logging
from .llm_interface import LLM

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AzureChat(LLM):
    """
    A class to interact with Azure OpenAI's chat models, which implements
    the generic LLM interface.
    
    Attributes:
        client (AzureOpenAI): The AzureOpenAI client instance.
        # Inherits model_id, system_message, max_tokens, etc. from LLM
    """

    def __init__(
        self,
        model_id: str,
        api_key: str,
        azure_endpoint: str,
        system_message: str = "You are a helpful AI assistant.",
        max_tokens: int = 4096,
        temperature: float = 0.3,
        top_p: float = 0.9,
        api_version: str = "2024-02-01" 
    ):
        """
        Initialize a new AzureChat instance.
        """
        # Call the parent constructor to set up common attributes
        super().__init__(
            model_id=model_id,
            system_message=system_message,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p
        )

        if not api_key:
            raise ValueError("api_key must be provided.")
        if not azure_endpoint:
            raise ValueError("azure_endpoint must be provided.")

        self.client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=azure_endpoint
        )

    def conv(self, message: str, max_retries: int = 3) -> Tuple[str, Optional[Dict[str, int]]]:
        """
        Sends a message to the Azure OpenAI model and gets its response.
        This method implements the abstract `conv` method from the LLM interface.
        """
        messages_payload: List[Dict[str, str]] = []
        if self.system_message:
            messages_payload.append({"role": "system", "content": self.system_message})
        messages_payload.append({"role": "user", "content": message})

        for attempt in range(max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_id,
                    messages=messages_payload,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    top_p=self.top_p,
                )

                content = response.choices[0].message.content or ""
                
                usage_info = None
                if response.usage:
                    usage_info = {
                        'input_tokens': response.usage.prompt_tokens,
                        'output_tokens': response.usage.completion_tokens,
                        'total_tokens': response.usage.total_tokens
                    }

                return content, usage_info

            except RateLimitError as e:
                if attempt < max_retries:
                    delay = (2 ** attempt) + random.uniform(0, 1)
                    logger.warning(f"Rate limit hit. Retrying in {delay:.2f}s...")
                    time.sleep(delay)
                else:
                    logger.error("Max retries reached for rate limit.")
                    raise Exception(f"Rate limit error after {max_retries} retries.") from e
            
            except APIError as e:
                logger.error(f"Azure OpenAI API error: {e}")
                raise Exception("API error during conversation.") from e
            
            except Exception as e:
                logger.error(f"An unexpected error occurred: {e}")
                if attempt < max_retries:
                    delay = (2 ** attempt) + random.uniform(0, 1)
                    logger.warning(f"Retrying after unexpected error in {delay:.2f}s...")
                    time.sleep(delay)
                else:
                    raise Exception("Unexpected error after max retries.") from e
        
        # This line should not be reachable if logic is correct, but serves as a failsafe
        raise Exception("Conversation failed unexpectedly after all retries.")