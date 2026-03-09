import axios from 'axios';
import { AssessmentResponse } from './types';

export const API_BASE_URL = 'http://localhost:8000';

export const assessReading = async (
  age: number,
  paragraph: string,
  audioBlob: Blob,
  recognizedText: string = ''
): Promise<AssessmentResponse> => {
  try {
    // Validate inputs
    if (!audioBlob || audioBlob.size === 0) {
      throw new Error('Audio blob is empty. Please record audio and try again.');
    }

    if (audioBlob.size < 100) {
      throw new Error('Audio recording too short. Please record at least a few seconds.');
    }

    if (!paragraph || paragraph.trim().length === 0) {
      throw new Error('Paragraph is empty');
    }

    if (!age || age < 5 || age > 100) {
      throw new Error('Invalid age provided');
    }

    console.log(`📤 Sending assessment request:`, {
      age,
      paragraphLength: paragraph.length,
      audioSize: `${(audioBlob.size / 1024).toFixed(2)} KB`,
      audioType: audioBlob.type,
      recognizedTextLength: recognizedText.length,
    });

    const formData = new FormData();
    formData.append('age', String(age));
    formData.append('paragraph', paragraph);
    formData.append('audio_file', audioBlob, 'recording.wav');
    if (recognizedText) {
      formData.append('recognized_text', recognizedText);
    }

    const response = await axios.post<AssessmentResponse>(
      `${API_BASE_URL}/assess`,
      formData,
      {
        timeout: 120000, // 120 second timeout for processing
      }
    );

    console.log('✅ Assessment completed successfully:', response.data.status);
    return response.data;
  } catch (error: any) {
    console.error('❌ Assessment error details:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status,
      statusText: error.response?.statusText,
    });

    // Extract detailed error message
    let errorMessage = 'Unknown error occurred';

    if (error.response) {
      // Server responded with error
      const data = error.response.data;

      if (typeof data === 'string') {
        errorMessage = data;
      } else if (data?.detail) {
        if (Array.isArray(data.detail)) {
          // FastAPI validation error
          errorMessage = data.detail
            .map((err: any) => {
              if (typeof err === 'object' && err.msg) {
                return `${err.loc?.join('.')}: ${err.msg}`;
              }
              return String(err);
            })
            .join('; ');
        } else {
          errorMessage = data.detail;
        }
      } else if (data?.message) {
        errorMessage = data.message;
      } else {
        errorMessage = `Server error (${error.response.status}): ${error.response.statusText}`;
      }
    } else if (error.request) {
      // Request made but no response
      errorMessage =
        'Backend server is not responding. Make sure it is running: python backend/app.py';
    } else {
      errorMessage = error.message;
    }

    throw new Error(errorMessage);
  }
};

export const getHealth = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/health`, {
      timeout: 5000,
    });
    console.log('✅ Backend health check passed');
    return response.data;
  } catch (error) {
    console.error('⚠️ Backend health check failed - server may not be running');
    throw new Error('Backend server is not responding at http://localhost:8000');
  }
};

export const submitSpeedTrainerResults = async (
  sessionId: string,
  elapsedTimeSeconds: number
): Promise<any> => {
  try {
    console.log(`📤 Submitting speed trainer results for session: ${sessionId}`);
    console.log(`   Elapsed time: ${elapsedTimeSeconds} seconds`);

    const response = await axios.post(
      `${API_BASE_URL}/speed-trainer/submit-results`,
      {
        session_id: sessionId,
        elapsed_time_seconds: elapsedTimeSeconds,
      },
      {
        timeout: 30000,
      }
    );

    console.log('✅ Speed trainer results submitted successfully');
    return response.data;
  } catch (error: any) {
    console.error('❌ Error submitting speed trainer results:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status,
    });

    let errorMessage = 'Failed to submit speed trainer results';

    if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail;
    } else if (error.message) {
      errorMessage = error.message;
    }

    throw new Error(errorMessage);
  }
};

export const submitChunkReadingResults = async (
  sessionId: string,
  elapsedTimeSeconds: number
): Promise<any> => {
  try {
    console.log(`📤 Submitting chunk reading results for session: ${sessionId}`);
    console.log(`   Elapsed time: ${elapsedTimeSeconds} seconds`);

    const response = await axios.post(
      `${API_BASE_URL}/chunk-reading/submit-results`,
      {
        session_id: sessionId,
        elapsed_time_seconds: elapsedTimeSeconds,
      },
      {
        timeout: 30000,
      }
    );

    console.log('✅ Chunk reading results submitted successfully');
    return response.data;
  } catch (error: any) {
    console.error('❌ Error submitting chunk reading results:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status,
    });

    let errorMessage = 'Failed to submit chunk reading results';

    if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail;
    } else if (error.message) {
      errorMessage = error.message;
    }

    throw new Error(errorMessage);
  }
};
