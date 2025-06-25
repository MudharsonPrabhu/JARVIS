let isListening = false;
let recognition = null;
let currentUtterance = null;

function addLog(message, type = "info") {
  const logContainer = document.getElementById("logs");
  const logEntry = document.createElement("div");
  logEntry.classList.add("log-entry", type);

  const iconMap = {
    user: "🗣️",
    jarvis: "🤖",
    error: "❌",
    info: "📢"
  };

  logEntry.innerHTML = `<span class="log-time">[${new Date().toLocaleTimeString()}]</span> ${iconMap[type] || ""} ${message}`;
  logContainer.appendChild(logEntry);
  logContainer.scrollTop = logContainer.scrollHeight;
}

function toggleMic() {
  const micBtn = document.querySelector('.mic-button');
  const synth = window.speechSynthesis;

  // Stop if already listening or speaking
  if (isListening || synth.speaking) {
    if (recognition) recognition.stop();
    if (synth.speaking) synth.cancel();
    isListening = false;
    micBtn.classList.remove("active"); // Optional: visual cue
    addLog("Speech/stt stopped.", "info");
    document.getElementById("response-text").textContent = "🛑 Stopped.";
    return;
  }

  // Start listening
  recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
  recognition.lang = 'en-US';
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  recognition.onstart = () => {
    isListening = true;
    micBtn.classList.add("active");
    document.getElementById("response-text").textContent = "🎙️ Listening...";
    addLog("Listening started...", "info");
  };

  recognition.onresult = async (event) => {
    const text = event.results[0][0].transcript;
    document.getElementById("response-text").textContent = `You said: ${text}`;
    addLog(text, "user");

    try {
      const res = await fetch('http://localhost:5000/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      });

      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(errorText);
      }

      const data = await res.json();
      document.getElementById("response-text").textContent = data.reply;
      addLog(data.reply, "jarvis");

      // Speak response
      currentUtterance = new SpeechSynthesisUtterance(data.reply);
      currentUtterance.pitch = 1.2;
      currentUtterance.rate = 1.0;
      synth.speak(currentUtterance);
    } catch (error) {
      const errMsg = `Server error: ${error.message}`;
      document.getElementById("response-text").textContent = errMsg;
      addLog(errMsg, "error");
    }
  };

  recognition.onerror = (event) => {
    const errMsg = `Recognition error: ${event.error}`;
    document.getElementById("response-text").textContent = errMsg;
    addLog(errMsg, "error");
  };

  recognition.onend = () => {
    isListening = false;
    micBtn.classList.remove("active");
    addLog("Listening ended. Tap mic to restart.", "info");
  };

  recognition.start();
}


  const bgAudio = document.getElementById("bg-audio");
  const audioBtn = document.querySelector(".audio-toggle");

  function toggleAudio() {
    if (!bgAudio) return;

    // If muted, unmute and play
    if (bgAudio.muted) {
      bgAudio.muted = false;
      bgAudio.volume = 0.1;
      bgAudio.play().catch(e => {
        console.warn("Play failed:", e);
      });
      audioBtn.textContent = "🔈";
    } else {
      bgAudio.muted = true;
      audioBtn.textContent = "🔇";
    }
  }

  window.addEventListener("DOMContentLoaded", () => {
    if (bgAudio) {
      bgAudio.volume = 0.2;
      bgAudio.muted = true;
    }
  });

