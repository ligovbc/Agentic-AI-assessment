from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from models import ChainOfThoughtStep
from config import Config
from typing import List
import json
import asyncio


class ChainOfThoughtEngine:
    """Engine for generating chain-of-thought reasoning using LangChain"""

    def __init__(self, model_name: str, temperature: float = 0.7):
        # Choose between Azure OpenAI and regular OpenAI
        if Config.OPENAI_PROVIDER == "azure":
            self.llm = AzureChatOpenAI(
                azure_deployment=model_name,
                api_version=Config.AZURE_OPENAI_API_VERSION,
                azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
                api_key=Config.AZURE_OPENAI_API_KEY,
                temperature=temperature
            )
        else:
            self.llm = ChatOpenAI(
                model=model_name,
                temperature=temperature,
                api_key=Config.OPENAI_API_KEY
            )
        self.step_prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an expert reasoning assistant. Break down complex problems
            into clear, logical steps. For each step, provide:
            1. The reasoning for this step
            2. An intermediate conclusion

            Return your response as JSON with keys: 'reasoning' and 'intermediate_conclusion'"""),
            ("human", "{instruction}")
        ])

    async def agenerate_cot_steps(self, prompt: str, num_steps: int) -> tuple[List[ChainOfThoughtStep], dict]:
        """
        Generate chain-of-thought reasoning steps for a given prompt

        Args:
            prompt: The user's input prompt
            num_steps: Number of reasoning steps to generate

        Returns:
            Tuple of (List of ChainOfThoughtStep objects, token_usage dict)
        """
        steps = []
        context = f"Original question: {prompt}\n\n"
        total_tokens = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

        for step_num in range(1, num_steps + 1):
            # Build instruction for this step
            if step_num == 1:
                instruction = f"{context}Generate step {step_num} of {num_steps} reasoning steps. What is the first thing we need to consider or break down?"
            elif step_num == num_steps:
                previous_steps = "\n".join([
                    f"Step {s.step_number}: {s.reasoning} → {s.intermediate_conclusion}"
                    for s in steps
                ])
                instruction = f"{context}Previous steps:\n{previous_steps}\n\nGenerate the final step {step_num} of {num_steps}. Synthesize the previous steps and provide a conclusive reasoning."
            else:
                previous_steps = "\n".join([
                    f"Step {s.step_number}: {s.reasoning} → {s.intermediate_conclusion}"
                    for s in steps
                ])
                instruction = f"{context}Previous steps:\n{previous_steps}\n\nGenerate step {step_num} of {num_steps}. Build upon the previous reasoning."

            # Generate step
            try:
                messages = self.step_prompt_template.format_messages(instruction=instruction)
                response = await self.llm.ainvoke(messages)

                # Track token usage
                if hasattr(response, 'usage_metadata') and response.usage_metadata:
                    total_tokens["prompt_tokens"] += response.usage_metadata.get("input_tokens", 0)
                    total_tokens["completion_tokens"] += response.usage_metadata.get("output_tokens", 0)
                    total_tokens["total_tokens"] += response.usage_metadata.get("total_tokens", 0)
                elif hasattr(response, 'response_metadata') and 'token_usage' in response.response_metadata:
                    usage = response.response_metadata['token_usage']
                    total_tokens["prompt_tokens"] += usage.get("prompt_tokens", 0)
                    total_tokens["completion_tokens"] += usage.get("completion_tokens", 0)
                    total_tokens["total_tokens"] += usage.get("total_tokens", 0)

                # Parse response
                content = response.content.strip()

                # Try to extract JSON if present
                if "```json" in content:
                    json_start = content.find("```json") + 7
                    json_end = content.find("```", json_start)
                    content = content[json_start:json_end].strip()
                elif "```" in content:
                    json_start = content.find("```") + 3
                    json_end = content.find("```", json_start)
                    content = content[json_start:json_end].strip()

                try:
                    parsed = json.loads(content)
                    reasoning = parsed.get("reasoning", content)
                    conclusion = parsed.get("intermediate_conclusion", "")
                except json.JSONDecodeError:
                    # Fallback: split content
                    parts = content.split("\n", 1)
                    reasoning = parts[0] if parts else content
                    conclusion = parts[1] if len(parts) > 1 else reasoning

                step = ChainOfThoughtStep(
                    step_number=step_num,
                    reasoning=reasoning,
                    intermediate_conclusion=conclusion
                )
                steps.append(step)

            except Exception as e:
                # Fallback step on error
                step = ChainOfThoughtStep(
                    step_number=step_num,
                    reasoning=f"Error in step generation: {str(e)}",
                    intermediate_conclusion="Unable to generate conclusion for this step"
                )
                steps.append(step)

        return steps, total_tokens

    async def agenerate_final_answer(self, prompt: str, cot_steps: List[ChainOfThoughtStep]) -> tuple[str, float, dict]:
        """
        Generate final answer based on chain-of-thought steps

        Args:
            prompt: Original user prompt
            cot_steps: List of reasoning steps

        Returns:
            Tuple of (final_answer, confidence_score, token_usage)
        """
        steps_summary = "\n".join([
            f"Step {s.step_number}: {s.reasoning}\nConclusion: {s.intermediate_conclusion}"
            for s in cot_steps
        ])

        final_prompt = f"""Original question: {prompt}

Reasoning steps:
{steps_summary}

Based on the above chain of reasoning, provide:
1. A clear, concise final answer to the original question
2. Your confidence level (0-100) considering:
   - Strength and validity of your reasoning
   - Certainty in your conclusion
   - Any ambiguities, assumptions, or limitations

Return ONLY a JSON object in this exact format:
{{"answer": "your final answer here", "confidence": 85}}"""

        messages = [
            SystemMessage(content="You are a helpful assistant that synthesizes reasoning steps into clear answers with confidence scores."),
            HumanMessage(content=final_prompt)
        ]

        response = await self.llm.ainvoke(messages)
        content = response.content.strip()

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

        # Try to parse JSON response
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
            answer = parsed.get("answer", content)
            confidence = float(parsed.get("confidence", 50.0))

            # Ensure confidence is in valid range
            confidence = max(0.0, min(100.0, confidence))

            return answer, confidence, token_usage

        except (json.JSONDecodeError, ValueError, KeyError):
            # Fallback: use content as answer, default confidence
            return content, 50.0, token_usage
