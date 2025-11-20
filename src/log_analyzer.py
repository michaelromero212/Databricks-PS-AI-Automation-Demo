import os
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from dotenv import load_dotenv

load_dotenv()

class LogAnalyzer:
    def __init__(self):
        self.model_id = os.getenv("MODEL_ID", "Qwen/Qwen2.5-1.5B-Instruct")
        self.hf_token = os.getenv("HF_TOKEN")
        self.pipeline = None
        self._initialize_model()

    def _initialize_model(self):
        """Initializes the Hugging Face pipeline."""
        print(f"Loading model: {self.model_id}...")
        try:
            # Check for GPU availability
            device = "cuda" if torch.cuda.is_available() else "cpu"
            if torch.backends.mps.is_available():
                device = "mps" # For Apple Silicon

            print(f"Using device: {device}")

            self.pipeline = pipeline(
                "text-generation",
                model=self.model_id,
                token=self.hf_token,
                device_map="auto" if device != "cpu" else None,
                torch_dtype=torch.float16 if device != "cpu" else torch.float32,
                max_new_tokens=512,
                truncation=True
            )
            print("Model loaded successfully.")
        except Exception as e:
            print(f"Error loading model: {e}")
            self.pipeline = None

    def analyze_log(self, log_text):
        """Analyzes the log text using the LLM."""
        if not self.pipeline:
            return {
                "root_cause": "Model not initialized.",
                "remediation": "Check model configuration.",
                "insights": "Ensure internet connection and valid HF token if required."
            }

        prompt = f"""
You are an expert Databricks Platform Engineer and Consultant.
Analyze the following Databricks log data and provide a structured report.

LOG DATA:
{log_text}

INSTRUCTIONS:
1. Identify the Root Cause of the failure or performance issue.
2. Recommend specific Remediation steps to fix the issue.
3. Provide additional Contextual Insights (e.g., impact on cost, best practices).

FORMAT YOUR RESPONSE AS JSON:
{{
  "root_cause": "...",
  "remediation": "...",
  "insights": "..."
}}
"""
        
        try:
            messages = [{"role": "user", "content": prompt}]
            # Apply chat template if available, otherwise raw prompt
            if hasattr(self.pipeline.tokenizer, "apply_chat_template"):
                prompt_formatted = self.pipeline.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            else:
                prompt_formatted = prompt

            outputs = self.pipeline(prompt_formatted, max_new_tokens=512, do_sample=True, temperature=0.7)
            generated_text = outputs[0]['generated_text']
            
            # Extract JSON part (simple heuristic)
            # In a real app, we'd use a more robust parser or constrained generation
            response_text = generated_text.split(prompt_formatted)[-1] if prompt_formatted in generated_text else generated_text
            
            # Clean up potential markdown code blocks
            response_text = response_text.replace("```json", "").replace("```", "").strip()
            
            import json
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError:
                # Fallback if model didn't output valid JSON
                result = {
                    "root_cause": "Could not parse structured response.",
                    "remediation": "Review raw output.",
                    "insights": response_text
                }
            
            return result

        except Exception as e:
            return {
                "root_cause": f"Error during inference: {str(e)}",
                "remediation": "Check logs.",
                "insights": "Model execution failed."
            }

if __name__ == "__main__":
    # Test run
    analyzer = LogAnalyzer()
    sample_log = '{"message": "Cluster startup failed: INIT_SCRIPT_FAILURE"}'
    print(analyzer.analyze_log(sample_log))
