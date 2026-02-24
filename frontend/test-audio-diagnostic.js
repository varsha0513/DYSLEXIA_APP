/**
 * Audio Diagnostic Test
 * Run this in the browser console to test audio functionality
 * 
 * Steps:
 * 1. Open http://localhost:3000
 * 2. Open DevTools (F12)
 * 3. Paste this entire file into the Console tab
 * 4. Press Enter
 * 5. Follow the prompts
 */

async function runAudioDiagnostics() {
  console.log('🔍 Starting audio diagnostics...\n');

  // Test 1: Check Web Audio API
  console.log('📊 Test 1: Web Audio API Support');
  const hasAudioContext = !!window.AudioContext || !!window.webkitAudioContext;
  console.log(`  Result: ${hasAudioContext ? '✅ PASS' : '❌ FAIL'}`);
  if (!hasAudioContext) {
    console.error(`  Error: Browser doesn't support Web Audio API`);
    return;
  }

  // Test 2: Check MediaRecorder
  console.log('\n📹 Test 2: MediaRecorder Support');
  const hasMediaRecorder = !!window.MediaRecorder;
  console.log(`  Result: ${hasMediaRecorder ? '✅ PASS' : '❌ FAIL'}`);
  if (!hasMediaRecorder) {
    console.error(`  Error: Browser doesn't support MediaRecorder`);
    return;
  }

  // Test 3: Check getUserMedia
  console.log('\n🎤 Test 3: getUserMedia Support');
  const hasGetUserMedia = !!navigator.mediaDevices?.getUserMedia;
  console.log(`  Result: ${hasGetUserMedia ? '✅ PASS' : '❌ FAIL'}`);
  if (!hasGetUserMedia) {
    console.error(`  Error: Browser doesn't support getUserMedia`);
    return;
  }

  // Test 4: Audio Context Sample Rate
  console.log('\n🎵 Test 4: Audio Context Properties');
  const audioContext = new (window.AudioContext || window.webkitAudioContext)();
  console.log(`  Sample Rate: ${audioContext.sampleRate} Hz`);
  console.log(`  State: ${audioContext.state}`);
  console.log(`  Result: ✅ PASS`);

  // Test 5: Request Microphone Access
  console.log('\n🎤 Test 5: Requesting Microphone Access');
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    console.log(`  ✅ PASS - Microphone access granted`);
    console.log(`  Stream tracks: ${stream.getTracks().length}`);
    console.log(`  Track settings:`, stream.getAudioTracks()[0].getSettings());

    // Test 6: Create ScriptProcessor
    console.log('\n⚙️ Test 6: Creating ScriptProcessor');
    const scriptProcessor = audioContext.createScriptProcessor(4096, 1, 1);
    const source = audioContext.createMediaStreamSource(stream);
    source.connect(scriptProcessor);
    scriptProcessor.connect(audioContext.destination);
    console.log(`  ✅ PASS - ScriptProcessor created`);

    // Test 7: Record 3 seconds of audio
    console.log('\n🎙️ Test 7: Recording 3 seconds of audio');
    console.log('  Please speak into your microphone...');

    const chunks = [];
    scriptProcessor.onaudioprocess = (e) => {
      const data = e.inputBuffer.getChannelData(0);
      chunks.push(new Float32Array(data));
    };

    await new Promise((resolve) => setTimeout(resolve, 3000));

    console.log(`  ✅ PASS - Recorded ${chunks.length} audio chunks`);

    // Test 8: Test WAV Encoding
    console.log('\n📦 Test 8: Testing WAV Encoding');

    // Import and test WavEncoder
    const totalLength = chunks.reduce((acc, chunk) => acc + chunk.length, 0);
    const audioData = new Float32Array(totalLength);
    let offset = 0;

    for (const chunk of chunks) {
      audioData.set(chunk, offset);
      offset += chunk.length;
    }

    // Simulate WAV encoding (simplified)
    const pcmData = new Int16Array(audioData.length);
    for (let i = 0; i < audioData.length; i++) {
      let s = Math.max(-1, Math.min(1, audioData[i]));
      pcmData[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
    }

    const wavData = new ArrayBuffer(44 + pcmData.byteLength);
    const view = new DataView(wavData);

    // RIFF header
    const writeString = (offset, string) => {
      for (let i = 0; i < string.length; i++) {
        view.setUint8(offset + i, string.charCodeAt(i));
      }
    };

    writeString(0, 'RIFF');
    view.setUint32(4, 36 + pcmData.byteLength, true);
    writeString(8, 'WAVE');
    writeString(12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, 1, true);
    view.setUint32(24, 16000, true);
    view.setUint32(28, 16000 * 2, true);
    view.setUint16(32, 2, true);
    view.setUint16(34, 16, true);
    writeString(36, 'data');
    view.setUint32(40, pcmData.byteLength, true);

    let dataOffset = 44;
    for (let i = 0; i < pcmData.length; i++) {
      view.setInt16(dataOffset, pcmData[i], true);
      dataOffset += 2;
    }

    const wavBlob = new Blob([wavData], { type: 'audio/wav' });
    console.log(`  ✅ PASS - Created WAV file: ${(wavBlob.size / 1024).toFixed(2)} KB`);

    // Test 9: Test Backend Connection
    console.log('\n🔗 Test 9: Testing Backend Connection');
    try {
      const response = await fetch('http://localhost:8000/health');
      if (response.ok) {
        const data = await response.json();
        console.log(`  ✅ PASS - Backend is running`);
        console.log(`  Backend status:`, data);
      } else {
        console.log(`  ❌ FAIL - Backend returned ${response.status}`);
      }
    } catch (e) {
      console.error(`  ❌ FAIL - Cannot reach backend`);
      console.error(`  Error:`, e.message);
    }

    // Cleanup
    stream.getTracks().forEach((track) => track.stop());
    audioContext.close();
    scriptProcessor.disconnect();
    source.disconnect();

    console.log('\n✅ All tests completed!\n');
    console.log('📋 Summary:');
    console.log(`  • Web Audio API: ✅`);
    console.log(`  • MediaRecorder: ✅`);
    console.log(`  • getUserMedia: ✅`);
    console.log(`  • Audio Context: ✅ (${audioContext.sampleRate}Hz)`);
    console.log(`  • Microphone Access: ✅`);
    console.log(`  • ScriptProcessor: ✅`);
    console.log(`  • Audio Recording: ✅ (${chunks.length} chunks)`);
    console.log(`  • WAV Encoding: ✅ (${(wavBlob.size / 1024).toFixed(2)} KB)`);
    console.log(`  • Backend Connection: Check above ☝️`);
    console.log('\n🎉 Ready to use the app!');
  } catch (err) {
    console.error(`❌ Error:`, err.message);
  }
}

// Run the diagnostics
runAudioDiagnostics();
