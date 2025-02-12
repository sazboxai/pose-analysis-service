const functions = require('firebase-functions');
const axios = require('axios');

exports.triggerVideoProcessing = functions.storage.object().onFinalize(async (object) => {
    // Only trigger for original video uploads
    if (!object.name.endsWith('video.mp4') || object.name.includes('pose_video')) {
        console.log('Skipping non-target file:', object.name);
        return null;
    }

    // Extract folder_id from path
    const pathParts = object.name.split('/');
    const folder_id = pathParts[pathParts.length - 2];
    console.log('Processing triggered for folder_id:', folder_id);

    // Call the FastAPI microservice
    try {
        console.log('Calling microservice for folder_id:', folder_id);
        const response = await axios.post('http://your-fastapi-service-url/process-video', {
            folder_id: folder_id
        });
        
        console.log('Successfully initiated processing for folder_id:', folder_id);
        console.log('Response:', response.data);
        return response.data;
    } catch (error) {
        console.error('Error triggering video processing for folder_id:', folder_id);
        console.error('Error details:', error.message);
        throw new Error('Failed to trigger video processing');
    }
}); 