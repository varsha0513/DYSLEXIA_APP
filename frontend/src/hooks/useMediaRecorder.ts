import { useState, useRef, useCallback } from 'react';

export const useMediaRecorder = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [recognizedText, setRecognizedText] = useState('');
  const recognitionRef = useRef<any>(null);

  const startRecording = useCallback(() => {
    setIsRecording(true);
    let finalTranscript = '';

    // Try to use Web Speech API for live recognition
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (SpeechRecognition) {
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.lang = 'en-US';
      recognitionRef.current.interimResults = true;
      recognitionRef.current.continuous = true;

      recognitionRef.current.onresult = (event: any) => {
        let interimTranscript = '';

        // Process only new results starting from resultIndex
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;

          if (event.results[i].isFinal) {
            // Only add final results once
            finalTranscript += transcript + ' ';
          } else {
            // Collect interim results for preview
            interimTranscript += transcript;
          }
        }

        // Update display: final text + interim preview (no duplication)
        setRecognizedText(finalTranscript + interimTranscript);
      };

      recognitionRef.current.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
      };

      recognitionRef.current.onend = () => {
        // Clean up final transcript at session end
        finalTranscript = '';
      };

      try {
        recognitionRef.current.start();
      } catch (error) {
        console.error('Error starting recognition:', error);
      }
    }
  }, []);

  const stopRecording = useCallback(() => {
    setIsRecording(false);

    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (error) {
        console.error('Error stopping recognition:', error);
      }
    }
  }, []);

  return {
    isRecording,
    recognizedText,
    startRecording,
    stopRecording,
  };
};
