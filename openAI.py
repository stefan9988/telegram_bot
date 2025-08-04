from openai import AzureOpenAI, RateLimitError, APIError 
from typing import Optional, Dict, Any, Tuple, List 
import time
import random
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AzureChat:
    """
    A class to interact with Azure OpenAI's chat models, designed to have
    similar functionality to the BedrockChat class.
    
    Attributes:
        model_id (str): The Azure OpenAI deployment name for the model.
        system_message (str): The system message to set context for the conversation.
        max_tokens (int): Maximum number of tokens to generate in the response.
        temperature (float): Controls randomness in the response (0.0 to 1.0).
        top_p (float): Controls diversity via nucleus sampling (0.0 to 1.0).
        client (AzureOpenAI): The AzureOpenAI client instance.
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
        api_version: str = "2024-10-21"
    ):
        """
        Initialize a new AzureChat instance.
        
        Args:
            model_id (str): The Azure OpenAI deployment name for the model (e.g., "gpt-35-turbo-deployment").
                            This MUST be provided.
            system_message (str): System message to set context for the conversation.
            max_tokens (int): Maximum number of tokens to generate in the response.
            temperature (float): Controls randomness in the response (0.0 to 1.0).
            top_p (float): Controls diversity via nucleus sampling (0.0 to 1.0).
            api_version (str): The API version for the Azure OpenAI client.
            
        Raises:
            ValueError: If Azure OpenAI API key, endpoint, or model_id are not properly configured.
        """
        
        if not api_key:
            raise ValueError("AZURE_OPENAI_API_KEY not found in environment variables.")
        if not azure_endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT not found in environment variables.")
        if not model_id:
            raise ValueError("model_id (Azure deployment name) must be provided.")

        self.client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=azure_endpoint
        )
        
        # Configuration parameters
        self.model_id = model_id
        self.system_message = system_message
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p

    def conv(self, message: str, max_retries: int = 3) -> Tuple[str, Optional[Dict[str, int]]]:
        """
        Send a message to the Azure OpenAI model and get its response.
        
        Args:
            message (str): The input message to send to the model.
            max_retries (int, optional): Maximum number of retry attempts for rate limit errors. Defaults to 3.
            
        Returns:
            Tuple[str, Optional[Dict[str, int]]]: A tuple containing:
                - The model's response message (str).
                - A dictionary with token usage information (Optional[Dict[str, int]])
                  formatted as {'input_tokens': ..., 'output_tokens': ..., 'total_tokens': ...},
                  or None if usage info is not available from the response.
            
        Raises:
            Exception: If there's an error in the conversation with the model after retries.
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
                
                content = ""
                if response.choices and response.choices[0].message:
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
                    logger.info(f"Rate limit hit. Retrying in {delay:.2f} seconds. Attempt {attempt + 1}/{max_retries} retries.")
                    time.sleep(delay)
                    continue
                else:
                    logger.info(f"Maximum retry attempts reached for rate limit after {max_retries} retries.")
                    raise Exception(f"Maximum rate limit retry attempts ({max_retries}) reached: {str(e)}") from e
                
            except APIError as e: # Catch other OpenAI API errors (e.g., authentication, server errors)
                # You could check e.status_code here for more specific handling if needed
                logger.info(f"Azure OpenAI API error: {str(e)}")
                raise Exception(f"Error in conversation with Azure OpenAI model: {str(e)}") from e
                
            except Exception as e: # Catch any other unexpected errors
                logger.info(f"An unexpected error occurred: {str(e)}")
                # If this is the last attempt, re-raise. Otherwise, could retry for some generic errors too.
                if attempt < max_retries:
                    delay = (2 ** attempt) + random.uniform(0, 1) # Basic retry for generic error too
                    logger.info(f"Unexpected error. Retrying in {delay:.2f} seconds. Attempt {attempt + 1}/{max_retries} retries.")
                    time.sleep(delay)
                    continue
                else:
                    raise Exception(f"Unexpected error after {max_retries} retries in conversation with Azure OpenAI model: {str(e)}") from e
        
        raise Exception("Conversation failed unexpectedly after all retries.")
    
