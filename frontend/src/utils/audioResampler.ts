/**
 * Audio Resampler - Resamples audio to 16000 Hz for backend processing
 */

export class AudioResampler {
  /**
   * Resample audio data to target sample rate using linear interpolation
   */
  static resample(
    audioData: Float32Array,
    sourceSampleRate: number,
    targetSampleRate: number = 16000
  ): Float32Array {
    if (sourceSampleRate === targetSampleRate) {
      return audioData;
    }

    const ratio = sourceSampleRate / targetSampleRate;
    const newLength = Math.ceil(audioData.length / ratio);
    const resampled = new Float32Array(newLength);

    let j = 0;
    for (let i = 0; i < newLength; i++) {
      const srcIndex = i * ratio;
      const prevIndex = Math.floor(srcIndex);
      const nextIndex = Math.ceil(srcIndex);
      const fraction = srcIndex - prevIndex;

      if (nextIndex >= audioData.length) {
        resampled[i] = audioData[prevIndex] || 0;
      } else {
        // Linear interpolation
        resampled[i] =
          audioData[prevIndex] * (1 - fraction) +
          audioData[nextIndex] * fraction;
      }
    }

    console.log(
      `📊 Resampled audio: ${audioData.length} samples @ ${sourceSampleRate}Hz -> ${newLength} samples @ ${targetSampleRate}Hz`
    );
    return resampled;
  }
}
