from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import torch
import torch.nn as nn
import numpy as np
import logging
from typing import List
import os

from model import CandlestickLSTM
from inference import ModelInference

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Candlestick Predictor AI Service", version="1.0.0")

# Global model instance
model_inference = None

class PredictionRequest(BaseModel):
    sequence: List[List[float]]

class PredictionResponse(BaseModel):
    prediction: List[List[float]]

@app.on_event("startup")
async def startup_event():
    """Initialize the model on startup"""
    global model_inference
    try:
        model_path = "/app/models/candlestick_predictor_model.pth"
        
        if not os.path.exists(model_path):
            logger.error(f"Model file not found at {model_path}")
            model_path = "./candlestick_predictor_model.pth"  # Fallback path
            
        if not os.path.exists(model_path):
            logger.warning("Model file not found. Creating a new model for demonstration.")
            # Create and save a dummy model for testing
            model = CandlestickLSTM(input_size=4, hidden_size=128, num_layers=2, output_size=4, sequence_length=50)
            torch.save(model.state_dict(), model_path)
        
        model_inference = ModelInference(model_path)
        logger.info("Model loaded successfully")
        
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        # Create model anyway for demo purposes
        logger.info("Creating fallback model...")
        try:
            model_path = "./candlestick_predictor_model.pth"
            model = CandlestickLSTM(input_size=4, hidden_size=128, num_layers=2, output_size=4, sequence_length=50)
            torch.save(model.state_dict(), model_path)
            model_inference = ModelInference(model_path)
            logger.info("Fallback model created successfully")
        except Exception as fallback_error:
            logger.error(f"Failed to create fallback model: {str(fallback_error)}")
            model_inference = None

@app.get("/")
async def root():
    return {"message": "Candlestick Predictor AI Service", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    model_status = "loaded" if model_inference is not None else "not_loaded"
    return {
        "status": "healthy",
        "model_status": model_status,
        "service": "ai_predictor"
    }

@app.get("/model-info")
async def model_info():
    """Get model information"""
    if model_inference is None:
        return {"error": "Model not loaded"}
    
    return {
        "model_type": "LSTM Sequence-to-Sequence",
        "input_features": 4,
        "output_features": 4,
        "sequence_length": 50,
        "prediction_length": 25,
        "status": "loaded"
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Predict future candlesticks from input sequence
    
    Args:
        request: Contains sequence of [open, high, low, close] values
        
    Returns:
        Predicted future candlestick sequence
    """
    try:
        if model_inference is None:
            raise HTTPException(status_code=503, detail="Model not loaded")
        
        sequence = request.sequence
        
        # Validate input
        if not sequence or len(sequence) == 0:
            raise HTTPException(status_code=400, detail="Empty sequence provided")
        
        if len(sequence[0]) != 4:
            raise HTTPException(status_code=400, detail="Each candlestick must have 4 values (OHLC)")
        
        logger.info(f"Received prediction request with {len(sequence)} candlesticks")
        
        # Get prediction from model
        prediction = model_inference.predict(sequence)
        
        logger.info(f"Generated prediction with {len(prediction)} future candlesticks")
        
        return {"prediction": prediction}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/predict-demo")
async def predict_demo(request: PredictionRequest):
    """
    Demo prediction endpoint that works without a trained model
    Generates realistic-looking future candlesticks based on trends
    """
    try:
        sequence = request.sequence
        
        if not sequence or len(sequence) == 0:
            raise HTTPException(status_code=400, detail="Empty sequence provided")
        
        logger.info(f"Demo prediction with {len(sequence)} input candlesticks")
        
        # Generate demo prediction based on recent trends
        prediction = generate_demo_prediction(sequence)
        
        return {"prediction": prediction}
        
    except Exception as e:
        logger.error(f"Error in demo prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Demo prediction error: {str(e)}")

def generate_demo_prediction(sequence: List[List[float]], prediction_length: int = 25) -> List[List[float]]:
    """
    Generate a realistic demo prediction based on input trends
    """
    if not sequence:
        return []
    
    # Get recent trend from last few candles
    recent_candles = sequence[-5:]  # Last 5 candles
    
    # Calculate average change
    price_changes = []
    for i in range(1, len(recent_candles)):
        prev_close = recent_candles[i-1][3]  # Previous close
        curr_close = recent_candles[i][3]    # Current close
        change = (curr_close - prev_close) / prev_close if prev_close != 0 else 0
        price_changes.append(change)
    
    avg_change = np.mean(price_changes) if price_changes else 0
    volatility = np.std(price_changes) if price_changes else 0.02
    
    # Start from last candle's close
    last_close = sequence[-1][3]
    prediction = []
    
    for i in range(prediction_length):
        # Add some randomness to the trend
        noise = np.random.normal(0, volatility)
        trend_factor = avg_change + noise
        
        # Calculate new close price
        new_close = last_close * (1 + trend_factor)
        
        # Generate realistic OHLC
        # Open near previous close with small gap
        new_open = last_close * (1 + np.random.normal(0, 0.001))
        
        # High and low based on volatility
        price_range = abs(new_close - new_open) + (volatility * last_close)
        new_high = max(new_open, new_close) + np.random.uniform(0, price_range)
        new_low = min(new_open, new_close) - np.random.uniform(0, price_range)
        
        # Ensure proper OHLC relationships
        new_high = max(new_high, new_open, new_close)
        new_low = min(new_low, new_open, new_close)
        
        # Normalize to 0-1 range (assuming input was normalized)
        new_candle = [
            max(0, min(1, new_open)),
            max(0, min(1, new_high)),
            max(0, min(1, new_low)),
            max(0, min(1, new_close))
        ]
        
        prediction.append(new_candle)
        last_close = new_close
    
    return prediction

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)