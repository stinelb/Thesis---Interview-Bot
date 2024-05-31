// Establish WebSocket connection with the server
const socket = new WebSocket('wss://prod1.cheetah.imada.sdu.dk/:8861');

// Function to handle input submission
function executeScript() {
	const input = document.getElementById('input');
	socket.send(input.value);
	const conversationContainer = document.querySelector('.message-container');
	const serverResponseDiv = document.createElement('div');
	serverResponseDiv.classList.add('message-orange');
	serverResponseDiv.innerHTML = `<p class="message-content">${input.value}</p>`;
	conversationContainer.appendChild(serverResponseDiv);
	input.value = '';
}

// Handle messages received from the server
socket.onmessage = function (event) {
	const output = event.data;
	if (!lastIsBlue()) {
		// Add new message
		const conversationContainer = document.querySelector('.message-container');
		const serverResponseDiv = document.createElement('div');
		serverResponseDiv.classList.add('message-blue');
		serverResponseDiv.innerHTML = `<p class="message-content">${output}</p>`;
		conversationContainer.appendChild(serverResponseDiv);
	} else {
		// Update last message
		const conversationContainer = document.querySelector('.message-container');
		const lastChild = conversationContainer.lastElementChild;
		lastChild.children[0].innerHTML += output;
	}
};

// Log any errors that occur
socket.onerror = function (error) {
	console.error('WebSocket error:', error);
};

// Log when the WebSocket connection is closed
socket.onclose = function (event) {
	console.log('WebSocket connection closed:', event);
};

function lastIsBlue() {
	const conversationContainer = document.querySelector('.message-container');
	const lastChild = conversationContainer.lastElementChild;
	if (lastChild && lastChild.classList.contains('message-blue')) {
		return true
	} else {
		return false
	}
}
