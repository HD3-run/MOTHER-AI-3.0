const chatContainer = document.getElementById("chatContainer");
const statusDisplay = document.getElementById("status");
const userInput = document.getElementById("userInput");

let recognition = null;

// Function to get a female voice
function getFemaleVoice() {
    const voices = window.speechSynthesis.getVoices();
    // Common female voice names across platforms
    const femaleVoiceNames = ["Samantha", "Zira", "Tessa", "Victoria", "Karen", "female"];
    return voices.find(voice => 
        femaleVoiceNames.some(name => voice.name.toLowerCase().includes(name.toLowerCase()))
    ) || voices[0]; // Fallback to default voice if no female voice is found
}

// Ensure voices are loaded before use
let voicesLoaded = false;
window.speechSynthesis.onvoiceschanged = () => {
    voicesLoaded = true;
};

function addMessage(sender, text) {
    const bubble = document.createElement("div");
    bubble.className = `bubble ${sender}`;
    bubble.innerHTML = `
        <p class="sender">${sender === 'user' ? 'You' : 'MOTHER'}</p>
        <p class="text">${text}</p>
    `;
    chatContainer.appendChild(bubble);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

async function sendToMother(message) {
    addMessage("user", message);
    statusDisplay.textContent = "Thinking...";

    try {
        const res = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message }),
        });

        const data = await res.json();

        if (data.response) {
            addMessage("mother", data.response);
            // Configure TTS with a female voice
            const utter = new SpeechSynthesisUtterance(data.response);
            if (voicesLoaded) {
                utter.voice = getFemaleVoice();
            } else {
                // Wait for voices to load if not ready
                window.speechSynthesis.onvoiceschanged = () => {
                    utter.voice = getFemaleVoice();
                    speechSynthesis.speak(utter);
                };
            }
            utter.rate = 1.0; // Normal speed
            utter.pitch = 1.2; // Slightly higher pitch for a female tone
            utter.volume = 0.9; // Near full volume
            speechSynthesis.speak(utter);
        } else {
            addMessage("mother", `⚠️ ${data.error || "Unknown error occurred"}`);
        }
    } catch (e) {
        console.error("[Fetch Error]", e);
        addMessage("mother", "⚠️ Could not reach server.");
    } finally {
        statusDisplay.textContent = "Idle";
    }
}

async function loadMemory() {
    try {
        const res = await fetch("/memory");
        const data = await res.json();
        const memoryPanel = document.querySelector(".memory-panel");
        memoryPanel.innerHTML = "";
        for (const [key, value] of Object.entries(data.facts)) {
            const p = document.createElement("p");
            p.innerHTML = `<strong>${key}:</strong> ${value}`;
            memoryPanel.appendChild(p);
        }
        const reflectionP = document.createElement("p");
        reflectionP.innerHTML = `<strong>Last Reflection:</strong> ${data.last_reflection}`;
        memoryPanel.appendChild(reflectionP);
    } catch (e) {
        console.error("Failed to load memory:", e);
        const memoryPanel = document.querySelector(".memory-panel");
        memoryPanel.innerHTML = "<p>Failed to load memory data.</p>";
    }
}

document.getElementById("exit-btn").addEventListener("click", () => {
  fetch("/exit", {
    method: "POST"
  })
  .then(res => res.json())
  .then(data => {
    alert(data.message); // Shows warm/funny message
    window.close(); // Try closing tab (browser may block)
  })
  .catch(err => {
    alert("Something went wrong while exiting.");
    console.error(err);
  });
});

document.addEventListener("DOMContentLoaded", loadMemory);

document.getElementById("sendBtn").onclick = () => {
    const msg = userInput.value.trim();
    if (msg) {
        userInput.value = "";
        sendToMother(msg);
    }
};

userInput.onkeydown = (e) => {
    if (e.key === "Enter") document.getElementById("sendBtn").click();
};

document.getElementById("micBtn").onclick = () => {
    if (!("webkitSpeechRecognition" in window || "SpeechRecognition" in window)) {
        alert("Your browser doesn't support speech recognition.");
        return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.interimResults = false;

    recognition.onstart = () => (statusDisplay.textContent = "Listening...");
    recognition.onresult = (e) => {
        statusDisplay.textContent = "Idle";
        const transcript = e.results[0][0].transcript;
        sendToMother(transcript);
    };
    recognition.onerror = () => (statusDisplay.textContent = "Idle");
    recognition.onend = () => (statusDisplay.textContent = "Idle");

    recognition.start();
};

document.getElementById("stopSpeechBtn").onclick = () => {
    speechSynthesis.cancel();
};

document.getElementById("forceIdleBtn").onclick = () => {
    if (recognition) recognition.abort();
    statusDisplay.textContent = "Idle";
};