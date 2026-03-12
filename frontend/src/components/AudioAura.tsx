import React, { useEffect, useRef } from 'react';
import './AudioAura.css';

interface AudioAuraProps {
  isRecording: boolean;
  analyser: AnalyserNode | null;
  size?: 'small' | 'medium' | 'large';
}

export const AudioAura: React.FC<AudioAuraProps> = ({
  isRecording,
  analyser,
  size = 'medium',
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationIdRef = useRef<number | null>(null);
  const volumeRef = useRef<number>(0);
  const frequencyDataRef = useRef<Uint8Array | null>(null);
  const smoothedFrequencyRef = useRef<number[]>([]);

  useEffect(() => {
    if (!isRecording || !analyser) {
      if (animationIdRef.current) {
        cancelAnimationFrame(animationIdRef.current);
      }
      return;
    }

    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    const dpr = window.devicePixelRatio || 1;
    canvas.width = canvas.offsetWidth * dpr;
    canvas.height = canvas.offsetHeight * dpr;
    ctx.scale(dpr, dpr);

    // FFT size for frequency analysis
    analyser.fftSize = 512;
    const bufferLength = analyser.frequencyBinCount;
    frequencyDataRef.current = new Uint8Array(bufferLength);
    
    // Initialize smoothed frequency array with fewer points for clarity
    const numBars = 64;
    smoothedFrequencyRef.current = new Array(numBars).fill(0);

    const animate = () => {
      if (!analyser || !frequencyDataRef.current || !canvas.offsetWidth) return;

      // Get frequency data
      analyser.getByteFrequencyData(frequencyDataRef.current as any);

      // Get time domain for volume detection
      const timeDomainData = new Uint8Array(analyser.frequencyBinCount);
      analyser.getByteTimeDomainData(timeDomainData as any);

      // Calculate RMS (volume)
      let sum = 0;
      for (let i = 0; i < timeDomainData.length; i++) {
        const val = (timeDomainData[i] - 128) / 128;
        sum += val * val;
      }
      const rms = Math.sqrt(sum / timeDomainData.length);
      volumeRef.current = Math.min(rms, 1);

      // Downsample frequency data to number of bars and smooth
      const numBars = smoothedFrequencyRef.current.length;
      for (let i = 0; i < numBars; i++) {
        // Map bar index to frequency bin range
        const binStart = Math.floor((i / numBars) * frequencyDataRef.current.length);
        const binEnd = Math.floor(((i + 1) / numBars) * frequencyDataRef.current.length);
        
        // Average frequency values in this range
        let sum = 0;
        for (let j = binStart; j < binEnd; j++) {
          sum += frequencyDataRef.current[j];
        }
        const average = sum / (binEnd - binStart);
        
        // Exponential smoothing for smooth transitions
        smoothedFrequencyRef.current[i] =
          smoothedFrequencyRef.current[i] * 0.7 + (average / 255) * 0.3;
      }

      const baseY = canvas.offsetHeight * 0.7;
      const volume = volumeRef.current;

      // Clear canvas
      ctx.fillStyle = 'rgba(26, 26, 26, 0.95)';
      ctx.fillRect(0, 0, canvas.offsetWidth, canvas.offsetHeight);

      // Draw frequency bars as an interactive wave
      const barWidth = canvas.offsetWidth / numBars;

      for (let i = 0; i < numBars; i++) {
        const x = i * barWidth;
        const freqValue = smoothedFrequencyRef.current[i];
        
        // Height based directly on frequency (0 to 200 pixels)
        const barHeight = freqValue * 200;
        
        // Position: draws upward from baseline
        const y = baseY - barHeight;

        // Create gradient for each bar based on frequency
        const hue = (i / numBars) * 240 + 240; // Purple to Blue range
        const saturation = 100;
        const lightness = 50 + freqValue * 30; // Brighter when louder

        // Draw the bar as a smooth wave
        ctx.beginPath();
        
        if (i === 0) {
          ctx.moveTo(x, baseY);
        } else {
          ctx.lineTo(x, y);
        }

        // Add curve for smoothness
        const nextI = Math.min(i + 1, numBars - 1);
        const nextFreqValue = smoothedFrequencyRef.current[nextI];
        const nextBarHeight = nextFreqValue * 200;
        const nextY = baseY - nextBarHeight;
        
        ctx.quadraticCurveTo(
          x + barWidth / 2,
          (y + nextY) / 2,
          x + barWidth,
          nextY
        );

        // Gradient line
        const gradientColor = `hsl(${hue}, ${saturation}%, ${lightness}%)`;
        ctx.strokeStyle = gradientColor;
        ctx.lineWidth = barWidth * 1.2;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        ctx.stroke();

        // Fill area under the wave
        ctx.beginPath();
        ctx.moveTo(x, baseY);
        ctx.lineTo(x, y);
        ctx.lineTo(x + barWidth, nextY);
        ctx.lineTo(x + barWidth, baseY);
        ctx.closePath();

        // Fill with semi-transparent gradient based on frequency
        const opacity = 0.3 + freqValue * 0.5;
        ctx.fillStyle = `hsla(${hue}, ${saturation}%, ${lightness}%, ${opacity})`;
        ctx.fill();
      }

      // Draw bottom baseline
      ctx.strokeStyle = 'rgba(200, 130, 200, 0.3)';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(0, baseY);
      ctx.lineTo(canvas.offsetWidth, baseY);
      ctx.stroke();

      // Draw glow effect based on volume
      if (volume > 0.1) {
        ctx.strokeStyle = `rgba(200, 130, 200, ${volume * 0.3})`;
        ctx.lineWidth = 15;
        ctx.beginPath();
        ctx.moveTo(0, baseY);
        ctx.lineTo(canvas.offsetWidth, baseY);
        ctx.stroke();
      }

      animationIdRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      if (animationIdRef.current) {
        cancelAnimationFrame(animationIdRef.current);
      }
    };
  }, [isRecording, analyser]);

  const sizeClasses = {
    small: 'audio-aura-small',
    medium: 'audio-aura-medium',
    large: 'audio-aura-large',
  };

  return (
    <div className={`audio-aura-container ${sizeClasses[size]} ${isRecording ? 'recording' : ''}`}>
      <canvas ref={canvasRef} className="audio-aura-canvas" />
      {isRecording && (
        <div className="aura-pulse-text">
          <span className="pulse-dot"></span>
          Listening...
        </div>
      )}
    </div>
  );
};
