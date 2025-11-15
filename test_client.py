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

    def health_check(self) -> Dict[str, Any]:
        """Check if the API is running"""
        url = f"{self.base_url}/"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()


def print_response(response: Dict[str, Any]):
    """Pretty print the API response with step-by-step details"""

    print("\n" + "=" * 80)
    print("RESPONSE")
    print("=" * 80)

    print(f"\nPrompt: {response.get('prompt', 'N/A')}")
    print(f"Model Used: {response.get('model_used', 'N/A')}")

    print("\n" + "=" * 80)
    print("STEP 1: GENERATE MULTIPLE SAMPLES (Each with CoT built-in)")
    print("=" * 80)
    samples = response.get('self_consistency_samples', [])
    print(f"Generated {len(samples)} independent reasoning path(s) in parallel\n")
    for sample in samples:
        print(f"  === Sample {sample['sample_number']} ===")
        reasoning_path = sample.get('reasoning_path', [])
        print(f"  Chain-of-Thought Steps: {len(reasoning_path)}")
        for step in reasoning_path:
            print(f"    Step {step['step_number']}: {step['reasoning'][:60]}...")
        print(f"  Final Answer: {sample['final_answer'][:80]}...")
        print(f"  LLM Confidence: {sample.get('llm_confidence', 0):.1f}%")
        print()

    print("\n" + "=" * 80)
    print("STEP 2: CALCULATE CONSISTENCY")
    print("=" * 80)
    print(f"Summary: {response.get('reasoning_summary', 'N/A')}")
    print(f"\nLLM Confidence: {response.get('llm_confidence', 0):.1f}%")
    print(f"Agreement Confidence: {response.get('agreement_confidence', 0):.1f}%")
    print(f"\nPreliminary Answer (most consistent across samples):")
    print(f"  {response.get('preliminary_answer', 'N/A')}")

    print("\n" + "=" * 80)
    print("STEP 3: REFLECTION AT THE END")
    print("=" * 80)
    print(f"Reflection analyzes all reasoning paths to produce refined final answer:")
    print(f"\nReflection Reasoning:")
    print(f"  {response.get('reflection_reasoning', 'N/A')}")
    print(f"\nReflection Confidence: {response.get('reflection_confidence', 0):.1f}%")

    print("\n" + "=" * 80)
    print("FINAL RESULT")
    print("=" * 80)
    print(f"Overall Confidence Score: {response.get('confidence_score', 0):.2%}")
    print(f"\nFinal Answer (refined by reflection):")
    print(f"{response.get('final_answer', 'N/A')}")

    print("\n" + "=" * 80)
    print("TOKEN USAGE & COST ANALYSIS")
    print("=" * 80)
    token_usage = response.get('token_usage', {})
    cost_analysis = response.get('cost_analysis', {})

    print(f"Prompt Tokens: {token_usage.get('prompt_tokens', 0):,}")
    print(f"Completion Tokens: {token_usage.get('completion_tokens', 0):,}")
    print(f"Total Tokens: {token_usage.get('total_tokens', 0):,}")

    print(f"\nCost ({cost_analysis.get('pricing_model', 'N/A')}):")
    print(f"  Input: ${cost_analysis.get('input_cost', 0):.8f} (${cost_analysis.get('input_price_per_1m', 0)}/1M tokens)")
    print(f"  Output: ${cost_analysis.get('output_cost', 0):.8f} (${cost_analysis.get('output_price_per_1m', 0)}/1M tokens)")
    print(f"  Total: ${cost_analysis.get('total_cost', 0):.8f} {cost_analysis.get('currency', 'USD')}")

    timing = response.get('timing', {})
    print(f"\nTotal Processing Time: {timing.get('total_time', 0):.3f} seconds")

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
    print("\n\nExample 1: Train speed calculation")
    print("-" * 80)
    try:
        response = client.completions(
            prompt="If a train travels 60 kilometers in 1 hour, how far will it travel in 2.5 hours?",
            num_self_consistency=3,
            num_cot=1,
            model="fast",
            temperature=0.7
        )
        print_response(response)
    except Exception as e:
        print(f"Error: {e}")

    # Example 2: Logical reasoning
    print("\n\nExample 2: Logical reasoning")
    print("-" * 80)
    try:
        response = client.completions(
            prompt="Imagine an infinitely wide entrance, which is more likely to pass through it, a military tank or a car?",
            num_self_consistency=1,
            num_cot=1,
            model="fast",
            temperature=0.8
        )
        print_response(response)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
