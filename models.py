from pydantic import BaseModel, Field, validator
from typing import Optional, Literal


class AgenticRequest(BaseModel):
    """Request model for the agentic AI API"""

    prompt: str = Field(..., description="The user's question or input prompt")
    system_prompt: Optional[str] = Field(
        default=None,
        description="System prompt to guide the AI's behavior and context"
    )
    num_self_consistency: int = Field(
        default=1,
        ge=1,
        le=15,
        description="Number of self-consistency samples to generate"
    )
    num_cot: int = Field(
        default=1,
        ge=1,
        le=10,
        description="Number of chain-of-thought reasoning steps"
    )
    model: Literal["fast", "slow"] = Field(
        default="fast",
        description="Model speed: 'fast' for GPT-3.5, 'slow' for GPT-4"
    )
    temperature: Optional[float] = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Temperature for response generation"
    )


class ChainOfThoughtStep(BaseModel):
    """Individual step in chain-of-thought reasoning"""

    step_number: int
    reasoning: str
    intermediate_conclusion: str


class SelfConsistencySample(BaseModel):
    """Individual sample from self-consistency generation"""

    sample_number: int
    reasoning_path: list[ChainOfThoughtStep]
    final_answer: str
    llm_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="LLM's self-assessed confidence (0-100)"
    )


class AgenticResponse(BaseModel):
    """Response model for the agentic AI API"""

    prompt: str
    model_used: str
    chain_of_thought: list[ChainOfThoughtStep]
    self_consistency_samples: list[SelfConsistencySample]
    preliminary_answer: str = Field(
        description="The preliminary answer from self-consistency before reflection"
    )
    final_answer: str = Field(
        description="The final refined answer after reflection"
    )
    confidence_score: float = Field(
        description="Final confidence score (0-1 scale) - from reflection analysis of all reasoning paths"
    )
    llm_confidence: float = Field(
        default=0.0,
        description="Average LLM self-assessed confidence (0-100 scale) - from self-consistency samples"
    )
    agreement_confidence: float = Field(
        default=0.0,
        description="Self-consistency agreement percentage (0-100 scale) - how many samples agreed"
    )
    reflection_reasoning: str = Field(
        default="",
        description="The reasoning from the reflection step analyzing all paths"
    )
    reflection_confidence: float = Field(
        default=0.0,
        description="Reflection confidence in the refined answer (0-100 scale)"
    )
    reasoning_summary: str
    token_usage: dict = Field(
        default_factory=dict,
        description="Total token usage breakdown (prompt_tokens, completion_tokens, total_tokens)"
    )
    cost_analysis: dict = Field(
        default_factory=dict,
        description="Cost breakdown (input_cost, output_cost, total_cost, currency, pricing_model)"
    )
    timing: dict = Field(
        default_factory=dict,
        description="Timing information (total_time in seconds)"
    )
