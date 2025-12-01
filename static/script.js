// Store current quiz data globally
let currentQuiz = null;

async function uploadKnowledge(){
    const text = document.getElementById('knowledge-input').value;
    const statusDiv = document.getElementById('upload-status');

    if (!text) {alert("Please paste some text first"); return; }

    statusDiv.innerText = "Processing... please wait.";
    statusDiv.style.color = "yellow";

    try {
        const res = await fetch('/learn',{
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({text:text})
        });
        const data = await res.json();

        if (data.error){
            statusDiv.innerText = "Error: " + data.error;
            statusDiv.style.color = "red";
        }
        else{
            statusDiv.innerText = "✅" + data.message;
            statusDiv.style.color = "lightgreen";
        }
    }
    catch (e){
        statusDiv.innerText = "Connection failed.";
        statusDiv.style.color = "red";
    }
}


function handleEnter(event) {
    if (event.key === 'Enter') run('notes');
}

async function run(mode) {
    const topic = document.getElementById('topic').value;
    if(!topic) return alert("Enter a topic!");

    const loadDiv = document.getElementById('loading');
    const resDiv = document.getElementById('result-area');

    loadDiv.style.display = 'block';
    resDiv.innerHTML = '';

    try {
        const res = await fetch('/generate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({topic: topic, mode: mode})
        });
        const data = await res.json();
        render(data, mode);
    } catch(e) {
        console.error(e);
        resDiv.innerText = "Error connecting to server.";
    } finally {
        loadDiv.style.display = 'none';
    }
}

function render(data, mode) {
    const area = document.getElementById('result-area');
    if(data.error) { area.innerText = "Error: " + data.error; return; }

    // NEW WAY (Uses marked.parse to render the text):
if(mode === 'notes') {
    // Convert Markdown to HTML
    const cleanHtml = marked.parse(data.content);
    area.innerHTML = `<div class="card notes-content"><h3>📝 Study Notes</h3>${cleanHtml}</div>`;
    }
else if(mode === 'quiz') {
        // Quiz Mode
        currentQuiz = data.content;
        let html = `<div class="card"><h3>Quiz</h3><p><strong>${currentQuiz.question}</strong></p><ul>`;

        currentQuiz.options.forEach((opt, index) => {
            html += `<li><button onclick="check(this, ${index})">${opt}</button></li>`;
        });

        html += `</ul><div id="explanation" style="margin-top:10px;"></div></div>`;
        area.innerHTML = html;
    }
else if(mode === 'video'){
    area.innerHTML = `
    <div class="card">
        <h3>📺 ${data.content.title}</h3>
        <div style="position: relative; padding-bottom: 56.25%;height: 0;overflow: hidden">
            <iframe
                src="${data.content.url}"
                style="position: absolute;top: 0;left: 0;width: 100%;height: 100%;border: 0;"
                allowfullscreen>
            </iframe>
        </div>
    </div>`;
}
}

function check(btn, choiceIndex) {
    const feedback = document.getElementById('explanation');
    const choice = currentQuiz.options[choiceIndex];
    const correct = currentQuiz.answer;

    // Disable all buttons after selection
    const allBtns = btn.parentElement.parentElement.querySelectorAll('button');
    allBtns.forEach(b => b.disabled = true);

    if(choice === correct) {
        btn.style.background = "#2e7d32"; // Green
        feedback.innerHTML = `<span class="correct">Correct!</span> ${currentQuiz.explanation}`;
    } else {
        btn.style.background = "#c62828"; // Red
        feedback.innerHTML = `<span class="wrong">Incorrect.</span> The correct answer was <strong>${correct}</strong>.`;
    }
}