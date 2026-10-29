from flask import Flask, render_template, request, jsonify
from analyzer import analyze_code
import os
import re
import requests

app = Flask(__name__)
PISTON = 'https://emkc.org/api/v2/piston/execute'
LANG_MAP = {
    'python': ('python', '3.10.0'),
    'java': ('java', '15.0.2'),
    'c': ('c', '10.2.0'),
}


def code_metrics(language, code, result):
    lines = code.splitlines()
    non_empty = [line for line in lines if line.strip()]
    comments = sum(1 for line in lines if line.strip().startswith(('#', '//', '/*', '*')))
    functions = 0
    if language == 'python':
        functions = len(re.findall(r'^\s*def\s+\w+\s*\(', code, re.M))
    elif language in {'c', 'java'}:
        functions = len(re.findall(r'\b(?:int|void|float|double|char|boolean|String|long|short|static|public|private|protected)\s+\w+\s*\([^;{}]*\)\s*\{', code))
    decisions = len(re.findall(r'\b(if|elif|else if|for|while|switch|case|catch|&&|\|\|)\b', code))
    errors = result.get('total', 0)
    score = max(0, 100 - errors * 12 - result.get('counts', {}).get('warning', 0) * 3)
    return {
        'lines': len(lines),
        'code_lines': len(non_empty),
        'comments': comments,
        'functions': functions,
        'decisions': decisions,
        'characters': len(code),
        'health_score': score,
    }


@app.get('/')
def index():
    return render_template('index.html')


@app.post('/api/analyze')
def analyze():
    data = request.get_json(silent=True) or {}
    language = str(data.get('language', '')).lower().strip()
    code = str(data.get('code', ''))
    if language not in LANG_MAP:
        return jsonify({'error': 'CodeLens AI currently supports only C, Python and Java.'}), 400
    if not code.strip():
        return jsonify({'error': 'Please paste or type some code first.'}), 400
    try:
        result = analyze_code(language, code)
        result['can_run'] = not any(x.get('severity') == 'error' for x in result.get('issues', []))
        result['metrics'] = code_metrics(language, code, result)
        result['language'] = language
        return jsonify(result)
    except Exception as exc:
        return jsonify({'error': f'Analysis failed safely: {exc}'}), 500


@app.post('/api/run')
def run_code():
    data = request.get_json(silent=True) or {}
    language = str(data.get('language', '')).lower().strip()
    code = str(data.get('code', ''))
    if language not in LANG_MAP:
        return jsonify({'error': 'Only C, Python and Java can be executed.'}), 400
    if not code.strip():
        return jsonify({'error': 'Please enter some code first.'}), 400
    try:
        runtime, version = LANG_MAP[language]
        payload = {
            'language': runtime,
            'version': version,
            'files': [{'name': 'Main.java' if language == 'java' else 'main', 'content': code}],
            'stdin': str(data.get('stdin', '')),
        }
        response = requests.post(PISTON, json=payload, timeout=20)
        response.raise_for_status()
        result = response.json()
        run = result.get('run', {})
        compile_result = result.get('compile', {})
        if compile_result.get('stderr'):
            return jsonify({'ok': False, 'stage': 'compile', 'output': compile_result.get('stderr', '')})
        return jsonify({
            'ok': run.get('code', 0) == 0,
            'stage': 'run',
            'output': run.get('output', '') or '',
            'stderr': run.get('stderr', ''),
            'exit_code': run.get('code', 0),
            'signal': run.get('signal'),
        })
    except requests.RequestException as exc:
        return jsonify({'error': f'Execution service unavailable: {exc}'}), 503
    except Exception as exc:
        return jsonify({'error': f'Execution failed safely: {exc}'}), 500


@app.get('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'CodeLens AI', 'languages': ['C', 'Python', 'Java']})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
