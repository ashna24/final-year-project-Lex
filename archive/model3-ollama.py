import ollama

def analyse_clause(clause):
    response = ollama.chat(model='llama3.2', messages=[
        {
            'role': 'system',
            'content': '''You are a legal document analyst helping non-lawyers understand contracts.

Your job is to analyse a legal clause and return THREE things:

1. RISK LEVEL: Choose exactly one of: HIGH RISK, MEDIUM RISK, or LOW RISK
   - HIGH RISK: clauses involving indemnity, liability waivers, unlimited obligations, 
     rights waivers, penalty clauses, clauses that survive termination indefinitely
   - MEDIUM RISK: termination clauses, non-compete restrictions, payment penalties, 
     data sharing, confidentiality obligations
   - LOW RISK: governing law, notice provisions, standard boilerplate, 
     dispute resolution, definitions

2. PLAIN ENGLISH EXPLANATION: Explain what this clause means in 2-3 simple sentences 
   that anyone can understand. No legal jargon.

3. CONFIDENCE: How confident are you in this risk assessment? 
   Choose one of: HIGH, MEDIUM, LOW and explain why in one sentence.

Always end with this exact disclaimer:
"Note: This is an AI-generated analysis and does not constitute legal advice."

Format your response exactly like this:
RISK LEVEL: [level]
EXPLANATION: [explanation]
CONFIDENCE: [level] - [reason]
DISCLAIMER: Note: This is an AI-generated analysis and does not constitute legal advice.'''
        },
        {
            'role': 'user',
            'content': f'Please analyse this clause:\n\n{clause}'
        }
    ])
    return response['message']['content']


clauses = [
    "The Client shall indemnify and hold harmless the Service Provider from any and all claims, damages, losses, costs and expenses arising out of or in connection with the Client's use of the services. This obligation shall survive termination of this agreement indefinitely.",

    "Either party may terminate this agreement by providing 30 days written notice to the other party.",

    "The Service Provider shall make reasonable efforts to ensure the platform is available 99% of the time.",

    "The Client waives all rights to pursue legal action against the Service Provider under any circumstances whatsoever.",

    "This agreement shall be governed by the laws of England and Wales."
]

print("=== LLAMA 3.2 CLAUSE ANALYSIS RESULTS ===\n")

for i, clause in enumerate(clauses, 1):
    print(f"--- Clause {i} ---")
    print(f"Input: {clause[:80]}...")
    print()
    result = analyse_clause(clause)
    print(result)
    print("\n" + "="*60 + "\n")