# CodeLens AI

**Understand your code. Fix your errors.**

CodeLens AI is a developer-focused static code analysis web app for C, C++, Java, Python and JavaScript. Paste code, choose a language, and scan it for common syntax, logic, runtime-risk, semantic/type and code-quality issues.

## Features

- Premium charcoal grey / moonlight silver / signal red interface
- C, C++, Java, Python and JavaScript support
- Line-numbered editor
- Syntax and bracket checks
- Common logic and runtime-risk checks
- Simple-English explanations
- Suggested fixes
- Final error summary
- No arbitrary user code execution

## Run locally

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

## Important

This project intentionally performs static analysis instead of executing submitted source code. Static analysis cannot guarantee that every possible logical or runtime problem is detected.
