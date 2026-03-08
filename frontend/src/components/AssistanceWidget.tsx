import React, { useState, useRef, useEffect } from 'react';
import { AssistanceData } from '../types';
import './AssistanceWidget.css';

interface AssistanceWidgetProps {
  assistance: AssistanceData;
}

interface AudioState {
  [key: string]: boolean;
}

interface AudioCache {
  [key: string]: {
    blob: Blob;
    url: string;
  };
}

export const AssistanceWidget: React.FC<AssistanceWidgetProps> = ({ assistance }) => {
  const [playingAudio, setPlayingAudio] = useState<AudioState>({});
  const [loadingAudio, setLoadingAudio] = useState<AudioState>({});
  const [audioCache, setAudioCache] = useState<AudioCache>({});
  const audioRefs = useRef<{ [key: string]: HTMLAudioElement }>({});
  const abortControllersRef = useRef<{ [key: string]: AbortController }>({});

  if (!assistance.has_errors || !assistance.assistance_enabled) {
    return null;
  }

  // Create audio elements only once on mount
  useEffect(() => {
    return () => {
      // Cleanup: revoke all object URLs on unmount
      Object.values(audioCache).forEach(audio => {
        URL.revokeObjectURL(audio.url);
      });
      // Cleanup: abort all pending requests
      Object.values(abortControllersRef.current).forEach(controller => {
        try {
          controller.abort();
        } catch (e) {
          // Ignore abort errors
        }
      });
    };
  }, [audioCache]);

  const playAudio = (audioElement: HTMLAudioElement, audioUrl: string, key: string) => {
    audioElement.src = audioUrl;
    audioElement.load();
    
    // Play once the audio is ready
    const playHandler = () => {
      audioElement.play().catch(err => {
        console.error('❌ Audio play error:', err);
      });
      audioElement.removeEventListener('canplay', playHandler);
    };
    
    audioElement.addEventListener('canplay', playHandler);
  };

  const stopAllAudio = () => {
    // Stop any currently playing audio
    Object.entries(audioRefs.current).forEach(([key, audioElement]) => {
      if (audioElement && !audioElement.paused) {
        audioElement.pause();
        audioElement.currentTime = 0;
      }
    });
    setPlayingAudio({});
  };

  const playWordPronunciation = async (correctWord: string) => {
    const key = `correct-${correctWord}`;
    
    try {
      // Stop any other audio that's currently playing
      stopAllAudio();

      // Cancel any previous pending request for this word
      if (abortControllersRef.current[key]) {
        abortControllersRef.current[key].abort();
      }

      // Check if audio is already cached
      if (audioCache[key]) {
        // Audio already generated, just play it
        if (!audioRefs.current[key]) {
          audioRefs.current[key] = new Audio();
          audioRefs.current[key].onplay = () => {
            setPlayingAudio(prev => ({ ...prev, [key]: true }));
          };
          audioRefs.current[key].onended = () => {
            setPlayingAudio(prev => ({ ...prev, [key]: false }));
          };
        }
        audioRefs.current[key].currentTime = 0;
        playAudio(audioRefs.current[key], audioCache[key].url, key);
        return;
      }

      // Need to fetch audio from backend
      setLoadingAudio(prev => ({ ...prev, [key]: true }));
      
      // Create a new abort controller for this request
      const controller = new AbortController();
      abortControllersRef.current[key] = controller;
      
      const formData = new FormData();
      formData.append('word', correctWord);
      
      console.log(`🔊 Fetching audio for: ${correctWord}`);
      const response = await fetch('http://localhost:8000/tts/word', {
        method: 'POST',
        body: formData,
        signal: controller.signal
      });

      if (!response.ok) {
        console.error('❌ Failed to generate audio:', response.statusText);
        setLoadingAudio(prev => ({ ...prev, [key]: false }));
        alert(`Failed to generate audio for "${correctWord}". Please check backend is running.`);
        return;
      }

      const audioBlob = await response.blob();
      console.log(`✅ Audio received: ${(audioBlob.size / 1024).toFixed(2)}KB`);
      
      const audioUrl = URL.createObjectURL(audioBlob);

      // Cache the audio
      setAudioCache(prev => ({
        ...prev,
        [key]: { blob: audioBlob, url: audioUrl }
      }));

      // Create audio element if it doesn't exist
      if (!audioRefs.current[key]) {
        audioRefs.current[key] = new Audio();
        audioRefs.current[key].onplay = () => {
          setPlayingAudio(prev => ({ ...prev, [key]: true }));
        };
        audioRefs.current[key].onended = () => {
          setPlayingAudio(prev => ({ ...prev, [key]: false }));
        };
      }

      setLoadingAudio(prev => ({ ...prev, [key]: false }));
      playAudio(audioRefs.current[key], audioUrl, key);
      
      // Clean up abort controller reference after successful completion
      delete abortControllersRef.current[key];
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        console.log(`⚠️ Audio fetch cancelled for: ${correctWord}`);
      } else {
        console.error('❌ Error playing audio:', error);
        alert('Error generating audio. Check console for details.');
      }
      setLoadingAudio(prev => ({ ...prev, [key]: false }));
    }
  };

  const stopAudio = (correctWord: string) => {
    stopAllAudio();
  };

  return (
    <div className="assistance-widget">
      <div className="assistance-header">
        <h2>🆘 Learning Assistance</h2>
        <p className="assistance-subtitle">
          Listen to correct pronunciations and practice these words
        </p>
      </div>

      {/* Word Errors Section */}
      {assistance.wrong_words && assistance.wrong_words.length > 0 && (
        <div className="assistance-section">
          <h3 className="section-title">❌ Words You Misread</h3>
          <div className="word-errors-list">
            {assistance.wrong_words.map(([spokenWord, correctWord], index) => {
              const key = `correct-${correctWord}`;
              const isPlaying = playingAudio[key] || false;
              const isLoading = loadingAudio[key] || false;

              return (
                <div key={index} className="word-error-item">
                  <div className="error-content">
                    <div className="word-comparison">
                      <div className="word-box wrong">
                        <span className="label">You said:</span>
                        <span className="word">{spokenWord}</span>
                      </div>
                      <div className="arrow">→</div>
                      <div className="word-box correct">
                        <span className="label">Correct:</span>
                        <span className="word">{correctWord}</span>
                      </div>
                    </div>
                  </div>

                  <div className="audio-controls-wrapper">
                    <div className="audio-controls">
                      {isPlaying ? (
                        <button
                          className="btn-play playing"
                          onClick={() => stopAudio(correctWord)}
                          title="Stop playback"
                        >
                          ⏹ Stop
                        </button>
                      ) : (
                        <button
                          className="btn-play"
                          onClick={() => playWordPronunciation(correctWord)}
                          disabled={isLoading}
                          title="Play pronunciation"
                        >
                          {isLoading ? '⏳' : '🔊'} {isLoading ? 'Loading...' : 'Hear it'}
                        </button>
                      )}
                    </div>
                    {isPlaying && (
                      <button
                        className="btn-replay"
                        onClick={() => playWordPronunciation(correctWord)}
                        title="Replay pronunciation"
                      >
                        🔄 Repeat
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Missing Words Section */}
      {assistance.missing_words && assistance.missing_words.length > 0 && (
        <div className="assistance-section">
          <h3 className="section-title">⚠ Words You Skipped</h3>
          <div className="missing-words-list">
            {assistance.missing_words.map((word, index) => {
              const key = `missing-${word}`;
              const isPlaying = playingAudio[key] || false;
              const isLoading = loadingAudio[key] || false;

              return (
                <div key={index} className="missing-word-item">
                  <div className="word-box missing">
                    <span className="label">Missing word:</span>
                    <span className="word">{word}</span>
                  </div>
                  <div className="audio-controls-wrapper">
                    <div className="audio-controls">
                      {isPlaying ? (
                        <button
                          className="btn-play playing"
                          onClick={() => stopAudio(word)}
                          title="Stop playback"
                        >
                          ⏹ Stop
                        </button>
                      ) : (
                        <button
                          className="btn-play"
                          onClick={() => playWordPronunciation(word)}
                          disabled={isLoading}
                          title="Play pronunciation"
                        >
                          {isLoading ? '⏳' : '🔊'} {isLoading ? 'Loading...' : 'Hear it'}
                        </button>
                      )}
                    </div>
                    {isPlaying && (
                      <button
                        className="btn-replay"
                        onClick={() => playWordPronunciation(word)}
                        title="Replay pronunciation"
                      >
                        🔄 Repeat
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Practice Instructions */}
      <div className="practice-guide">
        <h3>📖 How to Practice</h3>
        <ol className="practice-steps">
          <li>👂 Click <strong>"Hear it"</strong> to listen to each word</li>
          <li>🔄 While playing, click <strong>"Repeat"</strong> to hear it again</li>
          <li>📖 Read the paragraph aloud, focusing on these words</li>
          <li>🎯 Try the assessment again to check your progress</li>
        </ol>
      </div>

      <div className="motivation">
        <p>✨ Great effort! With practice, you'll master these words!</p>
      </div>
    </div>
  );
};
