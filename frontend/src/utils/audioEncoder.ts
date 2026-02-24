/**
 * WAV Encoder - Converts raw audio data to WAV format
 * Required for backend audio processing
 */

export class WavEncoder {
  private sampleRate: number;
  private numChannels: number;

  constructor(sampleRate: number = 16000, numChannels: number = 1) {
    this.sampleRate = sampleRate;
    this.numChannels = numChannels;
    console.log(`🔧 WavEncoder initialized: ${sampleRate}Hz, ${numChannels} channel(s)`);
  }

  /**
   * Encode PCM data to WAV format
   */
  encode(audioData: Float32Array): ArrayBuffer {
    console.log(`📦 Encoding ${audioData.length} samples...`);
    
    if (audioData.length === 0) {
      throw new Error('Audio data is empty');
    }

    const pcmData = this.floatTo16BitPCM(audioData);
    const wavBuffer = this.createWavFile(pcmData);
    
    console.log(`✅ WAV encoding complete: ${(wavBuffer.byteLength / 1024).toFixed(2)} KB`);
    return wavBuffer;
  }

  /**
   * Convert Float32 audio to 16-bit PCM
   */
  private floatTo16BitPCM(float32Data: Float32Array): Int16Array {
    const int16Data = new Int16Array(float32Data.length);
    
    for (let i = 0; i < float32Data.length; i++) {
      let s = Math.max(-1, Math.min(1, float32Data[i]));
      int16Data[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
    }
    
    return int16Data;
  }

  /**
   * Create WAV file with proper headers
   */
  private createWavFile(pcmData: Int16Array): ArrayBuffer {
    const frameLength = pcmData.length;
    const numberOfChannels = this.numChannels;
    const sampleRate = this.sampleRate;
    const byteRate = sampleRate * numberOfChannels * 2;
    const blockAlign = numberOfChannels * 2;

    const wavLength = 36 + frameLength * numberOfChannels * 2;
    const arrayBuffer = new ArrayBuffer(44 + frameLength * numberOfChannels * 2);
    const view = new DataView(arrayBuffer);

    // WAV file header
    const writeString = (offset: number, string: string) => {
      for (let i = 0; i < string.length; i++) {
        view.setUint8(offset + i, string.charCodeAt(i));
      }
    };

    writeString(0, 'RIFF');
    view.setUint32(4, wavLength, true);
    writeString(8, 'WAVE');

    writeString(12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true); // PCM
    view.setUint16(22, numberOfChannels, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, byteRate, true);
    view.setUint16(32, blockAlign, true);
    view.setUint16(34, 16, true); // 16-bit

    writeString(36, 'data');
    view.setUint32(40, frameLength * numberOfChannels * 2, true);

    // Write PCM data
    let offset = 44;
    for (let i = 0; i < pcmData.length; i++) {
      view.setInt16(offset, pcmData[i], true);
      offset += 2;
    }

    return arrayBuffer;
  }
}

/**
 * Get raw PCM data from MediaRecorder stream
 * This approach uses ScriptProcessorNode for direct audio capture
 */
export class AudioCapture {
  private audioContext: AudioContext | null = null;
  private mediaStreamAudioSource: MediaStreamAudioSource | null = null;
  private scriptProcessor: ScriptProcessorNode | null = null;
  private audioChunks: Float32Array[] = [];
  private isRecording = false;

  async startCapture(stream: MediaStream): Promise<void> {
    this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
    this.mediaStreamAudioSource = this.audioContext.createMediaStreamSource(stream);

    // Use ScriptProcessorNode for older browsers or AudioWorklet for newer ones
    this.scriptProcessor = this.audioContext.createScriptProcessor(4096, 1, 1);

    this.scriptProcessor.onaudioprocess = (event: AudioProcessingEvent) => {
      if (this.isRecording) {
        const inputData = event.inputBuffer.getChannelData(0);
        this.audioChunks.push(new Float32Array(inputData));
      }
    };

    this.mediaStreamAudioSource.connect(this.scriptProcessor);
    this.scriptProcessor.connect(this.audioContext.destination);
    this.isRecording = true;
  }

  stopCapture(): Blob {
    this.isRecording = false;

    if (this.scriptProcessor && this.mediaStreamAudioSource) {
      this.mediaStreamAudioSource.disconnect(this.scriptProcessor);
      this.scriptProcessor.disconnect();
    }

    if (this.audioContext) {
      this.audioContext.close();
    }

    // Concatenate all audio chunks
    const totalLength = this.audioChunks.reduce((acc, chunk) => acc + chunk.length, 0);
    const audioData = new Float32Array(totalLength);
    let offset = 0;

    for (const chunk of this.audioChunks) {
      audioData.set(chunk, offset);
      offset += chunk.length;
    }

    // Encode to WAV
    const encoder = new WavEncoder(this.audioContext?.sampleRate || 16000, 1);
    const wavBuffer = encoder.encode(audioData);
    return new Blob([wavBuffer], { type: 'audio/wav' });
  }
}
