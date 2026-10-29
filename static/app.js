const code = document.getElementById('code');
const language = document.getElementById('language');
const scanBtn = document.getElementById('scanBtn');
const clearBtn = document.getElementById('clearBtn');
const lineNumbers = document.getElementById('lineNumbers');
const results = document.getElementById('results');

const examples = {
  python: `def calculate_total(price, quantity):\n    total = price * quantity\n    if quantity > 0:\n        print("Total:", total)\n    return total\n\nprice = int(input("Price: "))\nquantity = int(input("Quantity: "))\nprint(calculate_total(price, quantity))`,
  c: `#include <stdio.h>\n\nint main() {\n    int value;\n    scanf("%d", value);\n    if (value = 10) {\n        printf("Ten\\n");\n    }\n    return 0;\n}`,
  cpp: `#include <iostream>\nusing namespace std;\n\nint main() {\n    int a = 10;\n    int b = 0;\n    cout << a / b << endl;\n    return 0;\n}`,
  java: `public class Main {\n    public static void main(String[] args) {\n        int a = 10;\n        int b = 0;\n        System.out.println(a / b);\n    }\n}`,
  javascript: `const price = 100;\nlet quantity = 2;\nif (quantity = 0) {\n    console.log("No items");\n}\nconsole.log(price * quantity);`
};

function updateEditor() {
  const count = code.value.split('\n').length;
  lineNumbers.textContent = Array.from({length: count}, (_, i) => i + 1).join('\n');
  document.getElementById('charCount').textContent = `${code.value.length} chars`;
}

function setFileName() {
  const ext = {python:'py', c:'c', cpp:'cpp', java:'java', javascript:'js'}[language.value];
  document.getElementById('fileLabel').textContent = `main.${ext}`;
}

function escapeHtml(value) {
  return value.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));
}

function renderIssues(data) {
  const c = data.counts;
  document.getElementById('syntaxCount').textContent = c.syntax;
  document.getElementById('logicCount').textContent = c.logic;
  document.getElementById('runtimeCount').textContent = c.runtime;
  document.getElementById('semanticCount').textContent = c.semantic;
  document.getElementById('warningCount').textContent = c.warning;

  const badge = document.getElementById('overallBadge');
  badge.textContent = data.total ? `${data.total} FINDING${data.total === 1 ? '' : 'S'}` : 'CLEAN';
  badge.className = `overall-badge ${data.total ? 'bad' : 'clean'}`;
  document.getElementById('resultTitle').textContent = data.total ? 'Issues found' : 'Your code looks clean';

  const issueBox = document.getElementById('issues');
  issueBox.innerHTML = data.issues.length ? data.issues.map((x, i) => `
    <article class="issue ${x.severity === 'warning' ? 'warning' : ''}">
      <div class="issue-top"><div class="issue-title">#${i + 1} ${escapeHtml(x.message)}</div><span class="tag">${escapeHtml(x.type)} · line ${x.line}</span></div>
      <p>${escapeHtml(x.explanation)}</p>
      <p class="fix"><b>How to fix:</b> ${escapeHtml(x.fix)}</p>
    </article>`).join('') : '<div class="issue" style="border-left-color:#70a874"><div class="issue-title">No obvious issues detected.</div><p>CodeLens found no problems with the static checks for this language. This does not prove that every possible logical or runtime issue is absent.</p></div>';

  document.getElementById('finalText').textContent = data.total
    ? `Final result: ${data.summary}`
    : 'Final result: 0 syntax, 0 logical, 0 runtime, 0 semantic/type issues, and 0 warnings.';
  results.classList.remove('hidden');
  results.scrollIntoView({behavior:'smooth', block:'start'});
}

async function scan() {
  const original = scanBtn.innerHTML;
  scanBtn.innerHTML = '<span>Scanning…</span><b>ANALYZING</b>';
  scanBtn.disabled = true;
  try {
    const response = await fetch('/api/analyze', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({language: language.value, code: code.value})
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Analysis failed');
    renderIssues(data);
  } catch (error) {
    alert(error.message);
  } finally {
    scanBtn.innerHTML = original;
    scanBtn.disabled = false;
  }
}

language.addEventListener('change', () => { setFileName(); code.value = examples[language.value]; updateEditor(); });
code.addEventListener('input', updateEditor);
code.addEventListener('scroll', () => { lineNumbers.scrollTop = code.scrollTop; });
clearBtn.addEventListener('click', () => { code.value = ''; updateEditor(); code.focus(); });
scanBtn.addEventListener('click', scan);
code.addEventListener('keydown', e => { if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') { e.preventDefault(); scan(); } });

setFileName(); updateEditor();
