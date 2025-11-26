from cot_engine import ChainOfThoughtEngine
from models import SelfConsistencySample, ChainOfThoughtStep
from typing import List, Tuple
from collections import Counter
from langchain.schema import HumanMessage, SystemMessage
import re
import asyncio
import json
import time


class SelfConsistencyEngine:
    """
    Engine for implementing self-consistency reasoning.
    Generates multiple reasoning paths and selects the most consistent answer.
    """

    def __init__(self, model_name: str, temperature: float = 0.9):
        """
        Initialize the self-consistency engine

        Args:
            model_name: Name of the LLM model to use
            temperature: Higher temperature for diverse reasoning paths
        """
        self.cot_engine = ChainOfThoughtEngine(model_name, temperature)

    async def _generate_single_sample_async(
        self,
        sample_num: int,
        prompt: str,
        num_cot_steps: int,
        system_prompt: str = None
    ) -> tuple[SelfConsistencySample, dict]:
        """
        Generate a single sample asynchronously

        Args:
            sample_num: Sample number
            prompt: User's input prompt
            num_cot_steps: Number of CoT steps per path
            system_prompt: Optional system prompt to provide context and instructions

        Returns:
            Tuple of (SelfConsistencySample object, token_usage dict)
        """
        # Generate chain-of-thought steps for this sample
        cot_steps, cot_tokens = await self.cot_engine.agenerate_cot_steps(prompt, num_cot_steps, system_prompt)

        # Generate final answer and confidence based on these steps
        final_answer, llm_confidence, answer_tokens = await self.cot_engine.agenerate_final_answer(prompt, cot_steps, system_prompt)

        # Aggregate tokens for this sample
        sample_tokens = {
            "prompt_tokens": cot_tokens["prompt_tokens"] + answer_tokens["prompt_tokens"],
            "completion_tokens": cot_tokens["completion_tokens"] + answer_tokens["completion_tokens"],
            "total_tokens": cot_tokens["total_tokens"] + answer_tokens["total_tokens"]
        }

        sample = SelfConsistencySample(
            sample_number=sample_num,
            reasoning_path=cot_steps,
            final_answer=final_answer,
            llm_confidence=llm_confidence
        )
        return sample, sample_tokens

    async def generate_multiple_paths_async(
        self,
        prompt: str,
        num_samples: int,
        num_cot_steps: int,
        system_prompt: str = None
    ) -> tuple[List[SelfConsistencySample], dict]:
        """
        Generate multiple independent reasoning paths IN PARALLEL

        Args:
            prompt: User's input prompt
            num_samples: Number of independent reasoning paths to generate
            num_cot_steps: Number of CoT steps per path
            system_prompt: Optional system prompt to provide context and instructions

        Returns:
            Tuple of (List of SelfConsistencySample objects, aggregated token_usage dict)
        """
        # Create tasks for all samples to run in parallel
        tasks = [
            self._generate_single_sample_async(sample_num, prompt, num_cot_steps, system_prompt)
            for sample_num in range(1, num_samples + 1)
        ]

        # Run all samples in parallel
        results = await asyncio.gather(*tasks)

        # Separate samples and token usage
        samples = [result[0] for result in results]

        # Aggregate tokens from all samples
        total_tokens = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        for result in results:
            sample_tokens = result[1]
            total_tokens["prompt_tokens"] += sample_tokens["prompt_tokens"]
            total_tokens["completion_tokens"] += sample_tokens["completion_tokens"]
            total_tokens["total_tokens"] += sample_tokens["total_tokens"]

        return samples, total_tokens

    def extract_key_answer(self, answer: str) -> str:
        """
        Extract the core answer from a potentially verbose response

        Args:
            answer: The full answer text

        Returns:
            Normalized key answer
        """
        # Remove extra whitespace
        answer = " ".join(answer.split())

        # Try to extract the most important sentence or phrase
        # Look for common answer patterns
        sentences = [s.strip() for s in answer.split('.') if s.strip()]

        if not sentences:
            return answer.lower().strip()

        # Use the first substantive sentence
        key_answer = sentences[0]

        # Normalize
        key_answer = key_answer.lower().strip()

        return key_answer

    def calculate_consistency(
        self,
        samples: List[SelfConsistencySample]
    ) -> Tuple[str, float, float, float, str]:
        """
        Calculate the most consistent answer from multiple samples using weighted hybrid approach

        Args:
            samples: List of self-consistency samples

        Returns:
            Tuple of (most_consistent_answer, weighted_confidence, llm_confidence, agreement_confidence, summary)
        """
        if not samples:
            return "", 0.0, 0.0, 0.0, "No samples generated"

        # Extract and normalize answers
        answers = [self.extract_key_answer(s.final_answer) for s in samples]

        # Count occurrences
        answer_counts = Counter(answers)

        # Find most common answer
        most_common_answer, count = answer_counts.most_common(1)[0]

        # Calculate agreement-based confidence (proportion of samples agreeing)
        agreement_confidence = (count / len(samples)) * 100.0  # 0-100 scale for display

        # Calculate average LLM confidence from samples that gave the most common answer
        llm_confidences = [
            s.llm_confidence for s in samples
            if self.extract_key_answer(s.final_answer) == most_common_answer
        ]
        avg_llm_confidence = sum(llm_confidences) / len(llm_confidences) if llm_confidences else 50.0

        # Use LLM confidence as primary confidence score (convert to 0-1 scale)
        primary_confidence = avg_llm_confidence / 100.0

        # Find the full answer corresponding to the most common key answer
        for sample in samples:
            if self.extract_key_answer(sample.final_answer) == most_common_answer:
                final_answer = sample.final_answer
                break
        else:
            final_answer = most_common_answer

        # Create summary
        summary = self._create_consistency_summary(
            samples, answer_counts, avg_llm_confidence, agreement_confidence
        )

        return final_answer, primary_confidence, avg_llm_confidence, agreement_confidence, summary

    def _create_consistency_summary(
        self,
        samples: List[SelfConsistencySample],
        answer_counts: Counter,
        llm_confidence: float,
        agreement_confidence: float
    ) -> str:
        """Create a summary of the self-consistency analysis"""

        summary_parts = [
            f"Generated {len(samples)} independent reasoning paths.",
            f"LLM confidence: {llm_confidence:.1f}% (Agreement: {agreement_confidence:.1f}%)",
        ]

        if len(answer_counts) > 1:
            summary_parts.append(
                f"Found {len(answer_counts)} distinct answer patterns."
            )
        else:
            summary_parts.append("All reasoning paths converged to the same answer.")

        return " ".join(summary_parts)

    def reflection_call(
        self,
        prompt: str,
        samples: List[SelfConsistencySample],
        preliminary_answer: str,
        system_prompt: str = None
    ) -> Tuple[str, str, float, dict]:
        """
        Make a final reflection call with all reasoning paths and answers

        Args:
            prompt: Original user prompt
            samples: All self-consistency samples with CoT reasoning
            preliminary_answer: The preliminary answer from self-consistency
            system_prompt: Optional system prompt to provide context and instructions

        Returns:
            Tuple of (refined_answer, reflection_reasoning, reflection_confidence, token_usage)
        """
        print(f"  Inside reflection_call with {len(samples)} samples")

        # Build summary of all reasoning paths
        reasoning_summary = []
        for sample in samples:
            reasoning_summary.append(f"\n=== Reasoning Path {sample.sample_number} ===")
            for step in sample.reasoning_path:
                reasoning_summary.append(f"Step {step.step_number}: {step.reasoning}")
                reasoning_summary.append(f"Conclusion: {step.intermediate_conclusion}")
            reasoning_summary.append(f"Final Answer: {sample.final_answer}")
            reasoning_summary.append(f"Confidence: {sample.llm_confidence}%\n")

        reasoning_text = "\n".join(reasoning_summary)

        # Create reflection prompt with optional system context
        if system_prompt:
            reflection_prompt = """You are analyzing multiple reasoning paths to produce a refined final answer.

SYSTEM CONTEXT:
{system_prompt}

ORIGINAL QUESTION:
{prompt}

ALL REASONING PATHS:
{reasoning_text}

PRELIMINARY ANSWER (most consistent):
{preliminary_answer}

Based on all the reasoning paths above, provide:
1. A refined final answer that incorporates the best insights from all paths
2. Your reasoning for the refined answer
3. Your confidence level (0-100)

Return ONLY a JSON object in this exact format:
{{"refined_answer": "your final answer", "reflection_reasoning": "your analysis", "confidence": 85}}"""
        else:
            reflection_prompt = """You are analyzing multiple reasoning paths to produce a refined final answer.

ORIGINAL QUESTION:
{prompt}

ALL REASONING PATHS:
{reasoning_text}

PRELIMINARY ANSWER (most consistent):
{preliminary_answer}

Based on all the reasoning paths above, provide:
1. A refined final answer that incorporates the best insights from all paths
2. Your reasoning for the refined answer
3. Your confidence level (0-100)

Return ONLY a JSON object in this exact format:
{{"refined_answer": "your final answer", "reflection_reasoning": "your analysis", "confidence": 85}}"""

        messages = [
            SystemMessage(content="You are an expert at synthesizing multiple reasoning paths into a refined answer."),
            HumanMessage(content=reflection_prompt)
        ]

        print(f"  Calling LLM for reflection...")
        response = self.cot_engine.llm.invoke(messages)
        print(f"  LLM response received, length: {len(response.content)}")
        content = response.content.strip()
        print(f"  Raw content preview: {content[:200]}")

        # Track token usage
        token_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        if hasattr(response, 'usage_metadata') and response.usage_metadata:
            token_usage["prompt_tokens"] = response.usage_metadata.get("input_tokens", 0)
            token_usage["completion_tokens"] = response.usage_metadata.get("output_tokens", 0)
            token_usage["total_tokens"] = response.usage_metadata.get("total_tokens", 0)
        elif hasattr(response, 'response_metadata') and 'token_usage' in response.response_metadata:
            usage = response.response_metadata['token_usage']
            token_usage["prompt_tokens"] = usage.get("prompt_tokens", 0)
            token_usage["completion_tokens"] = usage.get("completion_tokens", 0)
            token_usage["total_tokens"] = usage.get("total_tokens", 0)

        # Parse response
        try:
            # Extract JSON if wrapped in code blocks
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()
            elif "```" in content:
                json_start = content.find("```") + 3
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()

            parsed = json.loads(content)
            refined_answer = parsed.get("refined_answer", preliminary_answer)
            reflection_reasoning = parsed.get("reflection_reasoning", "Reflection completed")
            confidence = float(parsed.get("confidence", 50.0))
            confidence = max(0.0, min(100.0, confidence))

            return refined_answer, reflection_reasoning, confidence, token_usage

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            # Fallback: use preliminary answer
            print(f"Reflection JSON parsing failed: {str(e)}")
            print(f"Raw content: {content[:200]}")
            return preliminary_answer, "Reflection parsing failed, using preliminary answer", 50.0, token_usage

    def run_self_consistency(
        self,
        prompt: str,
        num_samples: int,
        num_cot_steps: int,
        system_prompt: str = None
    ) -> Tuple[List[SelfConsistencySample], str, str, str, float, float, float, float, str, dict, dict]:
        """
        Run complete self-consistency pipeline WITH PARALLEL EXECUTION and REFLECTION

        Args:
            prompt: User's input prompt
            num_samples: Number of reasoning paths
            num_cot_steps: Number of CoT steps per path
            system_prompt: Optional system prompt to provide context and instructions

        Returns:
            Tuple of (samples, preliminary_answer, final_answer, reflection_reasoning,
                     weighted_confidence, llm_confidence, agreement_confidence, reflection_confidence, summary, token_usage, timing)
        """
        start_time = time.time()

        # Generate multiple reasoning paths IN PARALLEL
        try:
            # Try to get existing event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, create a new one in a thread (shouldn't happen in Flask)
                import nest_asyncio
                nest_asyncio.apply()
                samples, samples_tokens = loop.run_until_complete(
                    self.generate_multiple_paths_async(prompt, num_samples, num_cot_steps, system_prompt)
                )
            else:
                samples, samples_tokens = loop.run_until_complete(
                    self.generate_multiple_paths_async(prompt, num_samples, num_cot_steps, system_prompt)
                )
        except RuntimeError:
            # No event loop exists, create one
            samples, samples_tokens = asyncio.run(
                self.generate_multiple_paths_async(prompt, num_samples, num_cot_steps, system_prompt)
            )

        # Calculate most consistent answer with weighted hybrid confidence
        preliminary_answer, weighted_confidence, llm_confidence, agreement_confidence, summary = self.calculate_consistency(samples)

        # Perform reflection call to get refined final answer
        print(f"\n=== STARTING REFLECTION CALL ===")
        print(f"Preliminary answer: {preliminary_answer[:100]}...")
        try:
            final_answer, reflection_reasoning, reflection_confidence, reflection_tokens = self.reflection_call(
                prompt, samples, preliminary_answer, system_prompt
            )
            print(f"=== REFLECTION COMPLETED ===")
            print(f"Final answer: {final_answer[:100]}...")
            print(f"Reflection confidence: {reflection_confidence}%")
        except Exception as e:
            # Fallback if reflection fails completely
            print(f"!!! Reflection call failed: {str(e)}")
            import traceback
            traceback.print_exc()
            final_answer = preliminary_answer
            reflection_reasoning = f"Reflection failed: {str(e)}"
            reflection_confidence = 50.0
            reflection_tokens = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

        # Calculate total time
        total_time = time.time() - start_time

        # Aggregate all tokens
        total_token_usage = {
            "prompt_tokens": samples_tokens["prompt_tokens"] + reflection_tokens["prompt_tokens"],
            "completion_tokens": samples_tokens["completion_tokens"] + reflection_tokens["completion_tokens"],
            "total_tokens": samples_tokens["total_tokens"] + reflection_tokens["total_tokens"]
        }

        # Create timing
        timing = {
            "total_time": round(total_time, 3),
            "unit": "seconds"
        }

        return (samples, preliminary_answer, final_answer, reflection_reasoning,
                weighted_confidence, llm_confidence, agreement_confidence, reflection_confidence, summary, total_token_usage, timing)
