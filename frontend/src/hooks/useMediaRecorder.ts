import { useState, useRef, useCallback } from 'react';
import { WavEncoder } from '../utils/audioEncoder';
import { AudioResampler } from '../utils/audioResampler';

export const useMediaRecorder = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [recognizedText, setRecognizedText] = useState('');
  const recognitionRef = useRef<any>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const audioSourceRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const scriptProcessorRef = useRef<ScriptProcessorNode | null>(null);
  const audioChunksRef = useRef<Float32Array[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const finalTranscriptRef = useRef<string>('');
  const recognitionCompleteRef = useRef<boolean>(false);

  const startRecording = useCallback(async () => {
    setIsRecording(true);
    audioChunksRef.current = [];
    finalTranscriptRef.current = '';
    recognitionCompleteRef.current = false;
    setRecognizedText('');

    try {
      // Get microphone stream
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: false  // Disable auto gain to preserve voice levels
        }
      });
      streamRef.current = stream;
      console.log('🎤 Got media stream');

      // Initialize Web Audio API to capture raw PCM
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      audioContextRef.current = audioContext;
      console.log(`🎵 Audio context created - Sample rate: ${audioContext.sampleRate} Hz`);

      const audioSource = audioContext.createMediaStreamSource(stream);
      audioSourceRef.current = audioSource;

      // ScriptProcessor to capture raw audio
      const scriptProcessor = audioContext.createScriptProcessor(4096, 1, 1);
      scriptProcessorRef.current = scriptProcessor;

      let chunks = 0;
      scriptProcessor.onaudioprocess = (event: AudioProcessingEvent) => {
        const inputData = event.inputBuffer.getChannelData(0);
        audioChunksRef.current.push(new Float32Array(inputData));
        chunks++;
        
        if (chunks % 10 === 0) {
          console.log(`📊 Captured ${chunks} chunks`);
        }
      };

      audioSource.connect(scriptProcessor);
      scriptProcessor.connect(audioContext.destination);

      // Set up Web Speech API for continuous recognition
      const SpeechRecognition =
        (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

      if (SpeechRecognition) {
        recognitionRef.current = new SpeechRecognition();
        recognitionRef.current.lang = 'en-US';
        recognitionRef.current.interimResults = true;
        recognitionRef.current.continuous = true;
        recognitionRef.current.maxAlternatives = 1;

        recognitionRef.current.onstart = () => {
          console.log('🎤 Web Speech API recognition started');
        };

        recognitionRef.current.onresult = (event: any) => {
          let interimTranscript = '';

          // Process all results from this event
          for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;

            if (event.results[i].isFinal) {
              // Add final results to permanent storage
              finalTranscriptRef.current += transcript + ' ';
              console.log(`✅ Final: "${transcript}"`);
            } else {
              // Interim results for display
              interimTranscript += transcript;
              console.log(`📝 Interim: "${transcript}"`);
            }
          }

          // Update display with final + interim text
          const displayText = finalTranscriptRef.current + interimTranscript;
          setRecognizedText(displayText);
          console.log(`📊 Current recognized text (${finalTranscriptRef.current.split(' ').filter(w => w).length} words): ${displayText}`);
        };

        recognitionRef.current.onerror = (event: any) => {
          console.error('🔴 Speech recognition error:', event.error);
          if (event.error === 'no-speech') {
            console.warn('⚠️ No speech detected - continuing to listen...');
            // Don't stop on no-speech error with continuous mode
          }
        };

        recognitionRef.current.onend = () => {
          recognitionCompleteRef.current = true;
          console.log('⏹ Web Speech API ended');
        };

        try {
          recognitionRef.current.start();
          console.log('🎤 Web Speech API started with continuous mode');
        } catch (error) {
          console.error('Error starting recognition:', error);
        }
      }
      
      console.log('✅ Recording and recognition started');
    } catch (error) {
      console.error('❌ Error starting recording:', error);
      setIsRecording(false);
      throw error;
    }
  }, []);

  const stopRecording = useCallback((): Promise<Blob> => {
    return new Promise((resolve, reject) => {
      try {
        setIsRecording(false);
        
        // Add a small delay to allow Web Speech API to process final results
        const stopTimeout = setTimeout(() => {
          console.log('⏱️ Stop timeout - proceeding with captured audio');
          proceedWithStop();
        }, 500);  // 500ms timeout for final processing

        const proceedWithStop = () => {
          clearTimeout(stopTimeout);

          // Stop Web Speech API
          if (recognitionRef.current) {
            try {
              console.log('⏹ Attempting to stop Web Speech API...');
              recognitionRef.current.stop();
              
              // Give it a moment to finish the onend callback
              setTimeout(() => {
                console.log(`🎤 Final recognized text (${finalTranscriptRef.current.split(' ').filter(w => w).length} words): "${finalTranscriptRef.current.trim()}"`);
                finishAudioProcessing();
              }, 100);
            } catch (error) {
              console.error('Error stopping recognition:', error);
              finishAudioProcessing();
            }
          } else {
            finishAudioProcessing();
          }
        };

        const finishAudioProcessing = () => {
          // Disconnect audio nodes
          if (scriptProcessorRef.current && audioSourceRef.current) {
            try {
              audioSourceRef.current.disconnect(scriptProcessorRef.current);
              scriptProcessorRef.current.disconnect();
            } catch (e) {
              console.warn('Warning disconnecting audio nodes:', e);
            }
          }

          // Stop stream
          if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => {
              try {
                track.stop();
              } catch (e) {
                console.warn('Warning stopping track:', e);
              }
            });
          }

          // Close audio context
          if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
            try {
              audioContextRef.current.close();
            } catch (e) {
              console.warn('Warning closing audio context:', e);
            }
          }

          // Process audio chunks into WAV
          const totalLength = audioChunksRef.current.reduce((acc, chunk) => acc + chunk.length, 0);
          console.log(`📊 Total samples captured: ${totalLength}`);

        // Check audio amplitude (to detect if microphone is working)
        let maxAmplitude = 0;
        let minAmplitude = 0;
        for (const chunk of audioChunksRef.current) {
          for (let i = 0; i < chunk.length; i++) {
            maxAmplitude = Math.max(maxAmplitude, Math.abs(chunk[i]));
            if (i === 0) minAmplitude = Math.min(minAmplitude, chunk[i]);
          }
        }
        console.log(`🎤 Audio Amplitude Check:`);
        console.log(`   - Max: ${(maxAmplitude * 100).toFixed(2)}%`);
        console.log(`   - Min: ${(minAmplitude * 100).toFixed(2)}%`);
        
        if (maxAmplitude < 0.01) {
          console.warn('⚠️ WARNING: Audio amplitude is very low (< 1%) - audio might be silent or microphone not working!');
          console.warn('   Suggestions: Check microphone volume, permissions, or try different microphone');
        }


          // Combine chunks
          const audioData = new Float32Array(totalLength);
          let offset = 0;
          for (const chunk of audioChunksRef.current) {
            audioData.set(chunk, offset);
            offset += chunk.length;
          }

          // Resample if needed
          const sampleRate = audioContextRef.current?.sampleRate || 48000;
          let audioToEncode: Float32Array = audioData;

          if (sampleRate !== 16000) {
            console.log(`🔄 Resampling from ${sampleRate}Hz to 16000Hz...`);
            const resampled = AudioResampler.resample(audioData, sampleRate, 16000);
            audioToEncode = new Float32Array(resampled);
          }

          // Encode to WAV
          const encoder = new WavEncoder(16000, 1);
          const wavBuffer = encoder.encode(audioToEncode);
          const wavBlob = new Blob([wavBuffer], { type: 'audio/wav' });

          console.log(`✅ WAV created: ${(wavBlob.size / 1024).toFixed(2)} KB`);
          console.log(`✅ Complete recognized text: "${finalTranscriptRef.current.trim()}"`);
          resolve(wavBlob);
        };
      } catch (error) {
        console.error('❌ Error in stopRecording:', error);
        reject(error);
      }
    });
  }, []);

  return {
    isRecording,
    recognizedText,
    startRecording,
    stopRecording,
    getFinalText: () => finalTranscriptRef.current.trim(),
  };
};
