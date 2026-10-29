from flask import Flask, render_template, request, jsonify
from analyzer import analyze_code

app = Flask(__name__)

@app.get('/')
def index():
    return render_template('index.html')

@app.post('/api/analyze')
def analyze():
    data = request.get_json(silent=True) or {}
    language = str(data.get('language', '')).lower().strip()
    code = str(data.get('code', ''))
    if language not in {'c', 'cpp', 'java', 'python', 'javascript'}:
        return jsonify({'error': 'Please select a supported language.'}), 400
    if not code.strip():
        return jsonify({'error': 'Please paste or type some code first.'}), 400
    try:
        return jsonify(analyze_code(language, code))
    except Exception as exc:
        return jsonify({'error': f'Analysis failed safely: {exc}'}), 500

@app.get('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'CodeLens AI'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
