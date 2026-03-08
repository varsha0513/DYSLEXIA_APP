import React, { useState, useRef, useEffect } from 'react';
import './PronunciationTrainingWidget.css';

interface PronunciationTrainingWidgetProps {
  words: string[]; // Words to practice pronunciation
  onComplete?: (results: TrainingResult[]) => void;
}

interface TrainingResult {
  word: string;
  success: boolean;
  attempts: number;
  feedback: string;
}

interface WordTrainingState {
  word: string;
  attempts: number;
  success: boolean;
  feedback: string;
  similarity: number;
  isRecording: boolean;
  isAnalyzing: boolean;
  recognized: string;
  error?: string;
}

// Microphone Visualization Component
const MicrophoneVisualizer: React.FC<{ isRecording: boolean; audioLevel: number }> = ({
  isRecording,
  audioLevel,
}) => {
  const bars = 5; // Number of bars in the visualization
  const maxLevel = 255; // Max audio level

  return (
    <div className={`microphone-visualizer ${isRecording ? 'active' : ''}`}>
      {/* Animated Microphone Icon */}
      <div className="mic-container">
        <div className="mic-icon">🎤</div>
        {isRecording && (
          <>
            <div className="pulse-ring pulse-1" />
            <div className="pulse-ring pulse-2" />
            <div className="pulse-ring pulse-3" />
          </>
        )}
      </div>

      {/* Audio Level Bars */}
      {isRecording && (
        <div className="audio-bars">
          {Array.from({ length: bars }).map((_, index) => {
            // Create a wave effect by offsetting each bar
            const offset = index * 15;
            const calculatedLevel = Math.max(0, audioLevel - offset);
            const barHeight = (calculatedLevel / maxLevel) * 100;

            return (
              <div
                key={index}
                className="audio-bar"
                style={{
                  height: `${Math.min(barHeight, 100)}%`,
                  opacity: Math.max(0.4, barHeight / 100),
                  animation: `barPulse ${0.1 + index * 0.05}s ease-in-out`,
                }}
              />
            );
          })}
        </div>
      )}

      {/* Recording Status Text */}
      {isRecording && <div className="recording-text">Listening...</div>}
    </div>
  );
};

export const PronunciationTrainingWidget: React.FC<PronunciationTrainingWidgetProps> = ({
  words,
  onComplete,
}) => {
  const [currentWordIndex, setCurrentWordIndex] = useState(0);
  const [trainingStates, setTrainingStates] = useState<{ [key: string]: WordTrainingState }>({});
  const [showTraining, setShowTraining] = useState(false);
  const [sessionComplete, setSessionComplete] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const dataArrayRef = useRef<Uint8Array | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const animationFrameRef = useRef<number | null>(null);

  const currentWord = words[currentWordIndex];

  useEffect(() => {
    // Initialize training states for all words
    const initialStates: { [key: string]: WordTrainingState } = {};
    words.forEach(word => {
      initialStates[word] = {
        word,
        attempts: 0,
        success: false,
        feedback: '',
        similarity: 0,
        isRecording: false,
        isAnalyzing: false,
        recognized: '',
      };
    });
    setTrainingStates(initialStates);
  }, [words]);

  const startRecording = async () => {
    try {
      console.log(`🎤 Starting recording for: ${currentWord}`);

      // Get microphone access
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 16000,
        },
      });

      streamRef.current = stream;

      // Create Audio Context for visualization
      const audioContext = window.AudioContext || (window as any).webkitAudioContext;
      audioContextRef.current = new audioContext();
      
      const analyser = audioContextRef.current.createAnalyser();
      analyser.fftSize = 256;
      analyserRef.current = analyser;

      const source = audioContextRef.current.createMediaStreamSource(stream);
      source.connect(analyser);

      // Set up data array for audio levels
      const bufferLength = analyser.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);
      dataArrayRef.current = dataArray;

      // Function to update audio level visualization
      const updateAudioLevel = () => {
        if (analyserRef.current && dataArrayRef.current) {
          analyserRef.current.getByteFrequencyData(dataArrayRef.current as any);
          
          // Get average frequency (RMS-like calculation)
          let sum = 0;
          for (let i = 0; i < dataArrayRef.current.length; i++) {
            sum += dataArrayRef.current[i];
          }
          const average = sum / dataArrayRef.current.length;
          
          setAudioLevel(average);
          animationFrameRef.current = requestAnimationFrame(updateAudioLevel);
        }
      };

      // Start updating audio level
      updateAudioLevel();

      // Create MediaRecorder
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm',
      });

      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = () => {
        // Cancel animation frame
        if (animationFrameRef.current) {
          cancelAnimationFrame(animationFrameRef.current);
          animationFrameRef.current = null;
        }

        // Convert to WAV format that backend expects
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        processAudio(audioBlob);

        // Clean up
        stream.getTracks().forEach(track => track.stop());
        streamRef.current = null;
        setAudioLevel(0);
      };

      mediaRecorder.start();
      mediaRecorderRef.current = mediaRecorder;

      // Update UI state
      setTrainingStates(prev => ({
        ...prev,
        [currentWord]: {
          ...prev[currentWord],
          isRecording: true,
          error: undefined,
        },
      }));
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Failed to access microphone';
      console.error('❌ Recording error:', error);
      setTrainingStates(prev => ({
        ...prev,
        [currentWord]: {
          ...prev[currentWord],
          error: `Microphone access denied: ${errorMsg}`,
        },
      }));
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      console.log(`⏹ Stopping recording for: ${currentWord}`);
      mediaRecorderRef.current.stop();
    }
  };

  const processAudio = async (audioBlob: Blob) => {
    try {
      setTrainingStates(prev => ({
        ...prev,
        [currentWord]: {
          ...prev[currentWord],
          isRecording: false,
          isAnalyzing: true,
        },
      }));

      // Convert WebM to WAV using audio context
      const arrayBuffer = await audioBlob.arrayBuffer();
      const audioContext = window.AudioContext || (window as any).webkitAudioContext;
      const ctx = new audioContext();

      const audioBuffer = await ctx.decodeAudioData(arrayBuffer);

      // Convert to WAV
      const wavBlob = await audioBufferToWav(audioBuffer);

      // Send to backend for pronunciation check
      const formData = new FormData();
      formData.append('word', currentWord);
      formData.append('audio_file', wavBlob, 'pronunciation.wav');

      console.log(`📤 Sending pronunciation check for: ${currentWord}`);
      const response = await fetch('http://localhost:8000/pronunciation/check', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Backend error: ${response.statusText}`);
      }

      const result = await response.json();
      console.log(`✅ Pronunciation check result:`, result);

      // Update training state with result
      const newAttempt = trainingStates[currentWord].attempts + 1;
      setTrainingStates(prev => ({
        ...prev,
        [currentWord]: {
          ...prev[currentWord],
          isAnalyzing: false,
          attempts: newAttempt,
          success: result.is_correct,
          feedback: result.feedback,
          similarity: result.similarity_ratio,
          recognized: result.recognized,
          error: undefined,
        },
      }));
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Processing failed';
      console.error('❌ Audio processing error:', error);
      setTrainingStates(prev => ({
        ...prev,
        [currentWord]: {
          ...prev[currentWord],
          isRecording: false,
          isAnalyzing: false,
          error: `Failed to analyze: ${errorMsg}`,
        },
      }));
    }
  };

  const audioBufferToWav = async (audioBuffer: AudioBuffer): Promise<Blob> => {
    const numberOfChannels = audioBuffer.numberOfChannels;
    const sampleRate = audioBuffer.sampleRate;
    const frameLength = audioBuffer.length;
    const channelData = audioBuffer.getChannelData(0);

    // PCM encoding
    const scaleTo16Bit = (sample: number) => {
      sample = Math.max(-1, Math.min(1, sample)); // Clamp to [-1, 1]
      return sample < 0 ? sample * 0x8000 : sample * 0x7fff;
    };

    const pcmData = new Int16Array(frameLength);
    for (let i = 0; i < frameLength; i++) {
      pcmData[i] = scaleTo16Bit(channelData[i]);
    }

    // WAV header
    const wavHeader = createWavHeader(sampleRate, numberOfChannels, pcmData.byteLength);
    const wavData = new Uint8Array(wavHeader.byteLength + pcmData.byteLength);
    wavData.set(new Uint8Array(wavHeader), 0);
    wavData.set(new Uint8Array(pcmData.buffer), wavHeader.byteLength);

    return new Blob([wavData], { type: 'audio/wav' });
  };

  const createWavHeader = (sampleRate: number, channels: number, dataSize: number): ArrayBuffer => {
    const buffer = new ArrayBuffer(44);
    const view = new DataView(buffer);

    const writeString = (offset: number, string: string) => {
      for (let i = 0; i < string.length; i++) {
        view.setUint8(offset + i, string.charCodeAt(i));
      }
    };

    // WAV header
    writeString(0, 'RIFF');
    view.setUint32(4, 36 + dataSize, true);
    writeString(8, 'WAVE');
    writeString(12, 'fmt ');
    view.setUint32(16, 16, true); // Subchunk1Size
    view.setUint16(20, 1, true); // AudioFormat (1 = PCM)
    view.setUint16(22, channels, true); // NumChannels
    view.setUint32(24, sampleRate, true); // SampleRate
    view.setUint32(28, sampleRate * channels * 2, true); // ByteRate
    view.setUint16(32, channels * 2, true); // BlockAlign
    view.setUint16(34, 16, true); // BitsPerSample
    writeString(36, 'data');
    view.setUint32(40, dataSize, true);

    return buffer;
  };

  const playWordPronunciation = async () => {
    try {
      const formData = new FormData();
      formData.append('word', currentWord);

      const response = await fetch(
        'http://localhost:8000/pronunciation/word-audio',
        {
          method: 'POST',
          body: formData,
        }
      );

      if (!response.ok) {
        console.error(`HTTP ${response.status}: ${response.statusText}`);
        throw new Error('Failed to get pronunciation');
      }

      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);
      
      const audio = new Audio(audioUrl);
      await audio.play();

      // Clean up URL after playing
      audio.onended = () => {
        URL.revokeObjectURL(audioUrl);
      };
    } catch (error) {
      console.error('❌ Failed to play pronunciation:', error);
      alert('Failed to play pronunciation. Please check backend is running.');
    }
  };

  const moveToNextWord = () => {
    if (currentWordIndex < words.length - 1) {
      setCurrentWordIndex(currentWordIndex + 1);
    } else {
      // Training session complete
      setSessionComplete(true);
      if (onComplete) {
        onComplete(
          words.map(word => ({
            word,
            success: trainingStates[word]?.success || false,
            attempts: trainingStates[word]?.attempts || 0,
            feedback: trainingStates[word]?.feedback || '',
          }))
        );
      }
    }
  };

  const resetWord = () => {
    setTrainingStates(prev => ({
      ...prev,
      [currentWord]: {
        ...prev[currentWord],
        attempts: 0,
        success: false,
        feedback: '',
        similarity: 0,
        recognized: '',
        error: undefined,
      },
    }));
  };

  if (words.length === 0) {
    return null;
  }

  if (sessionComplete) {
    const successCount = words.filter(w => trainingStates[w]?.success).length;
    return (
      <div className="pronunciation-training-widget">
        <div className="completion-card">
          <h2>🎉 Training Session Complete!</h2>
          <div className="completion-stats">
            <p>
              You successfully mastered <strong>{successCount}</strong> out of{' '}
              <strong>{words.length}</strong> words.
            </p>
            {successCount === words.length && (
              <p className="perfect-score">
                ⭐ Perfect! You did an excellent job!
              </p>
            )}
          </div>
          <button
            className="btn btn-primary"
            onClick={() => {
              setSessionComplete(false);
              setCurrentWordIndex(0);
              setTrainingStates(prev => {
                const reset: typeof prev = {};
                words.forEach(word => {
                  reset[word] = {
                    word,
                    attempts: 0,
                    success: false,
                    feedback: '',
                    similarity: 0,
                    isRecording: false,
                    isAnalyzing: false,
                    recognized: '',
                  };
                });
                return reset;
              });
            }}
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  const state = trainingStates[currentWord];

  if (!state) {
    return null;
  }

  return (
    <div className="pronunciation-training-widget">
      {!showTraining ? (
        <div className="training-intro">
          <h2>🎯 Pronunciation Training</h2>
          <p>
            Let's practice pronouncing the words you had trouble with. I'll help you learn the
            correct pronunciation!
          </p>
          <div className="word-count">
            Words to practice: <strong>{words.length}</strong>
          </div>
          <button className="btn btn-primary" onClick={() => setShowTraining(true)}>
            Start Training
          </button>
        </div>
      ) : (
        <div className="training-session">
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{
                width: `${((currentWordIndex + 1) / words.length) * 100}%`,
              }}
            />
          </div>

          <div className="current-word-section">
            <div className="word-counter">
              Word {currentWordIndex + 1} of {words.length}
            </div>

            <div className="target-word">
              <span className="label">Practice pronouncing:</span>
              <span className="word">{currentWord}</span>
            </div>

            {/* Hear pronunciation button */}
            <button
              className="btn btn-hear-it"
              onClick={playWordPronunciation}
              title="Click to hear the correct pronunciation"
            >
              🔊 Hear It
            </button>

            {/* Recording section */}
            <div className="recording-section">
              <p className="instruction">Ready? Click the button below and say the word:</p>

              {state.isRecording ? (
                <button className="btn btn-recording" onClick={stopRecording}>
                  ⏹ Stop Recording
                </button>
              ) : (
                <button
                  className="btn btn-record"
                  onClick={startRecording}
                  disabled={state.isAnalyzing}
                >
                  {state.isAnalyzing ? '⏳ Analyzing...' : '🎤 Record'}
                </button>
              )}

              {/* Microphone visualizer */}
              <MicrophoneVisualizer isRecording={state.isRecording} audioLevel={audioLevel} />

              {/* Error message */}
              {state.error && <div className="error-message">{state.error}</div>}

              {/* Feedback from pronunciation check */}
              {state.feedback && (
                <div className={`feedback ${state.success ? 'success' : 'retry'}`}>
                  <p className="feedback-text">{state.feedback}</p>
                  {state.recognized && (
                    <p className="recognized-text">
                      You said: <strong>{state.recognized}</strong>
                    </p>
                  )}
                  <p className="similarity">
                    Similarity: <strong>{(state.similarity * 100).toFixed(0)}%</strong>
                  </p>
                  <p className="attempt-counter">
                    Attempt: <strong>{state.attempts}</strong>
                  </p>
                </div>
              )}

              {/* Navigation buttons */}
              <div className="button-group">
                {state.success && (
                  <button
                    className="btn btn-next"
                    onClick={moveToNextWord}
                    title="Move to next word"
                  >
                    ✅ Next Word
                  </button>
                )}

                {!state.success && state.feedback && (
                  <button
                    className="btn btn-retry"
                    onClick={resetWord}
                    title="Try again"
                  >
                    🔄 Try Again
                  </button>
                )}

                {state.attempts >= 3 && !state.success && (
                  <button
                    className="btn btn-skip"
                    onClick={moveToNextWord}
                    title="Skip to next word"
                  >
                    ⏭ Skip
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
