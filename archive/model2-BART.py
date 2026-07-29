from transformers import pipeline

classifier = pipeline("zero-shot-classification", 
                      model="facebook/bart-large-mnli")

clauses = [
    "The Client shall indemnify and hold harmless the Service Provider from any and all claims, damages, losses, costs and expenses arising out of or in connection with the Client's use of the services. This obligation shall survive termination of this agreement indefinitely.",
    
    "Either party may terminate this agreement by providing 30 days written notice to the other party.",
    
    "The Service Provider shall make reasonable efforts to ensure the platform is available 99% of the time."
]

labels = [
    "clause that creates significant legal liability or obligation for the signing party",
    "clause that creates moderate obligations or restrictions",
    "clause that is standard and creates minimal risk for the signing party"
]

risk_map = {
    "clause that creates significant legal liability or obligation for the signing party": "HIGH RISK",
    "clause that creates moderate obligations or restrictions": "MEDIUM RISK",
    "clause that is standard and creates minimal risk for the signing party": "LOW RISK"
}
print("=== CLAUSE CLASSIFICATION RESULTS ===\n")

for i, clause in enumerate(clauses, 1):
    result = classifier(clause, candidate_labels=labels)
    print(f"Clause {i}:")
    print(f"Text: {clause[:80]}...")
    print("Scores:")
    for label, score in zip(result['labels'], result['scores']):
        print(f"  {risk_map[label]}: {score:.2%}")
    print()