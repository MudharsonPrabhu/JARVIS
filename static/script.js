const API_BASE_URL = "https://printers-generic-cooler-arch.trycloudflare.com/";

let isListening = false;
let recognition = null;
let currentUtterance = null;
let controller;

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

  if (isListening || synth.speaking) {
    if (recognition) recognition.stop();
    if (synth.speaking) synth.cancel();
    isListening = false;
    micBtn.classList.remove("active");
    addLog("Speech/stt stopped.", "info");
    document.getElementById("response-text").textContent = "🛑 Stopped.";
    return;
  }

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
      const res = await fetch(`${API_BASE_URL}/process`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      });

      const data = await res.json();
      document.getElementById("response-text").textContent = data.reply;
      addLog(data.reply, "jarvis");

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

document.getElementById("textInput").addEventListener("keydown", async (e) => {
  if (e.key === "Enter") {
    const message = e.target.value.trim();
    if (!message) return;

    e.target.value = "";
    document.getElementById("response-text").textContent = `You typed: ${message}`;
    addLog(message, "user");

    try {
      const res = await fetch(`${API_BASE_URL}/process`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
      });

      const data = await res.json();
      document.getElementById("response-text").textContent = data.reply;
      addLog(data.reply, "jarvis");

      const utter = new SpeechSynthesisUtterance(data.reply);
      utter.pitch = 1.2;
      utter.rate = 1.0;
      window.speechSynthesis.speak(utter);
    } catch (err) {
      const errMsg = "Failed to process command";
      document.getElementById("response-text").textContent = errMsg;
      addLog(errMsg, "error");
    }
  }
});

function stopJarvis() {
  console.log("STOP clicked");

  fetch(`${API_BASE_URL}/cancel`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    }
  })
  .then(r => r.json())
  .then(d => console.log("Cancel response:", d))
  .catch(e => console.error("Cancel error", e));

  window.speechSynthesis.cancel();
  if (recognition) recognition.stop();
}

document.getElementById("cancelBtn").addEventListener("click", stopJarvis);

navigator.mediaDevices.getUserMedia({ audio: true }).catch(function(err) {
  console.log("Mic error: ", err);
});

function updateTimeAndDate() {
  const now = new Date();
  document.getElementById("time").textContent = now.toLocaleTimeString();
  document.getElementById("date").textContent = now.toLocaleDateString();
}

setInterval(updateTimeAndDate, 1000);
updateTimeAndDate();

navigator.getBattery?.().then(battery => {
  function updateBattery() {
    const level = Math.round(battery.level * 100);
    document.getElementById("battery").textContent = `🔋 Battery: ${level}%`;
  }
  updateBattery();
  battery.addEventListener('levelchange', updateBattery);
});

document.addEventListener('keydown', function(event) {
  if (event.code === 'Space' && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
    event.preventDefault();
    const micButton = document.querySelector('.mic-button');
    if (micButton) micButton.click();
  }
});





