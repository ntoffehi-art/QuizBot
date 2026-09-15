let currentQuestion = null;
let score = 0;
let totalQuestions = 0;

async function Quiz() {
    const catElement = document.getElementById("cat");
    const langElement = document.getElementById("lang");

    const category = catElement ? catElement.value : "";
    const language = langElement ? langElement.value : "";

    if (!category || category === "" || !language || language === "") {
        alert("Veuillez choisir une catégorie et une langue avant de commencer !");
        return; // إيقاف العملية ومنع التردد على السيرفر
    }
    document.getElementById("welcome").classList.add("hidden");
    const scoreScreen = document.getElementById("score-screen");
    if (scoreScreen) scoreScreen.classList.add("hidden");

    document.getElementById("loading").classList.remove("hidden");

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
const translations = {
    fr: { correct: "Bravo ! Réponse Correcte 🎉", wrong: "Oups ! La bonne réponse était : ", justif: "💡 Justification : " },
    ar: { correct: "أحسنت! إجابة صحيحة 🎉", wrong: "للأسف! الإجابة الصحيحة هي: ", justif: "💡 الإجابة: " },
    en: { correct: "Good job! Correct Answer 🎉", wrong: "Oops! The correct answer was: ", justif: "💡 Justification: " },
};
function selectOpt(selectedText) {
    if (!currentQuestion) return;

    document.getElementById("quiz").classList.add("hidden");
    document.getElementById("loading").classList.remove("hidden");

    const lang = document.getElementById("lang").value || "fr";
    const t = translations[lang] || translations.fr;
    totalQuestions += 1;

    setTimeout(() => {
        document.getElementById("loading").classList.add("hidden");
        if (selectedText.trim() === currentQuestion.answer.trim()) {
            score += 1;
            document.getElementById("response-text").innerText = t.correct;
        } else {
            document.getElementById("response-text").innerText = t.wrong + currentQuestion.answer;
        }

        document.getElementById("justification-text").innerText = t.justif + currentQuestion.explanation;
        document.getElementById("react").classList.remove("hidden");
    }, 500);
}

function nextQuestion() {
    document.getElementById("react").classList.add("hidden");
    Quiz();
}

function quitQuiz() {
    const userConfirmed = confirm("Voulez-vous vraiment quitter le quiz ?");
    if (!userConfirmed) {
        return;
    }
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