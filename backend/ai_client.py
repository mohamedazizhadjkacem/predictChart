import aiohttp
import asyncio
import json
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class AIClient:
    """Client for communicating with the AI microservice"""
    
    def __init__(self, base_url: str = "http://ai:8001"):
        self.base_url = base_url
        self.session = None
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def health_check(self) -> bool:
        """Check if AI service is healthy"""
        try:
            session = await self._get_session()
            async with session.get(f"{self.base_url}/health", timeout=5) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"AI service health check failed: {str(e)}")
            return False
    
    async def predict(self, numeric_data: List[List[float]]) -> List[List[float]]:
        """
        Send numeric candlestick data to AI service for prediction
        
        Args:
            numeric_data: List of [open, high, low, close] values
            
        Returns:
            List of predicted future [open, high, low, close] values
        """
        try:
            session = await self._get_session()
            
            payload = {"sequence": numeric_data}
            
            logger.info(f"Sending prediction request with {len(numeric_data)} candlesticks")
            
            async with session.post(
                f"{self.base_url}/predict",
                json=payload,
                timeout=30,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"AI service returned status {response.status}: {error_text}")
                
                result = await response.json()
                prediction = result.get("prediction", [])
                
                if not prediction:
                    raise Exception("AI service returned empty prediction")
                
                logger.info(f"Received prediction with {len(prediction)} future candlesticks")
                return prediction
                
        except asyncio.TimeoutError:
            logger.error("Timeout waiting for AI service prediction")
            raise Exception("AI service prediction timed out")
        except aiohttp.ClientError as e:
            logger.error(f"Network error communicating with AI service: {str(e)}")
            raise Exception(f"Failed to communicate with AI service: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from AI service: {str(e)}")
            raise Exception("AI service returned invalid response")
        except Exception as e:
            logger.error(f"Unexpected error calling AI service: {str(e)}")
            raise Exception(f"AI service error: {str(e)}")
    
    async def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        try:
            session = await self._get_session()
            async with session.get(f"{self.base_url}/model-info", timeout=10) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Status {response.status}"}
        except Exception as e:
            logger.error(f"Error getting model info: {str(e)}")
            return {"error": str(e)}
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def __del__(self):
        """Cleanup session on deletion"""
        if hasattr(self, 'session') and self.session and not self.session.closed:
            # Create a new event loop if needed for cleanup
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is running, schedule cleanup
                    loop.create_task(self.session.close())
                else:
                    # If loop is not running, run cleanup
                    loop.run_until_complete(self.session.close())
            except RuntimeError:
                # Create new loop for cleanup
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.session.close())
                loop.close()

# Utility function for testing connectivity
async def test_ai_connection(base_url: str = "http://ai:8001") -> bool:
    """Test connection to AI service"""
    client = AIClient(base_url)
    try:
        is_healthy = await client.health_check()
        if is_healthy:
            model_info = await client.get_model_info()
            logger.info(f"AI service connected. Model info: {model_info}")
        return is_healthy
    finally:
        await client.close()