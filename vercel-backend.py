from flask import Flask, request, jsonify
from flask_cors import CORS
import anthropic
import json
import os

app = Flask(__name__)
CORS(app)

CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY', '')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        api_key = data.get('apiKey', CLAUDE_API_KEY)
        process_text = data.get('processText', '')

        if not process_text:
            return jsonify({'error': 'Process text required'}), 400
        if not api_key:
            return jsonify({'error': 'API key required'}), 400

        client = anthropic.Anthropic(api_key=api_key)
        prompt = f"""Analyze this Turkish business process and respond ONLY with valid JSON:
Process: "{process_text}"
Response must be:
{{"mermaid": "flowchart TD\\n    Start([Başla]) --> Step1[...]\\n    Step1 --> End([Bitir])", "analysis": {{"pillars": {{"human": 75, "system": 80, "process": 78, "operations": 72, "impact": 76}}, "elements": {{"lean": 72, "quality": 78, "improvement": 75}}, "recommendations": ["Tavsiye 1", "Tavsiye 2", "Tavsiye 3", "Tavsiye 4", "Tavsiye 5"]}}}}"""

        message = client.messages.create(model="claude-3-5-sonnet-20241022", max_tokens=2000, messages=[{"role": "user", "content": prompt}])
        response_text = message.content[0].text

        try:
            analysis_data = json.loads(response_text)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                analysis_data = json.loads(json_match.group())
            else:
                return jsonify({'error': 'Invalid response'}), 500

        return jsonify(analysis_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(debug=False)
