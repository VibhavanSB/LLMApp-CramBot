// Store current quiz data globally
let currentQuiz = null;

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
    } else {
        // Quiz Mode
        currentQuiz = data.content;
        let html = `<div class="card"><h3>Quiz</h3><p><strong>${currentQuiz.question}</strong></p><ul>`;

        currentQuiz.options.forEach((opt, index) => {
            html += `<li><button onclick="check(this, ${index})">${opt}</button></li>`;
        });

        html += `</ul><div id="explanation" style="margin-top:10px;"></div></div>`;
        area.innerHTML = html;
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