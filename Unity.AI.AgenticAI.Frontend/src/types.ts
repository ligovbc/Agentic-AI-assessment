// API Types for Agentic AI Backend

export interface ChainOfThoughtStep {
  step_number: number;
  reasoning: string;
}

export interface SelfConsistencySample {
  sample_number: number;
  reasoning_path: ChainOfThoughtStep[];
  final_answer: string;
  llm_confidence: number;
}

export interface TokenUsage {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
}

export interface CostAnalysis {
  input_cost: number;
  output_cost: number;
  total_cost: number;
  currency: string;
  pricing_model: string;
  input_price_per_1m: number;
  output_price_per_1m: number;
}

export interface Timing {
  total_time: number;
  samples_time?: number;
  reflection_time?: number;
}

export interface PDFInfo {
  num_pages: number;
  error?: string;
}

export interface AgenticResponse {
  prompt: string;
  model_used: string;
  chain_of_thought: ChainOfThoughtStep[];
  self_consistency_samples: SelfConsistencySample[];
  preliminary_answer: string;
  final_answer: string;
  confidence_score: number;
  llm_confidence: number;
  agreement_confidence: number;
  reflection_reasoning: string;
  reflection_confidence: number;
  reasoning_summary: string;
  token_usage: TokenUsage;
  cost_analysis: CostAnalysis;
  timing: Timing;
  pdf_info?: PDFInfo;
}

export interface AgenticRequest {
  prompt: string;
  system_prompt?: string;
  num_self_consistency: number;
  num_cot: number;
  model: 'fast' | 'slow';
  temperature: number;
}
