from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import uvicorn
import httpx
import json
import matplotlib.pyplot as plt

import matplotlib.patches as patches
import io
import numpy as np
from PIL import Image
import cv2
import torch
import os
from image_to_numeric import image_to_numeric, validate_numeric_data
from numeric_to_image import numeric_to_image, create_candlestick_chart_advanced

app = FastAPI(title="Candlestick Predictor Backend - Test", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AI_SERVICE_URL = "http://localhost:8001"

def reconstruct_candlestick_image(numeric_data, img_width=600, img_height=200):
    """
    Create a professional candlestick chart from numeric data using matplotlib
    """
    if not numeric_data:
        # Return blank white image if no data
        fig, ax = plt.subplots(figsize=(img_width/100, img_height/100))
        ax.text(0.5, 0.5, 'No Data', ha='center', va='center', transform=ax.transAxes)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        plt.close()
        buf.seek(0)
        img_array = plt.imread(buf)
        buf.close()
        return (img_array * 255).astype(np.uint8)
    
    # Create matplotlib figure
    fig, ax = plt.subplots(figsize=(img_width/100, img_height/100))
    
    # Remove margins and axes for clean look
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    # Find price range for scaling
    all_values = [val for candle in numeric_data for val in candle]
    min_val = min(all_values)
    max_val = max(all_values)
    val_range = max_val - min_val if max_val > min_val else 0.1
    
    # Add some padding to the price range
    padding = val_range * 0.1
    ax.set_ylim(min_val - padding, max_val + padding)
    ax.set_xlim(-0.5, len(numeric_data) - 0.5)
    
    # Draw candlesticks
    for i, (o, h, l, c) in enumerate(numeric_data):
        # Determine candle color
        color = '#26a69a' if c >= o else '#ef5350'  # Green for bullish, red for bearish
        
        # Draw high-low line (wick)
        ax.plot([i, i], [l, h], color='black', linewidth=1, alpha=0.8)
        
        # Draw candle body
        body_height = abs(c - o)
        body_bottom = min(o, c)
        
        if body_height > 0:
            # Draw rectangle for candle body
            rect = plt.Rectangle((i - 0.3, body_bottom), 0.6, body_height, 
                               facecolor=color, edgecolor='black', linewidth=0.5, alpha=0.8)
            ax.add_patch(rect)
        else:
            # Doji candle (open == close)
            ax.plot([i - 0.3, i + 0.3], [o, o], color='black', linewidth=2)
    
    # Convert to numpy array
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100, 
                facecolor='white', edgecolor='none', pad_inches=0)
    plt.close()
    buf.seek(0)
    
    # Convert to grayscale for consistency with original
    img_pil = Image.open(buf)
    img_gray = img_pil.convert('L')
    img_array = np.array(img_gray)
    buf.close()
    
    return img_array

def create_candlestick_comparison(past_sequence, actual_future, predicted_future, title="Candlestick Prediction Comparison"):
    """
    Create visualization showing input data and AI predictions
    """
    # Only show: Input (past_sequence) and Predicted (predicted_future) 
    # actual_future parameter is ignored as it's not meaningful
    
    # Create single plot showing input + predictions
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    fig.suptitle(title, fontsize=16, fontweight='bold')
    
    # Calculate proper proportional scaling
    # If we have both input and predictions, scale them proportionally
    input_len = len(past_sequence)
    pred_len = len(predicted_future)
    
    if input_len == 0 and pred_len == 0:
        ax.text(0.5, 0.5, 'No Data Available', ha='center', va='center', transform=ax.transAxes)
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        plt.close()
        img_buffer.seek(0)
        return img_buffer
    
    # Calculate proportional widths (prediction should be ~25% or more)
    if pred_len > 0:
        # Ensure predictions get at least 25% of the visual space
        min_pred_ratio = 0.25
        actual_ratio = pred_len / (input_len + pred_len) if (input_len + pred_len) > 0 else 0.5
        target_ratio = max(min_pred_ratio, actual_ratio)
        
        # Scale the timeline to give predictions proper visual weight
        visual_input_len = input_len
        visual_pred_len = max(pred_len, input_len * target_ratio / (1 - target_ratio))
        
        # Create position mapping for visual spacing
        input_positions = list(range(input_len))
        pred_start = input_len + 2  # Add gap between sections
        pred_positions = [pred_start + i * (visual_pred_len / pred_len) for i in range(pred_len)]
        
        total_visual_len = pred_start + visual_pred_len
    else:
        # Only input data
        input_positions = list(range(input_len))
        pred_positions = []
        total_visual_len = input_len
    
    # Combine all data for price range calculation
    combined_data = past_sequence + predicted_future
    all_values = [val for candle in combined_data for val in candle]
    min_val = min(all_values)
    max_val = max(all_values)
    val_range = max_val - min_val if max_val > min_val else 0.1
    padding = val_range * 0.05
    
    ax.set_ylim(min_val - padding, max_val + padding)
    ax.set_xlim(-0.5, total_visual_len - 0.5)
    
    # Draw input candlesticks with proper positioning
    for i, (o, h, l, c) in enumerate(past_sequence):
        x_pos = input_positions[i]
        
        # Input data - solid dark colors
        color = '#2e7d32' if c >= o else '#c62828'  # Dark green/red
        alpha = 1.0
        edge_style = '-'
        edge_width = 1
        
        # Draw high-low line (wick)
        ax.plot([x_pos, x_pos], [l, h], color='black', linewidth=1, alpha=alpha)
        
        # Draw candle body
        body_height = abs(c - o)
        body_bottom = min(o, c)
        
        if body_height > 0.001:
            rect = plt.Rectangle((x_pos - 0.3, body_bottom), 0.6, body_height, 
                               facecolor=color, edgecolor='black', 
                               linewidth=edge_width, linestyle=edge_style, alpha=alpha)
            ax.add_patch(rect)
        else:
            # Doji candle
            ax.plot([x_pos - 0.3, x_pos + 0.3], [o, o], color='black', linewidth=2, alpha=alpha)
    
    # Draw predicted candlesticks with proper positioning and scaling
    for i, (o, h, l, c) in enumerate(predicted_future):
        x_pos = pred_positions[i]
        
        # Prediction data - lighter colors with dashed outline  
        color = '#66bb6a' if c >= o else '#ef5350'  # Light green/red
        alpha = 0.8
        edge_style = '--'
        edge_width = 2
        
        # Draw high-low line (wick)
        ax.plot([x_pos, x_pos], [l, h], color='black', linewidth=1, alpha=alpha)
        
        # Draw candle body
        body_height = abs(c - o)
        body_bottom = min(o, c)
        
        if body_height > 0.001:
            rect = plt.Rectangle((x_pos - 0.3, body_bottom), 0.6, body_height, 
                               facecolor=color, edgecolor='black', 
                               linewidth=edge_width, linestyle=edge_style, alpha=alpha)
            ax.add_patch(rect)
        else:
            # Doji candle
            ax.plot([x_pos - 0.3, x_pos + 0.3], [o, o], color='black', linewidth=2, alpha=alpha)
    
    # Add separator line between input and predictions
    if len(past_sequence) > 0 and len(predicted_future) > 0:
        separator_x = input_len + 1  # Position between sections
        ax.axvline(x=separator_x, color='purple', linewidth=3, linestyle='--', alpha=0.9)
        ax.text(separator_x, ax.get_ylim()[1] * 0.95, 'AI PREDICTIONS START', 
               ha='center', va='top', fontweight='bold', color='purple', fontsize=12,
               bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='purple', alpha=0.8))
    
    # Calculate percentage for title
    if len(predicted_future) > 0:
        pred_percentage = len(predicted_future) / (len(past_sequence) + len(predicted_future)) * 100
        title_text = f'Input: {len(past_sequence)} candles → AI Predicted: {len(predicted_future)} candles ({pred_percentage:.1f}% predictions)'
    else:
        title_text = f'Input: {len(past_sequence)} candles (No predictions generated)'
    
    # Styling
    ax.set_title(title_text, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('Time Period (Proportionally Scaled)', fontsize=12)
    ax.set_ylabel('Price Level', fontsize=12)
    
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#2e7d32', label='Input - Bullish'),
        Patch(facecolor='#c62828', label='Input - Bearish'),
        Patch(facecolor='#66bb6a', label='Predicted - Bullish'),
        Patch(facecolor='#ef5350', label='Predicted - Bearish')
    ]
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.99, 0.99))
    
    # Convert to image bytes
    img_buffer = io.BytesIO()
    plt.tight_layout()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    
    img_buffer.seek(0)
    return img_buffer

@app.get("/")
async def root():
    return {"message": "Candlestick Predictor Backend API", "status": "running"}

@app.get("/health")
async def health_check():
    ai_status = "unknown"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{AI_SERVICE_URL}/health", timeout=5.0)
            if response.status_code == 200:
                ai_status = "healthy"
            else:
                ai_status = "unhealthy"
    except:
        ai_status = "unreachable"
    
    return {
        "status": "healthy",
        "backend": "running",
        "ai_service": ai_status
    }

@app.post("/convert-image-to-numeric")
async def convert_image_to_numeric_endpoint(file: UploadFile = File(...)):
    """Convert uploaded candlestick image to numeric OHLC data"""
    try:
        # Read uploaded image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        # Extract numeric data using image processing
        numeric_data = image_to_numeric(img)
        
        # Validate extracted data
        if not validate_numeric_data(numeric_data):
            raise HTTPException(status_code=400, detail="Failed to extract valid candlestick data from image")
        
        return {
            "status": "success",
            "message": f"Extracted {len(numeric_data)} candlesticks from {file.filename}",
            "numeric_data": numeric_data,
            "sequence_length": len(numeric_data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion error: {str(e)}")

@app.post("/predict")
async def predict_endpoint(data: dict):
    """Forward prediction request to AI service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AI_SERVICE_URL}/predict",
                json=data,
                timeout=30.0
            )
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"AI service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/full-process")
async def full_process_endpoint(file: UploadFile = File(...)):
    """Complete pipeline: real image -> numeric -> model prediction -> comparison visualization"""
    try:
        print(f"Processing file: {file.filename}")
        
        # Step 1: Extract numeric data from uploaded image
        contents = await file.read()
        print(f"File bytes length: {len(contents)}")
        
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            print("Failed to decode image")
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        print(f"Image shape: {img.shape}")
        
        # Real image processing
        past_sequence = image_to_numeric(img)
        print(f"Extracted {len(past_sequence)} candles")
        
        if not validate_numeric_data(past_sequence):
            print("Invalid numeric data extracted")
            raise HTTPException(status_code=400, detail="Failed to extract valid data from image")
        
        print(f"Extracted {len(past_sequence)} candles: {past_sequence[:3]}...")
        
        # Step 2: Get AI prediction using real model
        prediction_data = {
            "data": [past_sequence],  # Wrap in batch
            "sequence_length": len(past_sequence)
        }
        
        print(f"Sending to AI service: {len(past_sequence)} candles")
        
        async with httpx.AsyncClient() as client:
            ai_response = await client.post(
                f"{AI_SERVICE_URL}/predict",
                json=prediction_data,
                timeout=30.0
            )
            prediction_result = ai_response.json()
        
        print(f"AI response status: {prediction_result.get('status', 'unknown')}")
        print(f"AI response message: {prediction_result.get('message', 'no message')}")
        predicted_future = prediction_result.get("predictions", [[]])[0]  # Get first batch item
        print(f"Got {len(predicted_future)} predictions from {'REAL MODEL' if 'Real PyTorch' in prediction_result.get('message', '') else 'FALLBACK'}")
        
        # Step 3: No fake data needed - we only show input and predictions
        
        # Step 4: Create visualization showing input + predictions
        print("Reconstructing image...")
        chart_title = f"Candlestick Prediction for {file.filename}"
        
        try:
            img_buffer = create_candlestick_comparison(
                past_sequence, 
                [], 
                predicted_future, 
                chart_title
            )
            print("Image reconstruction successful")
        except Exception as viz_error:
            print(f"Visualization error: {viz_error}")
            # Create simple fallback response
            return {"error": f"Visualization failed: {str(viz_error)}", 
                   "past_candles": len(past_sequence),
                   "predicted_candles": len(predicted_future)}
        
        print("Returning image response")
        # Return as image
        return StreamingResponse(
            io.BytesIO(img_buffer.read()), 
            media_type="image/png",
            headers={
                "Content-Disposition": f"inline; filename=prediction_{file.filename}.png"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main_simple:app", host="0.0.0.0", port=8000, reload=True)
