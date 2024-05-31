const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const { spawn } = require('child_process');
const path = require('path');

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

let pythonProcess;

app.use(express.static(path.join(__dirname, 'public')));

wss.on('connection', (ws) => {
	console.log('Client connected');

	if (!pythonProcess) {
		startPythonScript();
	}
	
	ws.on('message', (message) => {
		const userInput = message.toString().replace(/\n/g, " ").trim()+"\n";
		console.log(userInput);
		if (!pythonProcess) {
			startPythonScript()
		}
		pythonProcess.stdin.write(userInput);
	});
	ws.on('close', (stream) => {
		pythonProcess.kill()
	})
});

function startPythonScript() {
	pythonProcess = spawn('python3', ['cript.py']);

	pythonProcess.stdout.on('data', (data) => {
		const output = data.toString();
		wss.clients.forEach((client) => {
			if (client.readyState === WebSocket.OPEN) {
				client.send(output);
			}
		});
	});

	pythonProcess.stderr.on('data', (data) => {
		console.error(`Error: ${data}`);
	});

	pythonProcess.on('close', (code) => {
		console.log(`Python script exited with code ${code}`);
		pythonProcess = null;
	});
}

server.listen(8861, "0.0.0.0", () => {
	console.log('Server is running on http://localhost:8861');
	console.log('Server is running on http://prod1.cheetah.imada.sdu.dk/');
});
