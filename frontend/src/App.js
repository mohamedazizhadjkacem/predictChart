import React from 'react';
import './App.css';
import CandlestickPredictor from './components/CandlestickPredictor';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>🔮 Candlestick Chart Predictor</h1>
        <p>Upload a candlestick chart image to get AI-powered future predictions</p>
      </header>
      
      <main className="App-main">
        <CandlestickPredictor />
      </main>
      
      <footer className="App-footer">
        <p>Powered by LSTM Neural Networks • React + FastAPI + PyTorch</p>
      </footer>
      
      <ToastContainer 
        position="top-right"
        autoClose={5000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
      />
    </div>
  );
}

export default App;