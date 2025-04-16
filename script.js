const chatBox = document.getElementById("chatBox");
const messageInput = document.getElementById("messageInput");
const locationInput = document.getElementById("locationInput");

function appendMessage(sender, message) {
  const msgDiv = document.createElement("div");
  msgDiv.innerHTML = `<strong>${sender}:</strong> ${message}`;
  msgDiv.classList.add("mb-2");
  chatBox.appendChild(msgDiv);
  chatBox.scrollTop = chatBox.scrollHeight;

 
  let structuredHistory = JSON.parse(localStorage.getItem("structuredChat") || "[]");
  structuredHistory.push({ sender, message, timestamp: new Date().toISOString() });
  localStorage.setItem("structuredChat", JSON.stringify(structuredHistory));


  localStorage.setItem("chatHistory", chatBox.innerHTML);


  if (sender === "Event Genie") {
    const utterance = new SpeechSynthesisUtterance(message);
    utterance.lang = "en-US";
    speechSynthesis.speak(utterance);
  }
}

function saveChat() {
  localStorage.setItem("chatHistory", chatBox.innerHTML);
}

function loadChat() {
  const structuredHistory = JSON.parse(localStorage.getItem("structuredChat") || "[]");
  chatBox.innerHTML = "";
  structuredHistory.forEach(({ sender, message }) => {
    const msgDiv = document.createElement("div");
    msgDiv.innerHTML = `<strong>${sender}:</strong> ${message}`;
    msgDiv.classList.add("mb-2");
    chatBox.appendChild(msgDiv);
  });
  chatBox.scrollTop = chatBox.scrollHeight;
}

function startNewChat() {
  chatBox.innerHTML = "";
  localStorage.removeItem("chatHistory");
  localStorage.removeItem("structuredChat");
  updateHistorySidebar();
}

function updateHistorySidebar() {
  const historySidebar = document.getElementById("chatHistorySidebar");
  historySidebar.innerHTML = "";

  const structuredHistory = JSON.parse(localStorage.getItem("structuredChat") || "[]");

  structuredHistory
    .filter(msg => msg.sender === "You")
    .forEach((msg, i) => {
      const div = document.createElement("div");
      div.classList.add("history-item", "p-2", "border", "mb-1", "bg-light");
      div.textContent = msg.message.substring(0, 40) + "...";
      div.onclick = () => {
        loadChat(); 
      };
      historySidebar.appendChild(div);
    });
}

window.onload = () => {
  loadChat();
  updateHistorySidebar(); 
};
function toggleHistorySidebar() {
  const sidebar = document.getElementById("historySidebar");
  if (sidebar.style.display === "none" || !sidebar.style.display) {
    sidebar.style.display = "block";
    updateHistorySidebar();
  } else {
    sidebar.style.display = "none";
  }
}


 

function toggleDarkMode() {
  document.body.classList.toggle("bg-dark");
  document.body.classList.toggle("text-white");
  chatBox.classList.toggle("bg-white");
  chatBox.classList.toggle("bg-dark");
  chatBox.classList.toggle("text-white");
}
function clearChat() {
  chatBox.innerHTML = "";
  localStorage.removeItem("chatHistory");
}

function startVoiceInput() {
  const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
  recognition.lang = "en-US";
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  recognition.start();

  recognition.onresult = function (event) {
    const transcript = event.results[0][0].transcript;
    messageInput.value = transcript;
    sendMessage();
  };

  recognition.onerror = function (event) {
    console.error("Speech recognition error:", event.error);
    alert("🎙️ Error using voice input. Try again.");
  };
}


async function sendMessage() {
  const userMessage = messageInput.value.trim();
  const location = locationInput.value.trim();

  if (!userMessage) return;

  appendMessage("You", userMessage);
  messageInput.value = "";

  try {
    const response = await fetch("http://localhost:8000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: userMessage, location }),
    });

    const data = await response.json();
    appendMessage("Event Genie", data.response);
  } catch (err) {
    appendMessage("Event Genie", "Sorry, there was an error fetching the response.");
  }
}
