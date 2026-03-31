import { useState, useRef, useEffect } from 'react'
import './App.css'

function App() {
  const [messages, setMessages] = useState([{ text: "Connection ready! Just start typing or hit the voice button.", sender: "agent" }]);
  const [inputText, setInputText] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [status, setStatus] = useState("Online");
  
  const messagesEndRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages]);

  const sendMessage = async () => {
    if (!inputText.trim()) return;
    
    setMessages(prev => [...prev, { text: inputText, sender: "user" }]);
    const currentInput = inputText;
    setInputText("");
    setStatus("Thinking...");
    
    try {
      const formData = new URLSearchParams();
      formData.append('message', currentInput);
      
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData.toString()
      });
      
      if (!response.ok) throw new Error("Backend failed to respond");
      
      const data = await response.json();
      setMessages(prev => [...prev, { text: data.response, sender: "agent" }]);
    } catch (error) {
      console.error(error);
      setMessages(prev => [...prev, { text: "Error connecting to local AI Backend. Ensure the Python API is running on localhost:8000 before sending messages.", sender: "agent" }]);
    }
    setStatus("Online");
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      sendMessage();
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        await sendVoiceMessage(audioBlob);
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
      setStatus("Listening...");
    } catch (err) {
      console.error("Error accessing microphone:", err);
      alert("Could not access microphone.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
    }
    setIsRecording(false);
    setStatus("Thinking...");
  };

  const toggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  const sendVoiceMessage = async (audioBlob) => {
    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'record.webm');

      // We don't append text user message immediately since we don't know what they said yet.
      // We wait for the audio to be transcribed and processed by the backend.

      const response = await fetch('http://localhost:8000/api/voice-chat', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error("Voice endpoint failed");

      // The backend will return an mp3 file
      const blob = await response.blob();
      const audioUrl = URL.createObjectURL(blob);
      
      // Play the audio
      const audioObj = new Audio(audioUrl);
      audioObj.play();

      setMessages(prev => [...prev, { text: "[Voice Message Received]", sender: "user" }]);
      setMessages(prev => [...prev, { text: "[Voice Audio Responded]", sender: "agent" }]);
      
    } catch (error) {
      console.error(error);
      setMessages(prev => [...prev, { text: "Error connecting to AI Backend for Voice.", sender: "agent" }]);
    }
    setStatus("Online");
  };

  return (
    <div className="app-container">
      <div className="chat-box">
        
        <div className="chat-header">
          <h1>Nexus AI Voice Agent</h1>
          <span className="status">{status}</span>
        </div>

        <div className="visualizer-container">
          <div className={`orb ${isRecording || status === "Thinking..." ? 'listening' : ''}`}></div>
        </div>

        <div className="messages">
          {messages.map((msg, index) => (
            <div key={index} className={`message ${msg.sender}`}>
              {msg.text}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-area">
          <button 
           className={`btn-voice ${isRecording ? 'active' : ''}`}
           onClick={toggleRecording}
           title="Toggle Voice Mode">
            {isRecording ? '⏹' : '🎤'}
          </button>
          <input 
            type="text" 
            placeholder="Type a message..." 
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={handleKeyPress}
          />
          <button onClick={sendMessage}>Send</button>
        </div>

      </div>
    </div>
  )
}

export default App
