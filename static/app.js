const code=document.getElementById('code'),language=document.getElementById('language'),scanBtn=document.getElementById('scanBtn'),runBtn=document.getElementById('runBtn'),clearBtn=document.getElementById('clearBtn'),exampleBtn=document.getElementById('exampleBtn'),lineNumbers=document.getElementById('lineNumbers'),results=document.getElementById('results'),outputPanel=document.getElementById('outputPanel');
const examples={python:`def calculate_total(price, quantity):
    total = price * quantity
    return total

price = int(input("Price: "))
quantity = int(input("Quantity: "))
print("Total:", calculate_total(price, quantity))`,c:`#include <stdio.h>
int main() {
    int a = 10, b = 5;
    printf("Sum = %d\\n", a + b);
    return 0;
}`,cpp:`#include <iostream>
using namespace std;
int main() {
    int a = 10, b = 5;
    cout << "Sum = " << a + b << endl;
    return 0;
}`,java:`public class Main {
    public static void main(String[] args) {
        int a = 10, b = 5;
        System.out.println("Sum = " + (a + b));
    }
}`,javascript:`const a = 10;
const b = 5;
console.log("Sum =", a + b);`};
function updateEditor(){lineNumbers.textContent=Array.from({length:code.value.split('\n').length},(_,i)=>i+1).join('\n');document.getElementById('charCount').textContent=`${code.value.length} chars`}
function setFileName(){document.getElementById('fileLabel').textContent=`main.${{python:'py',c:'c',cpp:'cpp',java:'java',javascript:'js'}[language.value]}`}
function escapeHtml(v){return v.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]))}
function renderIssues(data){const c=data.counts;document.getElementById('syntaxCount').textContent=c.syntax;document.getElementById('logicCount').textContent=c.logic;document.getElementById('runtimeCount').textContent=c.runtime;document.getElementById('semanticCount').textContent=c.semantic;document.getElementById('warningCount').textContent=c.warning;const badge=document.getElementById('overallBadge');badge.textContent=data.total?`${data.total} FINDING${data.total===1?'':'S'}`:'CLEAN';badge.className=`overall-badge ${data.total?'bad':'clean'}`;document.getElementById('resultTitle').textContent=data.total?'Issues found':'Your code looks clean';document.getElementById('issues').innerHTML=data.issues.length?data.issues.map((x,i)=>`<article class="issue ${x.severity==='warning'?'warning':''}"><div class="issue-top"><div class="issue-title">#${i+1} ${escapeHtml(x.message)}</div><span class="tag">${escapeHtml(x.type)} · line ${x.line}</span></div><p>${escapeHtml(x.explanation)}</p><p class="fix"><b>How to fix:</b> ${escapeHtml(x.fix)}</p></article>`).join(''):'<div class="issue clean-issue"><div class="issue-title">✓ No obvious issues detected.</div><p>Static checks found no problems. You can now run the program and inspect its actual output.</p></div>';document.getElementById('finalText').textContent=data.total?`Final result: ${data.summary}`:'Final result: 0 syntax, 0 logical, 0 runtime, 0 semantic/type issues, and 0 warnings.';results.classList.remove('hidden');results.scrollIntoView({behavior:'smooth',block:'start'})}
async function scan(){const original=scanBtn.innerHTML;scanBtn.innerHTML='<span>Scanning…</span><b>ANALYZING</b>';scanBtn.disabled=true;try{const r=await fetch('/api/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({language:language.value,code:code.value})});const d=await r.json();if(!r.ok)throw Error(d.error||'Analysis failed');renderIssues(d)}catch(e){alert(e.message)}finally{scanBtn.innerHTML=original;scanBtn.disabled=false}}
async function runCode(){const original=runBtn.innerHTML;runBtn.innerHTML='<span>Running…</span><b>EXECUTING</b>';runBtn.disabled=true;outputPanel.classList.remove('hidden');document.getElementById('runStatus').textContent='RUNNING';document.getElementById('outputBox').textContent='Executing safely…';try{const r=await fetch('/api/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({language:language.value,code:code.value,stdin:document.getElementById('stdin').value})});const d=await r.json();if(!r.ok)throw Error(d.error||'Execution failed');const box=document.getElementById('outputBox');if(d.ok){document.getElementById('runStatus').textContent='SUCCESS';document.getElementById('outputTitle').textContent='Program finished successfully';box.textContent=d.output||'(Program produced no output)'}else{document.getElementById('runStatus').textContent='ERROR';document.getElementById('outputTitle').textContent=d.stage==='compile'?'Compilation error':'Runtime error';box.textContent=d.output||d.stderr||'The program exited with an error.'}}catch(e){document.getElementById('runStatus').textContent='FAILED';document.getElementById('outputBox').textContent=e.message}finally{runBtn.innerHTML=original;runBtn.disabled=false;outputPanel.scrollIntoView({behavior:'smooth',block:'start'})}}
language.addEventListener('change',()=>{setFileName();code.value=examples[language.value];updateEditor();results.classList.add('hidden');outputPanel.classList.add('hidden')});exampleBtn.addEventListener('click',()=>{code.value=examples[language.value];updateEditor();code.focus()});clearBtn.addEventListener('click',()=>{code.value='';updateEditor();code.focus()});code.addEventListener('input',updateEditor);code.addEventListener('scroll',()=>lineNumbers.scrollTop=code.scrollTop);scanBtn.addEventListener('click',scan);runBtn.addEventListener('click',runCode);code.addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&e.key==='Enter'){e.preventDefault();scan()}});setFileName();code.value=examples.python;updateEditor();
