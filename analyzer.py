import ast
import re


def issue(kind, line, message, explanation, fix, severity='error'):
    return {
        'type': kind,
        'line': line,
        'message': message,
        'explanation': explanation,
        'fix': fix,
        'severity': severity,
    }


def balanced_delimiters(code):
    pairs = {')': '(', ']': '[', '}': '{'}
    stack = []
    in_string = None
    escaped = False
    for line_no, line in enumerate(code.splitlines(), 1):
        for ch in line:
            if in_string:
                if escaped:
                    escaped = False
                elif ch == '\\':
                    escaped = True
                elif ch == in_string:
                    in_string = None
                continue
            if ch in "'\"`":
                in_string = ch
            elif ch in '([{':
                stack.append((ch, line_no))
            elif ch in ')]}':
                if not stack or stack[-1][0] != pairs[ch]:
                    return issue('Syntax', line_no, f'Unexpected closing {ch}.', 'A closing bracket does not match the opening bracket before it.', 'Check the brackets on this line and the previous few lines.')
                stack.pop()
    if stack:
        ch, line_no = stack[-1]
        close = {'(': ')', '[': ']', '{': '}'}[ch]
        return issue('Syntax', line_no, f'Missing closing {close}.', 'An opening bracket was not closed.', f'Add the missing {close} or remove the extra {ch}.')
    return None


def python_analysis(code):
    issues = []
    try:
        ast.parse(code)
    except SyntaxError as e:
        issues.append(issue('Syntax', e.lineno or 1, e.msg, 'Python could not understand the structure of this code.', 'Correct the highlighted syntax near this line and scan again.'))
        return issues

    lines = code.splitlines()
    for i, line in enumerate(lines, 1):
        if re.search(r'\binput\s*\([^)]*\)\s*\+\s*\d', line):
            issues.append(issue('Type/Semantic', i, 'input() returns text.', 'Adding a number directly to input text causes a TypeError at runtime.', 'Convert it first, for example: int(input(...)).'))
        if re.search(r'\bprint\s*\([^)]*\b([A-Za-z_]\w*)\s*\+\s*([A-Za-z_]\w*)[^)]*\)', line):
            pass
        if 'while True:' in line and i < len(lines) and not any('break' in x for x in lines[i:i+15]):
            issues.append(issue('Logic', i, 'Possible infinite loop.', 'The loop is always true and no break is visible nearby.', 'Make the condition eventually false or add a controlled break.', 'warning'))
        if re.search(r'==\s*None', line):
            issues.append(issue('Code Quality', i, 'Use "is None" for None checks.', 'Python style and identity semantics are clearer with is None.', 'Replace == None with is None.', 'warning'))
        if 'except:' in line and not re.search(r'except\s+\w', line):
            issues.append(issue('Code Quality', i, 'Bare except catches everything.', 'It can hide unexpected errors and make debugging difficult.', 'Catch the specific exception you expect.', 'warning'))
    return issues


def c_like_analysis(code, language):
    issues = []
    lines = code.splitlines()
    b = balanced_delimiters(code)
    if b:
        issues.append(b)

    if language in {'c', 'cpp'}:
        if not re.search(r'\bmain\s*\(', code):
            issues.append(issue('Semantic', 1, 'No main() function found.', 'A normal executable C/C++ program needs an entry point.', 'Add int main() { ... }.', 'warning'))
        for i, line in enumerate(lines, 1):
            if re.search(r'\bscanf\s*\([^;]*%[a-zA-Z][^;]*\)', line) and '&' not in line and re.search(r'%[diu]', line):
                issues.append(issue('Runtime', i, 'scanf may need an address.', 'Numeric scanf arguments normally need &variable so scanf can store the value.', 'Use scanf("%d", &value) for an int.', 'error'))
            if re.search(r'\bif\s*\([^)]*=[^=]', line):
                issues.append(issue('Logic', i, 'Assignment used inside if condition.', 'This may be intentional, but it is often a typo for ==.', 'If you meant comparison, use ==.', 'warning'))
            if re.search(r'/\s*0\b|%\s*0\b', line):
                issues.append(issue('Runtime', i, 'Division by zero.', 'The program can fail when it reaches this expression.', 'Make sure the divisor cannot be zero before dividing.'))
            if 'gets(' in line:
                issues.append(issue('Runtime/Security', i, 'gets() is unsafe.', 'gets() can overflow the input buffer and is removed from modern C standards.', 'Use fgets() with a buffer size.', 'warning'))
            if language == 'cpp' and 'using namespace std;' in line:
                issues.append(issue('Code Quality', i, 'Global using namespace std.', 'It can create naming conflicts in larger projects.', 'Prefer std::cout, std::vector, etc., especially in headers.', 'warning'))
    return issues


def java_analysis(code):
    issues = []
    b = balanced_delimiters(code)
    if b:
        issues.append(b)
    lines = code.splitlines()
    if not re.search(r'\bclass\s+\w+', code):
        issues.append(issue('Syntax', 1, 'No class declaration found.', 'Java source code normally needs a class declaration.', 'Add a class and place the program inside it.'))
    if 'public static void main' not in code:
        issues.append(issue('Semantic', 1, 'No standard main method found.', 'The Java launcher needs a main entry point for a normal console program.', 'Add public static void main(String[] args).', 'warning'))
    for i, line in enumerate(lines, 1):
        if re.search(r'\bString\s+\w+\s*=\s*[^;]+;', line) and '"' not in line and 'new String' not in line:
            issues.append(issue('Type/Semantic', i, 'Check String assignment.', 'A String variable should receive a String expression, not a numeric or boolean value.', 'Make sure the assigned expression has type String.', 'warning'))
        if re.search(r'\bif\s*\([^)]*=[^=]', line):
            issues.append(issue('Syntax/Logic', i, 'Assignment inside if condition.', 'Java uses == for primitive comparison and .equals() for String content.', 'Replace accidental = with ==, or use .equals() for Strings.'))
        if re.search(r'/\s*0\b', line):
            issues.append(issue('Runtime', i, 'Division by zero.', 'Integer division by zero throws ArithmeticException.', 'Validate the divisor before division.'))
    return issues


def javascript_analysis(code):
    issues = []
    b = balanced_delimiters(code)
    if b:
        issues.append(b)
    lines = code.splitlines()
    for i, line in enumerate(lines, 1):
        if re.search(r'\b(const|let)\s+\w+\s*=\s*[^;]+\s*$', line) and line.strip().startswith(('const ', 'let ')):
            pass
        if re.search(r'\bvar\s+', line):
            issues.append(issue('Code Quality', i, 'var is used.', 'Modern JavaScript generally prefers let and const because their scoping is safer.', 'Use const when the binding does not change, otherwise let.', 'warning'))
        if re.search(r'\bif\s*\([^)]*=[^=]', line):
            issues.append(issue('Logic', i, 'Assignment inside if condition.', 'This is often an accidental assignment instead of a comparison.', 'Use === or == when you mean to compare.', 'warning'))
        if re.search(r'console\.log\s*\(', line):
            issues.append(issue('Code Quality', i, 'Debug console.log detected.', 'Leaving debug output in production code can clutter the console.', 'Remove it or replace it with a deliberate logging strategy.', 'warning'))
    return issues


def add_generic_checks(code, language, issues):
    lines = code.splitlines()
    for i, line in enumerate(lines, 1):
        if len(line) > 140:
            issues.append(issue('Code Quality', i, 'Very long line.', 'Long lines are harder to read and maintain.', 'Break the statement into smaller logical pieces.', 'warning'))
        if re.search(r'\bTODO\b|\bFIXME\b', line, re.I):
            issues.append(issue('Code Quality', i, 'TODO/FIXME marker found.', 'This comment suggests unfinished work remains.', 'Review the marker before considering the code complete.', 'warning'))
    return issues


def analyze_code(language, code):
    if language == 'python':
        issues = python_analysis(code)
    elif language in {'c', 'cpp'}:
        issues = c_like_analysis(code, language)
    elif language == 'java':
        issues = java_analysis(code)
    else:
        issues = javascript_analysis(code)

    add_generic_checks(code, language, issues)
    # Deduplicate exact findings.
    unique = []
    seen = set()
    for item in issues:
        key = (item['type'], item['line'], item['message'])
        if key not in seen:
            seen.add(key)
            unique.append(item)

    counts = {'syntax': 0, 'logic': 0, 'runtime': 0, 'semantic': 0, 'warning': 0}
    for item in unique:
        t = item['type'].lower()
        if 'syntax' in t:
            counts['syntax'] += 1
        elif 'logic' in t:
            counts['logic'] += 1
        elif 'runtime' in t:
            counts['runtime'] += 1
        elif 'semantic' in t or 'type' in t:
            counts['semantic'] += 1
        else:
            counts['warning'] += 1

    return {
        'language': language,
        'issues': unique,
        'counts': counts,
        'total': len(unique),
        'summary': f"{counts['syntax']} syntax, {counts['logic']} logical, {counts['runtime']} runtime, {counts['semantic']} semantic/type issue(s), and {counts['warning']} warning(s).",
        'status': 'clean' if not unique else 'issues'
    }
