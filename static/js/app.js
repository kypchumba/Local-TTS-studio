
const textInput = document.getElementById("textInput");
const counter = document.getElementById("counter");
const voiceSelect = document.getElementById("voiceSelect");
const speedRange = document.getElementById("speedRange");
const speedValue = document.getElementById("speedValue");
const generateBtn = document.getElementById("generateBtn");
const message = document.getElementById("message");
const audioPanel = document.getElementById("audioPanel");
const audioPlayer = document.getElementById("audioPlayer");
const downloadLink = document.getElementById("downloadLink");

// Character counter
textInput.addEventListener("input", () => {
    counter.textContent =
        `${textInput.value.length.toLocaleString()} characters`;
});

// Speaking speed display
speedRange.addEventListener("input", () => {
    speedValue.textContent =
        `${Number(speedRange.value).toFixed(2)}x`;
});

// Load available voices
async function loadVoices() {
    try {
        const response = await fetch("/api/voices");
        const data = await response.json();

        voiceSelect.innerHTML = "";

        data.voices.forEach(voice => {
            const option = document.createElement("option");

            option.value = voice;
            option.textContent = voice.replaceAll("_", " ");

            voiceSelect.appendChild(option);
        });

        voiceSelect.value = "af_heart";

    } catch (error) {
        message.textContent = "Could not load voices.";
    }
}

// Generate narration
generateBtn.addEventListener("click", async () => {
    const text = textInput.value.trim();

    if (!text) {
        message.textContent = "Please enter some text first.";
        return;
    }

    generateBtn.disabled = true;
    generateBtn.textContent = "Generating...";
    message.textContent = "Generating your narration. Please wait...";
    audioPanel.style.display = "none";

    try {
        const response = await fetch("/api/generate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                text,
                voice: voiceSelect.value,
                speed: Number(speedRange.value)
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Generation failed.");
        }

        audioPlayer.src = data.audio_url;
        downloadLink.href = data.audio_url;

        audioPanel.style.display = "block";

        message.textContent =
            `Generated successfully · ${data.duration}s · ${data.sample_rate} Hz`;

        audioPlayer.load();

    } catch (error) {
        message.textContent = error.message;

    } finally {
        generateBtn.disabled = false;
        generateBtn.textContent = "Generate narration";
    }
});

// Initialize
loadVoices();
