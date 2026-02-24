import React, { useState, useRef } from 'react';
import { useMediaRecorder } from '../hooks/useMediaRecorder';
import { WavEncoder } from '../utils/audioEncoder';
import { AudioResampler } from '../utils/audioResampler';
import './ReadingTask.css';

interface ReadingTaskProps {
  age: number;
  paragraph: string;
  onComplete: (audioBlob: Blob) => void;
}

export const ReadingTask: React.FC<ReadingTaskProps> = ({
  age,
  paragraph,
  onComplete,
}) => {
  const { startRecording, stopRecording, isRecording, recognizedText } =
    useMediaRecorder();
  const [isStarted, setIsStarted] = useState(false);
  const [error, setError] = useState<string>('');
  const audioContextRef = useRef<AudioContext | null>(null);
  const mediaStreamAudioSourceRef = useRef<MediaStreamAudioSource | null>(null);
  const scriptProcessorRef = useRef<ScriptProcessorNode | null>(null);
  const audioChunksRef = useRef<Float32Array[]>([]);
  const streamRef = useRef<MediaStream | null>(null);

  const handleStartReading = async () => {
    setError('');
    setIsStarted(true);
    audioChunksRef.current = [];

    try {
      console.log('🎤 Requesting microphone access...');
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      });
      streamRef.current = stream;
      console.log('✅ Microphone accessed');

      // Initialize Web Audio API for raw PCM capture
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      audioContextRef.current = audioContext;

      console.log(`🎵 Audio context created - Sample rate: ${audioContext.sampleRate} Hz`);

      const audioSource = audioContext.createMediaStreamSource(stream);
      mediaStreamAudioSourceRef.current = audioSource;

      // Create script processor to capture raw audio
      const scriptProcessor = audioContext.createScriptProcessor(4096, 1, 1);
      scriptProcessorRef.current = scriptProcessor;

      let processedCount = 0;
      scriptProcessor.onaudioprocess = (event: AudioProcessingEvent) => {
        const inputData = event.inputBuffer.getChannelData(0);
        // Store a copy of the data
        audioChunksRef.current.push(new Float32Array(inputData));
        processedCount++;
        
        if (processedCount % 10 === 0) {
          console.log(`📊 Audio processing: ${processedCount} chunks captured`);
        }
      };

      audioSource.connect(scriptProcessor);
      scriptProcessor.connect(audioContext.destination);

      console.log('🎙️ Audio capture started - Speak now!');
      startRecording();
    } catch (err: any) {
      console.error('❌ Microphone error:', err);
      setError('Failed to access microphone. Please check: 1) Browser permissions, 2) Microphone is connected, 3) Try a different browser');
      setIsStarted(false);
    }
  };

  const handleStopReading = async () => {
    stopRecording();

    console.log('📊 Audio capture stats:', {
      chunks: audioChunksRef.current.length,
      totalSamples: audioChunksRef.current.reduce((acc, chunk) => acc + chunk.length, 0),
      sampleRate: audioContextRef.current?.sampleRate || 'unknown',
    });

    // Clean up audio context
    if (scriptProcessorRef.current && mediaStreamAudioSourceRef.current) {
      mediaStreamAudioSourceRef.current.disconnect(scriptProcessorRef.current);
      scriptProcessorRef.current.disconnect();
    }

    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
    }

    if (audioContextRef.current) {
      audioContextRef.current.close();
    }

    // Convert audio chunks to WAV
    try {
      const totalLength = audioChunksRef.current.reduce(
        (acc, chunk) => acc + chunk.length,
        0
      );

      if (totalLength === 0) {
        setError('No audio was captured. Please try again and speak clearly into the microphone.');
        setIsStarted(false);
        return;
      }

      console.log(`📦 Processing ${totalLength} audio samples...`);

      const audioData = new Float32Array(totalLength);
      let offset = 0;

      for (const chunk of audioChunksRef.current) {
        audioData.set(chunk, offset);
        offset += chunk.length;
      }

      const originalSampleRate = audioContextRef.current?.sampleRate || 44100;

      // Resample to 16000 Hz if needed
      let audioToEncode = audioData;
      if (originalSampleRate !== 16000) {
        console.log(
          `🔄 Resampling from ${originalSampleRate}Hz to 16000Hz...`
        );
        audioToEncode = AudioResampler.resample(audioData, originalSampleRate, 16000);
      }

      // Encode to WAV format with 16000 Hz sample rate
      const encoder = new WavEncoder(16000, 1);
      const wavBuffer = encoder.encode(audioToEncode);
      const wavBlob = new Blob([wavBuffer], { type: 'audio/wav' });

      console.log(`✅ WAV file created: ${(wavBlob.size / 1024).toFixed(2)} KB`);

      if (wavBlob.size === 0) {
        setError('Failed to create audio file. Please try again.');
        setIsStarted(false);
        return;
      }

      if (wavBlob.size < 1000) {
        setError('Audio file is too small. Please record for at least a few seconds.');
        setIsStarted(false);
        return;
      }

      console.log('🎵 Audio ready, sending to backend...');
      onComplete(wavBlob);
    } catch (err: any) {
      console.error('❌ Audio processing error:', err);
      setError(`Failed to process audio: ${err.message}`);
      setIsStarted(false);
    }
  };

  return (
    <div className="reading-task-container">
      <div className="reading-task-card">
        <div className="task-header">
          <h2>📖 Reading Assessment (Age {age})</h2>
          <p className="instruction">Read the paragraph below aloud clearly</p>
        </div>

        <div className="paragraph-box">
          <p className="paragraph-text">{paragraph}</p>
        </div>

        {recognizedText && (
          <div className="recognition-box">
            <h3>🎤 Live Recognition:</h3>
            <p className="recognized-text">{recognizedText}</p>
          </div>
        )}

        {error && <p className="error-message">{error}</p>}

        <div className="controls">
          {!isStarted ? (
            <button className="btn btn-primary" onClick={handleStartReading}>
              🎤 Start Reading
            </button>
          ) : (
            <>
              <button className="btn btn-danger" onClick={handleStopReading}>
                ⏹ Stop & Submit
              </button>
              {isRecording && (
                <div className="recording-indicator">
                  <span className="dot"></span> Recording...
                </div>
              )}
            </>
          )}
        </div>

        <div className="tips">
          <h4>📝 Instructions:</h4>
          <ul>
            <li>✓ Read the entire paragraph clearly and naturally</li>
            <li>✓ Speak at a normal pace (don't rush)</li>
            <li>✓ Ensure your microphone is working properly</li>
            <li>✓ Minimize background noise for best results</li>
            <li>✓ Keep recording for at least 5-10 seconds</li>
            <li>💡 Tip: Open DevTools (F12) → Console to see detailed logs if there's an error</li>
          </ul>
        </div>
      </div>
    </div>
  );
};
