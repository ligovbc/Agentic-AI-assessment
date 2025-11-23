import { useState, type ChangeEvent, type FormEvent } from 'react';
import './App.css';
import { Header } from './components/Header';
import { agenticAPI } from './services/api';
import type { AgenticRequest, AgenticResponse } from './types';
import { Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

function App() {
  const [formData, setFormData] = useState<AgenticRequest>({
    prompt: 'If a train travels 60 kilometers in 1 hour, how far will it travel in 2.5 hours?',
    system_prompt: '',
    num_self_consistency: 3,
    num_cot: 2,
    model: 'fast',
    temperature: 0.7,
  });
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<AgenticResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: ['num_self_consistency', 'num_cot'].includes(name)
        ? parseInt(value)
        : name === 'temperature'
        ? parseFloat(value)
        : value
    }));
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setPdfFile(e.target.files[0]);
    }
  };

  const handleRemovePdf = () => {
    setPdfFile(null);
    // Reset the file input
    const fileInput = document.getElementById('pdfFile') as HTMLInputElement;
    if (fileInput) {
      fileInput.value = '';
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      let result: AgenticResponse;
      if (pdfFile) {
        result = await agenticAPI.submitCompletionWithPDF(formData, pdfFile);
      } else {
        result = await agenticAPI.submitCompletion(formData);
      }
      setResponse(result);
    } catch (err: any) {
      setError(err.response?.data?.message || err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const COLORS = ['#003366', '#38598a', '#fcba19', '#2e8540'];

  return (
    <>
      <a href="#main-content" className="skip-to-main">Skip to main content</a>
      <Header />

      <div className="container">
        <main id="main-content">
          {/* Input Form */}
          <div className="card">
            <form onSubmit={handleSubmit}>
              <div className="input-group">
                <label htmlFor="prompt">Prompt / Question</label>
                <textarea
                  id="prompt"
                  name="prompt"
                  value={formData.prompt}
                  onChange={handleInputChange}
                  placeholder="Enter your question or prompt here..."
                  rows={4}
                  required
                  aria-required="true"
                />
              </div>

              <div className="input-group">
                <label htmlFor="system_prompt" style={{ fontSize: '0.9em' }}>System Prompt (Optional)</label>
                <input
                  type="text"
                  id="system_prompt"
                  name="system_prompt"
                  value={formData.system_prompt}
                  onChange={handleInputChange}
                  placeholder="e.g., 'You are a helpful assistant...'"
                  style={{ fontSize: '0.9em' }}
                />
              </div>

              <div className="input-group">
                <label htmlFor="pdfFile">Upload PDF (Optional)</label>
                <input
                  type="file"
                  id="pdfFile"
                  accept=".pdf"
                  onChange={handleFileChange}
                  aria-describedby="pdf-help"
                />
                {pdfFile && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '8px', padding: '8px', backgroundColor: '#f5f5f5', borderRadius: '4px' }}>
                    <span style={{ flex: 1, fontSize: '0.9em' }}>📄 {pdfFile.name}</span>
                    <button
                      type="button"
                      onClick={handleRemovePdf}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: '#d32f2f',
                        cursor: 'pointer',
                        fontSize: '1.2em',
                        padding: '0 8px',
                        fontWeight: 'bold',
                        lineHeight: '1'
                      }}
                      aria-label="Remove PDF"
                      title="Remove PDF"
                    >
                      ✕
                    </button>
                  </div>
                )}
                <small id="pdf-help">Upload a PDF document to analyze its content</small>
              </div>

              <div className="parameters-grid">
                <div className="input-group">
                  <label htmlFor="num_self_consistency">
                    Self-Consistency Samples
                  </label>
                  <input
                    type="number"
                    id="num_self_consistency"
                    name="num_self_consistency"
                    min="1"
                    max="10"
                    value={formData.num_self_consistency}
                    onChange={handleInputChange}
                  />
                </div>

                <div className="input-group">
                  <label htmlFor="num_cot">Chain-of-Thought Steps</label>
                  <input
                    type="number"
                    id="num_cot"
                    name="num_cot"
                    min="1"
                    max="5"
                    value={formData.num_cot}
                    onChange={handleInputChange}
                  />
                </div>

                <div className="input-group">
                  <label htmlFor="model">Model Speed</label>
                  <select
                    id="model"
                    name="model"
                    value={formData.model}
                    onChange={handleInputChange}
                  >
                    <option value="fast">Fast (GPT-4o-mini)</option>
                    <option value="slow">Slow (GPT-4o)</option>
                  </select>
                </div>

                <div className="input-group">
                  <label htmlFor="temperature">Temperature ({formData.temperature})</label>
                  <input
                    type="range"
                    id="temperature"
                    name="temperature"
                    min="0"
                    max="2"
                    step="0.1"
                    value={formData.temperature}
                    onChange={handleInputChange}
                  />
                  <output htmlFor="temperature">{formData.temperature}</output>
                </div>
              </div>

              <button
                type="submit"
                className="btn-primary"
                disabled={loading}
                aria-busy={loading}
              >
                {loading ? (
                  <>
                    <span className="spinner"></span>
                    <span>Processing...</span>
                  </>
                ) : (
                  <span>Run Analysis</span>
                )}
              </button>
            </form>

            {error && (
              <div className="alert alert-error" role="alert">
                <strong>Error:</strong> {error}
              </div>
            )}
          </div>

          {/* Results Section */}
          {response && (
            <>
              {/* Overview Card */}
              <div className="card">
                <h2>Results Overview</h2>

                {response.pdf_info && (
                  <div className="pdf-info" role="status">
                    <strong>PDF Processed:</strong> {response.pdf_info.num_pages} pages
                    {response.pdf_info.error && <div>Warning: {response.pdf_info.error}</div>}
                  </div>
                )}

                <div className="stats-grid">
                  <div className="stat-card">
                    <div className="stat-label">LLM Confidence</div>
                    <div className="stat-value">{response.llm_confidence.toFixed(1)}%</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-label">Processing Time</div>
                    <div className="stat-value">{response.timing.total_time.toFixed(2)}s</div>
                  </div>
                </div>
              </div>

              {/* Final Answer */}
              <div className="card">
                <h2>Final Answer</h2>
                <div className="answer-box">{response.final_answer}</div>

                <h3>Reflection Reasoning</h3>
                <div className="reflection-box">{response.reflection_reasoning}</div>
              </div>

              {/* Self-Consistency Samples */}
              <div className="card">
                <h2>Self-Consistency Analysis</h2>
                <div className="summary-box">{response.reasoning_summary}</div>

                {response.self_consistency_samples.map((sample) => (
                  <div key={sample.sample_number} className="sample">
                    <div className="sample-header">
                      <span className="sample-title">Sample {sample.sample_number}</span>
                      <span className="confidence-badge">
                        {sample.llm_confidence.toFixed(1)}% Confidence
                      </span>
                    </div>

                    <div className="cot-steps">
                      <strong>Chain-of-Thought Steps:</strong>
                      {sample.reasoning_path.map((step) => (
                        <div key={step.step_number} className="cot-step">
                          <div className="step-number">Step {step.step_number}</div>
                          <div>{step.reasoning}</div>
                        </div>
                      ))}
                    </div>

                    <div className="sample-answer">
                      <strong>Answer:</strong>
                      {sample.final_answer}
                    </div>
                  </div>
                ))}
              </div>

              {/* Cost Analysis */}
              <div className="card">
                <h2>Cost Analysis</h2>
                <div className="cost-grid">
                  <div className="cost-item">
                    <span className="cost-label">Model Used:</span>
                    <span className="cost-value">{response.model_used}</span>
                  </div>
                  <div className="cost-item">
                    <span className="cost-label">Total Tokens:</span>
                    <span className="cost-value">{response.token_usage.total_tokens.toLocaleString()}</span>
                  </div>
                  <div className="cost-item">
                    <span className="cost-label">Prompt Tokens:</span>
                    <span className="cost-value">{response.token_usage.prompt_tokens.toLocaleString()}</span>
                  </div>
                  <div className="cost-item">
                    <span className="cost-label">Completion Tokens:</span>
                    <span className="cost-value">{response.token_usage.completion_tokens.toLocaleString()}</span>
                  </div>
                  <div className="cost-item">
                    <span className="cost-label">Input Cost:</span>
                    <span className="cost-value">${response.cost_analysis.input_cost.toFixed(6)}</span>
                  </div>
                  <div className="cost-item">
                    <span className="cost-label">Output Cost:</span>
                    <span className="cost-value">${response.cost_analysis.output_cost.toFixed(6)}</span>
                  </div>
                  <div className="cost-item highlight">
                    <span className="cost-label">Total Cost:</span>
                    <span className="cost-value">
                      ${response.cost_analysis.total_cost.toFixed(6)} {response.cost_analysis.currency}
                    </span>
                  </div>
                </div>

                <div className="chart-container">
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={[
                          { name: 'Prompt Tokens', value: response.token_usage.prompt_tokens },
                          { name: 'Completion Tokens', value: response.token_usage.completion_tokens },
                        ]}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name}: ${((percent ?? 0) * 100).toFixed(0)}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {[0, 1].map((_, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </>
          )}
        </main>
      </div>
    </>
  );
}

export default App;
