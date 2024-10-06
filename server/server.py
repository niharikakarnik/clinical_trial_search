from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import json

# Open AI Details
client = OpenAI(
    api_key = "YOUR_API_KEY",
)

# Flask app
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests (useful for React frontends)

# Load clinical trials data from JSON
with open('/Users/niharikakarnik/Documents/argon_interview/server/ctg-studies.json', 'r') as f:
    clinical_trials = json.load(f)

# Retrieve list of similar medical terms from openai. Limiting to 5 synonyms since current search for terms is bruteforce
def get_synonyms(query):
    # For production should have better error handling and surface issue to user. For now, just log it.
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert in the medical field. Return a list of up to 5 synonyms for the query. Acronyms can be used as synonyms"},
                {"role": "user", "content": f"What are the synonyms for {query}?"}
            ],
            max_tokens=100
        )
        synonyms_text = response['choices'][0]['message']['content']
        print(f"Synonyms: {synonyms_text}")
        synonyms = [syn.strip() for syn in synonyms_text.split('\n') if syn.strip()]
        return synonyms[:5]  # Limit to 5 synonyms
    except Exception as e:
        print(f"Error getting synonyms: {e}")
        return []
    
# Function to search the clinical trials dataset for matching terms
# Right now this is doing a brute force search. If the dataset is stored in a database, to optimize the search, I would want to use elastic search to query my results
def search_json(clinical_trials, synonyms):
    results = []
    for trial in clinical_trials:
        # Combine relevant fields to search through
        trial_text = (
            trial.get('protocolSection', {}).get('identificationModule', {}).get('briefTitle', '') + ' ' +
            ' '.join(trial.get('protocolSection', {}).get('conditionsModule', {}).get('conditions', [])) + ' ' +
            ' '.join(trial.get('protocolSection', {}).get('conditionsModule', {}).get('keywords', [])) + ' ' +
            trial.get('protocolSection', {}).get('descriptionModule', {}).get('briefSummary', '')
        ).lower()

        # Check if any of the synonyms appear in the trial text
        if any(synonym.lower() in trial_text for synonym in synonyms):
            results.append({
                "nctId": trial.get('protocolSection', {}).get('identificationModule', {}).get('nctId', ''),
                "briefTitle": trial.get('protocolSection', {}).get('identificationModule', {}).get('briefTitle', ''),
                "officialTitle": trial.get('protocolSection', {}).get('identificationModule', {}).get('officialTitle', ''),
                "keywords": trial.get('protocolSection', {}).get('conditionsModule', {}).get('keywords', [])
            })
    return results

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    if not query:
        return jsonify({"error": "No query provided"}), 400

    # Step 1: Get synonyms for the search query using OpenAI
    synonyms = get_synonyms(query)
    print(f"Synonyms for '{query}': {synonyms}")

    # Step 2: Perform brute-force search on the JSON file using the synonyms
    results = search_json(clinical_trials, synonyms)

    # Step 3: Return the search results
    if results:
        return jsonify(results)
    else:
        return jsonify({"message": "No matching clinical trials found."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
