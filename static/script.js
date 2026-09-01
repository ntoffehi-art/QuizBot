let currentQuestion = null;
let score = 0;
let totalQuestions = 0;

async function Quiz() {
    document.getElementById("welcome").classList.add("hidden");
    // إذا كنتِ زدتِ شاشة السكور في الـ HTML نخفيوها زادة
    const scoreScreen = document.getElementById("score-screen");
    if (scoreScreen) scoreScreen.classList.add("hidden");

    document.getElementById("loading").classList.remove("hidden");

    const category = document.getElementById("cat").value || "IT";
    const language = document.getElementById("lang").value || "fr";

    try {
        const response = await fetch('/generate-question', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ category: category, language: language })
        });

        const textData = await response.text(); 
        let data;
        try {
            data = JSON.parse(textData);
        } catch (e) {
            throw new Error("Le serveur a planté et n'a pas renvoyé de JSON. Détails: " + textData.substring(0, 100));
        }

        if (data.error) {
            throw new Error(data.error);
        }

        currentQuestion = data;
        document.getElementById("question-text").innerText = data.question;
        document.getElementById("btn1").innerText = data.options[0];
        document.getElementById("btn2").innerText = data.options[1];
        document.getElementById("btn3").innerText = data.options[2];

        document.getElementById("loading").classList.add("hidden");
        document.getElementById("quiz").classList.remove("hidden");

    } catch (error) {
        console.error("Erreur bloquante:", error);
        alert("Erreur technique: " + error.message);
        
        document.getElementById("loading").classList.add("hidden");
        document.getElementById("welcome").classList.remove("hidden");
    }
}

function selectOpt(selectedText) {
    if (!currentQuestion) return;

    document.getElementById("quiz").classList.add("hidden");
    document.getElementById("loading").classList.remove("hidden");

    totalQuestions += 1;

    setTimeout(() => {
        document.getElementById("loading").classList.add("hidden");
        if (selectedText.trim() === currentQuestion.answer.trim()) {
            score += 1;
            document.getElementById("response-text").innerText = "Bravo ! Réponse Correcte 🎉";
        } else {
            document.getElementById("response-text").innerText = "Oups ! La bonne réponse était : " + currentQuestion.answer;
        }

        document.getElementById("justification-text").innerText = "💡 Justification : " + currentQuestion.explanation;
        document.getElementById("react").classList.remove("hidden");
    }, 500);
}

function nextQuestion() {
    document.getElementById("react").classList.add("hidden");
    Quiz();
}

function quitQuiz() {
    document.getElementById("quiz").classList.add("hidden");
    document.getElementById("react").classList.add("hidden");
    document.getElementById("loading").classList.add("hidden");
    document.getElementById("welcome").classList.add("hidden");

    let scoreScreen = document.getElementById("score-screen");
    if (scoreScreen) {
        scoreScreen.style.display = "block";
        scoreScreen.classList.remove("hidden");
    }
    
    document.getElementById("final-score").innerText = `${score} / ${totalQuestions}`;
}

function goHome() {
    window.location.href = '/';
}