const functions = require("firebase-functions/v2");
const { onObjectFinalized } = require("firebase-functions/v2/storage");
const { defineString } = require("firebase-functions/params");
const axios = require("axios");

// Define the service URL parameter
const SERVICE_URL = '<Your_URL>';

exports.triggerVideoProcessing = onObjectFinalized({
    memory: '256MB',
    timeoutSeconds: 60,
    region: 'us-east1',
    bucket: 'fitnessaitrainer.firebasestorage.app'
}, async (event) => {
    // Check if this is a video.mp4 file in an exercise_videos subfolder
    const pathParts = event.data.name.split('/');
    
    // Only proceed if:
    // 1. Path starts with exercise_videos/
    // 2. Has exactly 3 parts (exercise_videos/folderId/video.mp4)
    // 3. Ends with video.mp4
    // 4. Is not a pose_video
    if (!event.data.name.startsWith('exercise_videos/') || 
        pathParts.length !== 3 ||
        !event.data.name.endsWith('video.mp4') ||
        event.data.name.includes('pose_video')) {
        console.log('Not a target video file:', event.data.name);
        return null;
    }

    const folder_id = pathParts[1];
    console.log(`New video detected in folder: ${folder_id}`);

    try {
        const url = `${SERVICE_URL}/process-video`;
        console.log(`Calling processing service at URL: ${url}`);
        
        const response = await axios.post(url, {
            folder_id: folder_id
        }, {
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        console.log('Processing initiated:', response.data);
        return response.data;
    } catch (error) {
        console.error(`Error processing video in folder ${folder_id}:`, error.message);
        if (error.config) {
            console.error('Failed request config:', {
                url: error.config.url,
                method: error.config.method,
                data: error.config.data
            });
        }
        throw new Error(`Failed to process video: ${error.message}`);
    }
}); 