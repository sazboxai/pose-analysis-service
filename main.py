from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import uvicorn
from typing import Optional, Dict
from dotenv import load_dotenv
from video_processor import process_new_video, bucket
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

class VideoRequest(BaseModel):
    folder_id: str
    notification_url: Optional[str] = None

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Check the health of the service and its dependencies
    """
    try:
        # Check Firebase connection by listing a single bucket
        bucket.exists()
        return {
            "status": "healthy",
            "message": "Service is running and Firebase connection is active"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Service is unhealthy: Firebase connection failed"
        )

@app.post("/process-video")
async def process_video_endpoint(request: VideoRequest, background_tasks: BackgroundTasks):
    """
    Endpoint to process a video from Firebase Storage
    """
    try:
        logger.info(f"Received video processing request for folder_id: {request.folder_id}")
        # Add task to background processing
        background_tasks.add_task(process_new_video, request.folder_id)
        logger.info(f"Added background task for folder_id: {request.folder_id}")
        return {"message": f"Processing video for folder_id: {request.folder_id}", "status": "accepted"}
    except Exception as e:
        logger.error(f"Error processing request for folder_id {request.folder_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 