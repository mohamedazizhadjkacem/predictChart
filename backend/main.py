from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

import uvicorn
import numpy as np
import cv2
from PIL import Image
import io
import base64
from typing import List
import json
import logging
from pydantic import BaseModel


from image_to_numeric import image_to_numeric
from numeric_to_image import numeric_to_image
from ai_client import AIClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Candlestick Predictor Backend", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI client
ai_client = AIClient("http://ai:8001")

class NumericData(BaseModel):
    numeric: List[List[float]]

class PredictionResponse(BaseModel):
    future: List[List[float]]

@app.get("/")
async def root():
    return {"message": "Candlestick Predictor Backend API", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check AI service connectivity
        ai_status = await ai_client.health_check()
        return {
            "status": "healthy",
            "backend": "running",
            "ai_service": "connected" if ai_status else "disconnected"
        }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "error": str(e)
        }

@app.post("/convert-image-to-numeric")
async def convert_image_to_numeric_endpoint(file: UploadFile = File(...)):
    """Convert uploaded image to numeric candlestick data"""
    try:
        # Read image file
        contents = await file.read()
        
        # Convert to numpy array
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # Convert image to numeric data
        numeric_data = image_to_numeric(img)
        
        logger.info(f"Converted image to {len(numeric_data)} candlesticks")
        
        return {"numeric": numeric_data}
        
    except Exception as e:
        logger.error(f"Error converting image to numeric: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.post("/predict", response_model=PredictionResponse)
async def predict_endpoint(data: NumericData):
    """Send numeric data to AI service for prediction"""
    try:
        # Send data to AI service
        prediction = await ai_client.predict(data.numeric)
        
        logger.info(f"Received prediction with {len(prediction)} future candlesticks")
        
        return {"future": prediction}
        
    except Exception as e:
        logger.error(f"Error getting prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting prediction: {str(e)}")

@app.post("/reconstruct-image")
async def reconstruct_image_endpoint(data: NumericData):
    """Convert numeric data back to image"""
    try:
        # Convert numeric to image
        img = numeric_to_image(data.numeric)
        
        # Convert PIL image to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        return StreamingResponse(
            io.BytesIO(img_byte_arr.getvalue()),
            media_type="image/png",
            headers={"Content-Disposition": "inline; filename=reconstructed.png"}
        )
        
    except Exception as e:
        logger.error(f"Error reconstructing image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error reconstructing image: {str(e)}")

@app.post("/full-process")
async def full_process_endpoint(file: UploadFile = File(...)):
    """Complete pipeline: image -> numeric -> prediction -> concatenated image"""
    try:
        # Step 1: Read and convert image to numeric
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        original_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if original_img is None:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # Convert to numeric data
        numeric_data = image_to_numeric(original_img)
        logger.info(f"Converted image to {len(numeric_data)} candlesticks")
        
        # Step 2: Get prediction from AI service
        prediction = await ai_client.predict(numeric_data)
        logger.info(f"Received prediction with {len(prediction)} future candlesticks")
        
        # Step 3: Convert prediction to image
        predicted_img = numeric_to_image(prediction, width=342, height=817)
        
        # Step 4: Convert original image to PIL for concatenation
        original_pil = Image.fromarray(cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB))
        
        # Ensure original image is correct size (1025x817)
        original_pil = original_pil.resize((1025, 817))
        
        # Step 5: Concatenate images horizontally
        total_width = original_pil.width + predicted_img.width
        combined_img = Image.new('RGB', (total_width, 817), 'white')
        
        # Paste images
        combined_img.paste(original_pil, (0, 0))
        combined_img.paste(predicted_img, (original_pil.width, 0))
        
        # Convert to bytes for response
        img_byte_arr = io.BytesIO()
        combined_img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        logger.info("Successfully processed full pipeline")
        
        return StreamingResponse(
            io.BytesIO(img_byte_arr.getvalue()),
            media_type="image/png",
            headers={"Content-Disposition": "inline; filename=prediction_result.png"}
        )
        
    except Exception as e:
        logger.error(f"Error in full process: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in full process: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
