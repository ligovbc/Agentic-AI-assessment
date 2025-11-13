from pydantic import BaseModel, Field, validator
from typing import Optional, Literal


class AgenticRequest(BaseModel):
    """Request model for the agentic AI API"""

    prompt: str = Field(..., description="The input prompt for the AI")
    num_self_consistency: int = Field(
        default=3,
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
    final_answer: str
    confidence_score: float = Field(
        description="LLM self-assessed confidence (0-1 scale) - averaged from samples with most common answer"
    )
    llm_confidence: float = Field(
        default=0.0,
        description="Average LLM self-assessed confidence (0-100 scale) - same as confidence_score but on 0-100 scale"
    )
    agreement_confidence: float = Field(
        default=0.0,
        description="Self-consistency agreement percentage (0-100 scale) - how many samples agreed"
    )
    reasoning_summary: str
