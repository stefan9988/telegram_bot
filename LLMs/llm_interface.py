from abc import ABC, abstractmethod
from typing import Optional, Dict, Tuple

class LLM(ABC):
    """
    An abstract base class (interface) for a Large Language Model client.

    This interface defines the essential contract for interacting with an LLM,
    ensuring that different implementations (e.g., Azure, Bedrock, local models)
    can be used interchangeably.

    Attributes:
        model_id (str): The identifier for the specific model being used.
        system_message (str): A system message to set context for the conversation.
        max_tokens (int): The maximum number of tokens to generate in a response.
        temperature (float): The sampling temperature for controlling randomness.
        top_p (float): The nucleus sampling parameter for controlling diversity.
    """

    def __init__(
        self,
        model_id: str,
        system_message: str,
        max_tokens: int,
        temperature: float,
        top_p: float
    ):
        """
        Initializes common configuration for the LLM.
        """
        self.model_id = model_id
        self.system_message = system_message
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p

    @abstractmethod
    def conv(self, message: str, max_retries: int = 3) -> Tuple[str, Optional[Dict[str, int]]]:
        """
        Sends a single message to the language model and retrieves the response.

        This method must be implemented by any concrete subclass.

        Args:
            message (str): The user's input message to send to the model.
            max_retries (int): The maximum number of times to retry on failure
                               (e.g., due to rate limiting).

        Returns:
            Tuple[str, Optional[Dict[str, int]]]: A tuple containing:
                - The model's response message (str).
                - A dictionary with token usage information:
                  {'input_tokens': ..., 'output_tokens': ..., 'total_tokens': ...}
                  or None if usage info is not available.
        """
        pass