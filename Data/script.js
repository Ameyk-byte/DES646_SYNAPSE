document.getElementById('send-btn').addEventListener('click', async () => {
    const userInput = document.getElementById('user-input').value;
    if (!userInput.trim()) return;

    // Append user's message to chat box
    const chatBox = document.getElementById('chat-box');
    chatBox.innerHTML += `<p><strong>You:</strong> ${userInput}</p>`;

    // Clear input field
    document.getElementById('user-input').value = '';

    // Send query to backend
    const response = await fetch('/process_query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userInput }),
    });

    const data = await response.json();

    // Append assistant's response to chat box
    chatBox.innerHTML += `<p><strong>Assistant:</strong> ${data.response}</p>`;
    chatBox.scrollTop = chatBox.scrollHeight; // Scroll to bottom
});