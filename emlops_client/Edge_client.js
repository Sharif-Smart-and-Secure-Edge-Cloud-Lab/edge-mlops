const mqtt = require('mqtt');
const fs = require('fs');
const path = require('path');
const net = require('net'); // Import the 'net' module
const mongoose = require("mongoose"); 

// MQTT broker information
const mqttBroker = 'mqtt://127.0.0.1';
const mqttTopic = 'temperature';

// Socket server information (Server IP and Port)
const serverHost = '127.0.0.1'; // Replace with your server's IP address
const serverPort = 8080; // Replace with your desired port

// Initialize the MQTT client
const mqttClient = mqtt.connect(mqttBroker);

// Initialize the TCP socket client
const socketClient = new net.Socket();

// Callback function for MQTT connection
mqttClient.on('connect', () => {
  console.log('Connected to MQTT broker');
  
  // Subscribe to the MQTT topic
  mqttClient.subscribe(mqttTopic, (err) => {
    if (err) {
      console.error('Error subscribing to MQTT topic:', err);
    } else {
      console.log('Subscribed to MQTT topic');
    }
  });
});

mongoose.connect('mongodb://127.0.0.1:27017/Edge_MLOps',{
  useNewUrlParser: true,
  useUnifiedTopology: true
}).then(db => console.log('connected to db')).catch(err => console.log(err))

const messageSchema = new mongoose.Schema({
  title : {type: String , required: true},
  description :  {type: String , required: true},
  date: {type: Date , default: Date.now}
})

const Message = mongoose.model('Message',messageSchema);
async function createMessage(title,description){
  const message = new Message({
      title: title,
      description : description
  });
  const result = await message.save();
  console.log(result);
}

// Callback function for receiving MQTT messages
mqttClient.on('message', (topic, message) => {
  console.log(`Received message on topic ${topic}: ${message}`);
  createMessage(topic,message);
  // Handle the received message (e.g., process data or files)
  // You can add your logic here
  
  // Example: Saving a received file
//  const receivedFileName = 'received-file.txt';
//  const filePath = path.join(__dirname, receivedFileName);
//  fs.writeFile(filePath, message, (err) => {
//    if (err) {
//      console.error('Error saving received file:', err);
//    } else {
//      console.log(`Saved received file as ${receivedFileName}`);
//      
//      // After saving the file, send it to the server using the socket
//      sendDataToServer(filePath);
//    }
//  });
});

// Function to send data to the server using the socket
function sendDataToServer(dataFilePath) {
  // Connect to the server
  socketClient.connect(serverPort, serverHost, () => {
    console.log('Connected to server via socket');
    
    // Read data from the file
    const data = fs.readFileSync(dataFilePath, 'utf8');
    
    // Send data to the server
    socketClient.write(data);
  });
}

// Socket client event handlers
socketClient.on('data', (data) => {
  console.log('Received data from server:', data.toString());
  // Handle data received from the server as needed
});

socketClient.on('close', () => {
  console.log('Socket connection with server closed');
  // Add any necessary cleanup or reconnection logic here
});
