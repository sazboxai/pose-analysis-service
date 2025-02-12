import firebase_admin
from firebase_admin import credentials, storage
import cv2
import mediapipe as mp
import numpy as np
import json
import os
from tempfile import NamedTemporaryFile
import tempfile
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Initialize Firebase Admin SDK if not already initialized
if not firebase_admin._apps:
    firebase_creds = json.loads(os.getenv('FIREBASE_CREDENTIALS'))
    
    # Fix the private key formatting
    if 'private_key' in firebase_creds:
        firebase_creds['private_key'] = firebase_creds['private_key'].replace('\\n', '\n')
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
        json.dump(firebase_creds, temp_file)
        temp_file_path = temp_file.name

    cred = credentials.Certificate(temp_file_path)
    firebase_admin.initialize_app(cred, {
        "storageBucket": os.getenv('FIREBASE_STORAGE_BUCKET')
    })
    
    os.unlink(temp_file_path)

bucket = storage.bucket()

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

POSE_CONNECTIONS = [
    (mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.LEFT_ELBOW),
    (mp_pose.PoseLandmark.LEFT_ELBOW, mp_pose.PoseLandmark.LEFT_WRIST),
    (mp_pose.PoseLandmark.RIGHT_SHOULDER, mp_pose.PoseLandmark.RIGHT_ELBOW),
    (mp_pose.PoseLandmark.RIGHT_ELBOW, mp_pose.PoseLandmark.RIGHT_WRIST),
    (mp_pose.PoseLandmark.LEFT_HIP, mp_pose.PoseLandmark.LEFT_KNEE),
    (mp_pose.PoseLandmark.LEFT_KNEE, mp_pose.PoseLandmark.LEFT_ANKLE),
    (mp_pose.PoseLandmark.RIGHT_HIP, mp_pose.PoseLandmark.RIGHT_KNEE),
    (mp_pose.PoseLandmark.RIGHT_KNEE, mp_pose.PoseLandmark.RIGHT_ANKLE),
]

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def calculate_angles(landmarks):
    """Calculate angles at key joints while handling edge cases."""
    def angle_between(p1, p2, p3):
        v1 = np.array([p1.x - p2.x, p1.y - p2.y])
        v2 = np.array([p3.x - p2.x, p3.y - p2.y])
        
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)

        if norm_v1 == 0 or norm_v2 == 0:
            return 0

        cosine_angle = np.dot(v1, v2) / (norm_v1 * norm_v2)

        if np.isnan(cosine_angle) or cosine_angle < -1 or cosine_angle > 1:
            return 0  

        return np.degrees(np.arccos(cosine_angle))

    return {
        mp_pose.PoseLandmark.LEFT_ELBOW: angle_between(
            landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER], 
            landmarks[mp_pose.PoseLandmark.LEFT_ELBOW], 
            landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
        ),
        mp_pose.PoseLandmark.RIGHT_ELBOW: angle_between(
            landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER], 
            landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW], 
            landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
        ),
        mp_pose.PoseLandmark.LEFT_KNEE: angle_between(
            landmarks[mp_pose.PoseLandmark.LEFT_HIP], 
            landmarks[mp_pose.PoseLandmark.LEFT_KNEE], 
            landmarks[mp_pose.PoseLandmark.LEFT_ANKLE]
        ),
        mp_pose.PoseLandmark.RIGHT_KNEE: angle_between(
            landmarks[mp_pose.PoseLandmark.RIGHT_HIP], 
            landmarks[mp_pose.PoseLandmark.RIGHT_KNEE], 
            landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE]
        ),
        mp_pose.PoseLandmark.RIGHT_HIP: angle_between(
            landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER], 
            landmarks[mp_pose.PoseLandmark.RIGHT_HIP], 
            landmarks[mp_pose.PoseLandmark.NOSE]
        ),
        mp_pose.PoseLandmark.LEFT_HIP: angle_between(
            landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER], 
            landmarks[mp_pose.PoseLandmark.LEFT_HIP], 
            landmarks[mp_pose.PoseLandmark.NOSE]
        )
    }

def process_video(video_path):
    cap = cv2.VideoCapture(video_path)
    width = int(cap.get(3))
    height = int(cap.get(4))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    # Create output path in the same directory as input
    output_path = os.path.join(os.path.dirname(video_path), f"processed_{os.path.basename(video_path)}")
    
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    angles_data = []
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            keypoints = {
                lm: (int(landmarks[lm].x * width), int(landmarks[lm].y * height))
                for lm in mp_pose.PoseLandmark
            }
            angles = calculate_angles(landmarks)
            angles_data.append(angles)

            for x, y in keypoints.values():
                cv2.circle(frame, (x, y), 6, (0, 0, 255), -1)

            for connection in POSE_CONNECTIONS:
                pt1 = keypoints.get(connection[0])
                pt2 = keypoints.get(connection[1])
                if pt1 and pt2:
                    cv2.line(frame, pt1, pt2, (255, 255, 255), 2)

            for joint, angle in angles.items():
                x, y = keypoints[joint]
                angle_text = f"{int(angle)}°" if angle else "N/A"
                cv2.putText(frame, angle_text, (x + 10, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2, cv2.LINE_AA)

        out.write(frame)

    cap.release()
    out.release()
    
    logger.info(f"Video processed and saved to: {output_path}")
    return output_path, angles_data

def download_video(folder_id: str) -> str:
    """Download video from Firebase Storage"""
    try:
        with NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
            blob = bucket.blob(f"exercise_videos/{folder_id}/video.mp4")
            blob.download_to_filename(temp_file.name)
            logger.info(f"Successfully downloaded video for folder_id: {folder_id}")
            return temp_file.name
    except Exception as e:
        logger.error(f"Error downloading video for folder_id {folder_id}: {str(e)}")
        raise Exception(f"Error downloading video: {str(e)}")

def upload_processed_data(folder_id, processed_video_path, angles_data):
    try:
        # Upload processed video
        processed_blob = bucket.blob(f"exercise_videos/{folder_id}/pose_video.mp4")
        processed_blob.upload_from_filename(processed_video_path)
        logger.info(f"Uploaded processed video for folder_id: {folder_id}")

        # Save angles data as JSON
        angles_json_path = f"pose_angles.json"
        with open(angles_json_path, "w") as f:
            json.dump(angles_data, f)

        angles_blob = bucket.blob(f"exercise_videos/{folder_id}/pose_angles.json")
        angles_blob.upload_from_filename(angles_json_path)
        logger.info(f"Uploaded angles data for folder_id: {folder_id}")
        
        os.unlink(angles_json_path)
    except Exception as e:
        logger.error(f"Error uploading processed data for folder_id {folder_id}: {str(e)}")
        raise

def process_new_video(folder_id: str):
    """Process video and upload results"""
    try:
        logger.info(f"Starting video processing for folder_id: {folder_id}")
        
        # Download video
        video_path = download_video(folder_id)
        logger.info(f"Video downloaded to: {video_path}")
        
        # Process video
        processed_video_path, angles_data = process_video(video_path)
        logger.info(f"Video processed: {processed_video_path}")
        
        # Upload results
        upload_processed_data(folder_id, processed_video_path, angles_data)
        logger.info(f"Results uploaded for folder_id: {folder_id}")
        
        # Cleanup temporary files
        os.unlink(video_path)
        os.unlink(processed_video_path)
        logger.info(f"Temporary files cleaned up for folder_id: {folder_id}")
        
    except Exception as e:
        logger.error(f"Error processing video for folder_id {folder_id}: {str(e)}")
        raise 