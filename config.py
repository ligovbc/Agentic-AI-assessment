import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration class for the Agentic AI API"""

    # Provider selection
    OPENAI_PROVIDER = os.getenv("OPENAI_PROVIDER", "openai").lower()

    # Regular OpenAI settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Azure OpenAI settings
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

    # Model settings (deployment names for Azure, model names for OpenAI)
    FAST_MODEL = os.getenv("FAST_MODEL", "gpt-4o-mini")
    SLOW_MODEL = os.getenv("SLOW_MODEL", "gpt-4")

    # Flask settings
    FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"

    # Chain-of-thought settings
    DEFAULT_COT_STEPS = 3
    MAX_COT_STEPS = 10

    # Self-consistency settings
    DEFAULT_SELF_CONSISTENCY_SAMPLES = 5
    MAX_SELF_CONSISTENCY_SAMPLES = 15

    @classmethod
    def validate(cls):
        """Validate that required configuration is present"""
        if cls.OPENAI_PROVIDER == "azure":
            if not cls.AZURE_OPENAI_API_KEY:
                raise ValueError("AZURE_OPENAI_API_KEY must be set in environment or .env file")
            if not cls.AZURE_OPENAI_ENDPOINT:
                raise ValueError("AZURE_OPENAI_ENDPOINT must be set in environment or .env file")
        else:
            if not cls.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY must be set in environment or .env file")
        return True
