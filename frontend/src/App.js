import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './App.css';


function App() {
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);


const scrollToBottom = () => {
  messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
};




  const exampleQuestions = [
    "Which members have the highest cancellation rate?",
    "How much revenue did we lose to weather cancellations in December?",
    "Which coaches generate the most revenue?",
    "Show me the top 5 members by total bookings",
    "What's the average revenue per booking?"
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!question.trim()) return;

    const userMessage = {type: 'user', text: question};
    setMessages(prev => [...prev, userMessage]);
    setQuestion('');
    setLoading(true);

    try {
      const response = await axios.post('https://courtiq-6pe7.onrender.com', {
  question: question,
  history: messages.map(msg => ({
    question: msg.type === 'user' ? msg.text : null,
    answer: msg.type === 'assistant' ? msg.text : null
  }))
});

      const assistantMessage = {
        type: 'assistant',
        text: response.data.answer,
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage = {
        type: 'assistant',
        text: "I'm having trouble understanding that question. Could you rephrase it or ask something about members, bookings, coaches, or revenue?"
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
      setTimeout(() => {
        const input = document.querySelector('.input');
        if (input) input.focus();
      }, 300);
    }
  };

  const handleExampleClick = (exampleQuestion) => {
    setQuestion(exampleQuestion);
  };

  return (
    <div className="App">
      <div className="container">
        <header className="header">
          <h1>🎾 CourtIQ</h1>
          <p>AI Assistant for Tennis Club Analytics</p>
          <a href="/admin" style={{color: 'white', marginTop: '10px', display: 'inline-block', textDecoration: 'underline'}}>
    Admin Panel →
  </a>
        </header>





        <div className="chat-container">
          {messages.length === 0 ? (
            <div className="welcome">
              <h2>Welcome to CourtIQ</h2>
              <p>Ask questions about your tennis club in natural language</p>
              <div className="examples">
                <h3>Try these examples:</h3>
                {exampleQuestions.map((q, i) => (
                  <button
                    key={i}
                    className="example-btn"
                    onClick={() => handleExampleClick(q)}
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="messages">
              {messages.map((msg, i) => (
                <div key={i} className={`message ${msg.type}`}>
                  <div className="message-content">
                    {msg.text}
                  </div>
                </div>
              ))}
              {loading && (
                <div className="message assistant">
                  <div className="message-content loading">
                    <span>Thinking</span>
                    <span className="dots">...</span>
                  </div>
                </div>
             )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        <form onSubmit={handleSubmit} className="input-form">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question about your tennis club..."
            disabled={loading}
            className="input"
          />
          <button type="submit" disabled={loading || !question.trim()} className="submit-btn">
            Send
          </button>
        </form>
      </div>
    </div>
  );
}

export default App;
