# Pose Analysis Service

A high-performance microservice for real-time exercise video analysis. Built with FastAPI and MediaPipe, this service processes videos to detect poses, calculate joint angles, and provide detailed movement analysis. Seamlessly integrated with Firebase Storage for scalable video processing.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.68.0+-green.svg)
![Firebase](https://img.shields.io/badge/Firebase-Storage-orange.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🚀 Features

- **Real-time Pose Analysis**
  - Advanced pose detection using MediaPipe
  - Precise angle calculations for 6 key body joints
  - Frame-by-frame movement tracking

- **Comprehensive Joint Analysis**
  - Left/Right Elbow angles
  - Left/Right Knee angles
  - Left/Right Hip angles
  - Visual angle overlay on processed videos

- **Robust Architecture**
  - Asynchronous video processing
  - Background task management
  - Health monitoring endpoint
  - Detailed logging system

- **Cloud Integration**
  - Firebase Storage integration
  - Automatic video processing triggers
  - Secure credential management

## 🛠️ Prerequisites

- Python 3.9 or higher
- Firebase project with Storage enabled
- Firebase Admin SDK credentials
- Docker (optional, for containerization)
- OpenCV system dependencies

## 🔧 Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/pose-analysis-service.git
   cd pose-analysis-service
   ```

2. **Set Up Virtual Environment (Recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   
   Create `.env` file and add your Firebase credentials:
   ```env
   FIREBASE_CREDENTIALS={"type": "service_account","project_id": "your-project-id",...}
   FIREBASE_STORAGE_BUCKET=your-bucket-name.appspot.com
   ```

## 🚀 Running the Service

### Local Development
```bash
# Run with auto-reload for development
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run for production
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker Deployment
```bash
# Build the image
docker build -t video-processor .

# Run in detached mode with automatic restart
docker run -d \
  --name video-processor \
  -p 8000:8000 \
  --env-file .env \
  --restart unless-stopped \
  video-processor
```

## 🔌 API Endpoints

### Health Check
```http
GET /health
```
Response:
```json
{
    "status": "healthy",
    "message": "Service is running and Firebase connection is active"
}
```

### Process Video
```http
POST /process-video
```
Request:
```json
{
    "folder_id": "unique-folder-id",
    "notification_url": "https://your-callback-url.com/notify"
}
```
Response:
```json
{
    "message": "Processing video for folder_id: unique-folder-id",
    "status": "accepted"
}
```

## 📁 Storage Structure

```
exercise_videos/
├── {folder_id}/
│   ├── video.mp4           # Original upload
│   ├── pose_video.mp4      # Processed with overlays
│   └── pose_angles.json    # Angle data per frame
```

## 🛠️ Development

### Project Structure
```
├── main.py                 # FastAPI application
├── video_processor.py      # Core processing logic
├── requirements.txt        # Dependencies
├── Dockerfile             # Container configuration
├── .env                   # Environment variables
└── functions/            # Firebase Functions
    └── index.js          # Cloud Function trigger
```

### Docker Management
```bash
# View logs
docker logs video-processor

# Monitor container
docker stats video-processor

# Container lifecycle
docker stop video-processor
docker start video-processor
docker restart video-processor
```

## 📊 Monitoring

- Health endpoint for uptime monitoring
- Comprehensive logging with timestamps
- Docker container metrics
- Firebase Storage analytics

## 🔒 Security

- Secure Firebase credential handling
- Environment variable protection
- Docker security best practices
- Input validation and sanitization

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📧 Contact

Your Name - [@yourusername](https://twitter.com/yourusername)

Project Link: [https://github.com/yourusername/pose-analysis-service](https://github.com/yourusername/pose-analysis-service)