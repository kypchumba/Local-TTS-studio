
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

// Voice library elements
const voiceGrid = document.getElementById("voiceGrid");
const voiceCount = document.getElementById("voiceCount");
const languageFilter = document.getElementById("languageFilter");
const genderFilter = document.getElementById("genderFilter");
const selectedVoice = document.getElementById("selectedVoice");
const previewPlayer = document.getElementById("previewPlayer");

let voices = [];
let currentVoice = "af_heart";

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

// Load voice library
async function loadVoices() {
    try {
        const response = await fetch("/api/voice-library");

        if (!response.ok) {
            throw new Error("Could not retrieve voice library.");
        }

        const data = await response.json();

        if (!data.success || !Array.isArray(data.voices)) {
            throw new Error("Invalid voice library response.");
        }

        voices = data.voices;

        // Populate language filter
        const languages = [...new Set(
            voices.map(voice => voice.language)
        )].sort();

        languages.forEach(language => {
            const option = document.createElement("option");
            option.value = language;
            option.textContent = language;
            languageFilter.appendChild(option);
        });

        // Set default voice
        if (!voices.some(voice => voice.id === currentVoice)) {
            currentVoice = voices[0]?.id || "";
        }

        voiceSelect.value = currentVoice;
        updateSelectedVoice();
        renderVoices();

    } catch (error) {
        console.error("Voice library error:", error);
        voiceCount.textContent = "Unavailable";
        voiceGrid.textContent = error.message;
    }
}

// Render voice cards
function renderVoices() {
    const language = languageFilter.value;
    const gender = genderFilter.value;

    const filteredVoices = voices.filter(voice => {
        const matchesLanguage =
            language === "all" || voice.language === language;

        const matchesGender =
            gender === "all" || voice.gender === gender;

        return matchesLanguage && matchesGender;
    });

    voiceGrid.innerHTML = "";

    voiceCount.textContent =
        `${filteredVoices.length} voices`;

    if (!filteredVoices.length) {
        voiceGrid.textContent = "No voices match these filters.";
        return;
    }

    filteredVoices.forEach(voice => {
        const card = document.createElement("div");

        card.className = "voice-card";

        if (voice.id === currentVoice) {
            card.classList.add("selected");
        }

        const top = document.createElement("div");
        top.className = "voice-card-top";

        const details = document.createElement("div");

        const name = document.createElement("strong");
        name.textContent = voice.name;

        const meta = document.createElement("div");
        meta.className = "voice-meta";
        meta.textContent = `${voice.language} · ${voice.gender}`;

        details.append(name, meta);
        top.appendChild(details);

        const actions = document.createElement("div");
        actions.className = "voice-actions";

        const previewButton = document.createElement("button");
        previewButton.className = "preview-btn";
        previewButton.textContent = "▶ Preview";
        previewButton.dataset.action = "preview";
        previewButton.dataset.voice = voice.id;

        const selectButton = document.createElement("button");
        selectButton.className = "select-btn";
        selectButton.textContent =
            voice.id === currentVoice ? "Selected ✓" : "Select";

        selectButton.dataset.action = "select";
        selectButton.dataset.voice = voice.id;

        actions.append(previewButton, selectButton);
        card.append(top, actions);

        voiceGrid.appendChild(card);
    });
}

// Update selected voice display
function updateSelectedVoice() {
    const voice = voices.find(item => item.id === currentVoice);

    voiceSelect.value = currentVoice;
    selectedVoice.textContent = voice
        ? `${voice.name} · ${voice.language}`
        : currentVoice;
}

// Filter listeners
languageFilter.addEventListener("change", renderVoices);
genderFilter.addEventListener("change", renderVoices);

// Voice card actions
voiceGrid.addEventListener("click", async (event) => {
    const button = event.target.closest("button[data-action]");

    if (!button) return;

    const voiceId = button.dataset.voice;
    const action = button.dataset.action;

    if (action === "select") {
        currentVoice = voiceId;

        updateSelectedVoice();
        renderVoices();

        return;
    }

    if (action === "preview") {
        const originalText = button.textContent;

        button.disabled = true;
        button.textContent = "Loading...";

        try {
            const response = await fetch("/api/preview", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    voice: voiceId,
                    speed: Number(speedRange.value)
                })
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(data.error || "Preview failed.");
            }

            previewPlayer.pause();
            previewPlayer.src = data.audio_url;
            previewPlayer.load();

            await previewPlayer.play();

        } catch (error) {
            console.error("Preview error:", error);
            message.textContent = error.message;

        } finally {
            button.disabled = false;
            button.textContent = originalText;
        }
    }
});

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
