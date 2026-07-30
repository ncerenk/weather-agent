const chatBox = document.getElementById("chat-box");
const messageInput = document.getElementById("message");
const sendButton = document.getElementById("send-btn");

let currentUser = null;

function addMessage(sender, message) {

    const wrapper = document.createElement("div");

    wrapper.className =
        sender === "Sen"
            ? "message user"
            : "message bot";

    const bubble = document.createElement("div");

    bubble.className = "bubble";

    bubble.innerHTML = marked.parse(message);

    wrapper.appendChild(bubble);

    chatBox.appendChild(wrapper);

    chatBox.scrollTop = chatBox.scrollHeight;
}

sendButton.addEventListener("click", sendMessage);

messageInput.addEventListener("keypress", function (event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});

async function sendMessage() {

    const message = messageInput.value.trim();

    if (message === "") return;

    addMessage("Sen", message);

    messageInput.value = "";

    const response = await fetch("/chat", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({

            message: message,

            current_user: currentUser

        })

    });

    const data = await response.json();

    currentUser = data.current_user;

    document.getElementById("input-tokens").textContent =
        data.input_tokens;

    document.getElementById("output-tokens").textContent =
        data.output_tokens;

    document.getElementById("total-tokens").textContent =
        data.total_tokens;

    addMessage("Bot", data.response);

}