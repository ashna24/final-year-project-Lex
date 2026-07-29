import json
import requests
import gradio as gr

def analyze_contract_clause(clause_text):
    url = "http://localhost:11434/api/generate"
    
    system_prompt = """You are an expert legal AI assistant designed to help non-lawyers understand contracts. 
    Analyze the following clause and output your response STRICTLY as a JSON object with the following three keys:
    1. "risk_level": A string that must be exactly "High", "Medium", or "Low".
       - Use "High" for severe financial penalties, predatory traps, extreme liability shifts, or highly unusual restrictions.
       - Use "Medium" for standard industry obligations, temporary restrictions, or vague timelines (e.g., standard 6-month non-solicitation, "reasonable" effort clauses).
       - Use "Low" for standard legal boilerplate (e.g., severability, basic jurisdiction).
    2. "confidence_score": An integer from 0 to 100 representing how confident you are in your classification.
    3. "explanation": A plain English explanation of what this clause actually means, written at a 12-year-old reading level.
    Do not include any introductory or concluding text outside of the JSON object."""
    
    payload = {
        "model": "llama3.2",
        "prompt": f"{system_prompt}\n\nClause to analyze:\n{clause_text}",
        "format": "json",
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        if response.status_code == 200:
            result = response.json()
            parsed_data = json.loads(result['response'])
            
            # Extracting structured metrics to map to UI 
            risk = parsed_data.get("risk_level", "Unknown")
            confidence = f"{parsed_data.get('confidence_score', 0)}%"
            explanation = parsed_data.get("explanation", "No explanation provided.")
            return risk, confidence, explanation
            
        else:
            return "Error", "0%", f"API Error: {response.status_code}"
    except Exception as e:
        return "Error", "0%", f"Could not connect to local Ollama instance: {str(e)}"

# Defining examples
examples = [
    ["The Employee shall indemnify and hold harmless the Employer, its directors, and its affiliates from any claims, damages, or liabilities arising directly from their professional conduct during the term of employment."],
    ["This agreement constitutes the entire agreement between the parties with respect to its subject matter and supersedes all prior discussions, representations, or agreements."],
    ["The Landlord shall use reasonable endeavours to repair any reported faults in the heating or plumbing systems within a timeframe they solely deem to be commercially viable."]
]

#Gradio Interface
with gr.Blocks(title="Lex - AI Legal Analyzer") as demo:
    gr.Markdown("Lex: AI-Powered Legal Document Analyser")
    gr.Markdown("Feature Prototype - Llama 3.2")
    
    with gr.Row():
        with gr.Column():
            input_text = gr.Textbox(
                label="Contract Clause Text", 
                placeholder="Paste a contract clause here to analyze...", 
                lines=5
            )
            submit_btn = gr.Button("Analyze Clause", variant="primary")
            
            gr.Examples(examples=examples, inputs=input_text)
            
        with gr.Column():
            output_risk = gr.Label(label="Assessed Risk Level")
            output_conf = gr.Textbox(label="Model Confidence Score")
            output_expl = gr.Textbox(label="Plain English Explanation", lines=4)
            
    submit_btn.click(
        fn=analyze_contract_clause, 
        inputs=input_text, 
        outputs=[output_risk, output_conf, output_expl]
    )

if __name__ == "__main__":
    demo.launch()