"""
Test client for the Agentic AI API
Demonstrates how to use both /v1/completions and /v1/chat/completions endpoints
"""

import requests
import json
from typing import Dict, Any


class AgenticAIClient:
    """Client for interacting with the Agentic AI API"""

    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url

    def completions(
        self,
        prompt: str,
        num_self_consistency: int = 5,
        num_cot: int = 3,
        model: str = "fast",
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Call the /v1/completions endpoint

        Args:
            prompt: The question or prompt
            num_self_consistency: Number of reasoning paths
            num_cot: Number of chain-of-thought steps
            model: "fast" or "slow"
            temperature: Response randomness (0.0-2.0)

        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}/v1/completions"

        data = {
            "prompt": prompt,
            "num_self_consistency": num_self_consistency,
            "num_cot": num_cot,
            "model": model,
            "temperature": temperature
        }

        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def chat_completions(
        self,
        message: str,
        num_self_consistency: int = 5,
        num_cot: int = 3,
        model: str = "fast",
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Call the /v1/chat/completions endpoint

        Args:
            message: The user message
            num_self_consistency: Number of reasoning paths
            num_cot: Number of chain-of-thought steps
            model: "fast" or "slow"
            temperature: Response randomness (0.0-2.0)

        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}/v1/chat/completions"

        data = {
            "messages": [
                {"role": "user", "content": message}
            ],
            "num_self_consistency": num_self_consistency,
            "num_cot": num_cot,
            "model": model,
            "temperature": temperature
        }

        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def health_check(self) -> Dict[str, Any]:
        """Check if the API is running"""
        url = f"{self.base_url}/"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()


def print_response(response: Dict[str, Any], endpoint_type: str = "completions"):
    """Pretty print the API response"""

    print("\n" + "=" * 80)
    print(f"RESPONSE FROM {endpoint_type.upper()}")
    print("=" * 80)

    if endpoint_type == "completions":
        print(f"\nPrompt: {response.get('prompt', 'N/A')}")
        print(f"Model Used: {response.get('model_used', 'N/A')}")
        print(f"Confidence Score: {response.get('confidence_score', 0):.2%}")
        print(f"\nReasoning Summary:\n{response.get('reasoning_summary', 'N/A')}")

        print("\n" + "-" * 80)
        print("CHAIN OF THOUGHT (Primary Path)")
        print("-" * 80)
        for step in response.get('chain_of_thought', []):
            print(f"\nStep {step['step_number']}:")
            print(f"  Reasoning: {step['reasoning']}")
            print(f"  Conclusion: {step['intermediate_conclusion']}")

        print("\n" + "-" * 80)
        print("SELF-CONSISTENCY SAMPLES")
        print("-" * 80)
        for sample in response.get('self_consistency_samples', []):
            print(f"\nSample {sample['sample_number']}:")
            print(f"  Answer: {sample['final_answer'][:100]}...")

        print("\n" + "-" * 80)
        print("FINAL ANSWER")
        print("-" * 80)
        print(f"\n{response.get('final_answer', 'N/A')}")

    elif endpoint_type == "chat":
        print(f"\nModel: {response.get('model', 'N/A')}")
        print(f"Message: {response['choices'][0]['message']['content']}")

        metadata = response.get('agentic_metadata', {})
        print(f"\nConfidence Score: {metadata.get('confidence_score', 0):.2%}")
        print(f"Reasoning Summary: {metadata.get('reasoning_summary', 'N/A')}")

    print("\n" + "=" * 80)


def main():
    """Run test examples"""

    client = AgenticAIClient()

    # Health check
    print("Checking API health...")
    try:
        health = client.health_check()
        print(f"✓ API is running: {health['service']}")
    except Exception as e:
        print(f"✗ Error connecting to API: {e}")
        print("Make sure the server is running with: python app.py")
        return

    # Example 1: Train speed calculation
    print("\n\nExample 1: Train speed calculation (completions endpoint)")
    print("-" * 80)
    try:
        response = client.completions(
            prompt="If a train travels 60 kilometers in 1 hour, how far will it travel in 2.5 hours?",
            num_self_consistency=3,
            num_cot=1,
            model="fast",
            temperature=0.7
        )
        print_response(response, "completions")
    except Exception as e:
        print(f"Error: {e}")

    # Example 2: Logical reasoning with infinitely wide entrance
    print("\n\nExample 2: Logical reasoning (chat endpoint)")
    print("-" * 80)
    try:
        response = client.chat_completions(
            message="Imagine an infinitely wide entrance, which is more likely to pass through it, a military tank or a car?",
            num_self_consistency=3,
            num_cot=1,
            model="fast",
            temperature=0.8
        )
        print_response(response, "chat")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
