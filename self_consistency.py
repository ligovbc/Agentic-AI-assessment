from cot_engine import ChainOfThoughtEngine
from models import SelfConsistencySample, ChainOfThoughtStep
from typing import List, Tuple
from collections import Counter
import re
import asyncio


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

    def generate_multiple_paths(
        self,
        prompt: str,
        num_samples: int,
        num_cot_steps: int
    ) -> List[SelfConsistencySample]:
        """
        Generate multiple independent reasoning paths

        Args:
            prompt: User's input prompt
            num_samples: Number of independent reasoning paths to generate
            num_cot_steps: Number of CoT steps per path

        Returns:
            List of SelfConsistencySample objects
        """
        samples = []

        for sample_num in range(1, num_samples + 1):
            # Generate chain-of-thought steps for this sample
            cot_steps = self.cot_engine.generate_cot_steps(prompt, num_cot_steps)

            # Generate final answer and confidence based on these steps
            final_answer, llm_confidence = self.cot_engine.generate_final_answer(prompt, cot_steps)

            sample = SelfConsistencySample(
                sample_number=sample_num,
                reasoning_path=cot_steps,
                final_answer=final_answer,
                llm_confidence=llm_confidence
            )
            samples.append(sample)

        return samples

    async def _generate_single_sample_async(
        self,
        sample_num: int,
        prompt: str,
        num_cot_steps: int
    ) -> SelfConsistencySample:
        """
        Generate a single sample asynchronously

        Args:
            sample_num: Sample number
            prompt: User's input prompt
            num_cot_steps: Number of CoT steps per path

        Returns:
            SelfConsistencySample object
        """
        # Generate chain-of-thought steps for this sample
        cot_steps = await self.cot_engine.agenerate_cot_steps(prompt, num_cot_steps)

        # Generate final answer and confidence based on these steps
        final_answer, llm_confidence = await self.cot_engine.agenerate_final_answer(prompt, cot_steps)

        sample = SelfConsistencySample(
            sample_number=sample_num,
            reasoning_path=cot_steps,
            final_answer=final_answer,
            llm_confidence=llm_confidence
        )
        return sample

    async def generate_multiple_paths_async(
        self,
        prompt: str,
        num_samples: int,
        num_cot_steps: int
    ) -> List[SelfConsistencySample]:
        """
        Generate multiple independent reasoning paths IN PARALLEL

        Args:
            prompt: User's input prompt
            num_samples: Number of independent reasoning paths to generate
            num_cot_steps: Number of CoT steps per path

        Returns:
            List of SelfConsistencySample objects
        """
        # Create tasks for all samples to run in parallel
        tasks = [
            self._generate_single_sample_async(sample_num, prompt, num_cot_steps)
            for sample_num in range(1, num_samples + 1)
        ]

        # Run all samples in parallel
        samples = await asyncio.gather(*tasks)

        return list(samples)

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
            samples, answer_counts, primary_confidence, avg_llm_confidence, agreement_confidence
        )

        return final_answer, primary_confidence, avg_llm_confidence, agreement_confidence, summary

    def _create_consistency_summary(
        self,
        samples: List[SelfConsistencySample],
        answer_counts: Counter,
        primary_confidence: float,
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

    def run_self_consistency(
        self,
        prompt: str,
        num_samples: int,
        num_cot_steps: int
    ) -> Tuple[List[SelfConsistencySample], str, float, float, float, str]:
        """
        Run complete self-consistency pipeline WITH PARALLEL EXECUTION

        Args:
            prompt: User's input prompt
            num_samples: Number of reasoning paths
            num_cot_steps: Number of CoT steps per path

        Returns:
            Tuple of (samples, final_answer, weighted_confidence, llm_confidence, agreement_confidence, summary)
        """
        # Generate multiple reasoning paths IN PARALLEL
        try:
            # Try to get existing event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, create a new one in a thread (shouldn't happen in Flask)
                import nest_asyncio
                nest_asyncio.apply()
                samples = loop.run_until_complete(
                    self.generate_multiple_paths_async(prompt, num_samples, num_cot_steps)
                )
            else:
                samples = loop.run_until_complete(
                    self.generate_multiple_paths_async(prompt, num_samples, num_cot_steps)
                )
        except RuntimeError:
            # No event loop exists, create one
            samples = asyncio.run(
                self.generate_multiple_paths_async(prompt, num_samples, num_cot_steps)
            )

        # Calculate most consistent answer with weighted hybrid confidence
        final_answer, weighted_confidence, llm_confidence, agreement_confidence, summary = self.calculate_consistency(samples)

        return samples, final_answer, weighted_confidence, llm_confidence, agreement_confidence, summary
