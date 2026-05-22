export function recordWav(signal) {
  return new Promise((resolve, reject) => {
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then((stream) => {
        const ctx = new AudioContext();
        const src = ctx.createMediaStreamSource(stream);
        const sampleRate = ctx.sampleRate;
        let recording = true;
        const samples = [];

        const processor = ctx.createScriptProcessor(4096, 1, 1);
        processor.onaudioprocess = (e) => {
          if (!recording) return;
          samples.push(new Float32Array(e.inputBuffer.getChannelData(0)));
        };

        src.connect(processor);
        processor.connect(ctx.destination);

        function stop() {
          recording = false;
          src.disconnect();
          processor.disconnect();
          stream.getTracks().forEach(t => t.stop());

          const totalLen = samples.reduce((s, a) => s + a.length, 0);
          const merged = new Float32Array(totalLen);
          let offset = 0;
          for (const a of samples) {
            merged.set(a, offset);
            offset += a.length;
          }

          const wav = encodeWav(merged, sampleRate);
          const blob = new Blob([wav], { type: 'audio/wav' });
          const file = new File([blob], 'recording.wav', { type: 'audio/wav' });
          ctx.close();
          resolve(file);
        }

        if (signal) {
          signal.addEventListener('abort', stop);
        }
      })
      .catch(() => reject(new Error('Microphone access denied')));
  });
}

function encodeWav(samples, sampleRate) {
  const numChannels = 1;
  const bitsPerSample = 16;
  const byteRate = sampleRate * numChannels * bitsPerSample / 8;
  const blockAlign = numChannels * bitsPerSample / 8;
  const dataSize = samples.length * blockAlign;
  const buffer = new ArrayBuffer(44 + dataSize);
  const view = new DataView(buffer);

  function writeString(offset, str) {
    for (let i = 0; i < str.length; i++) view.setUint8(offset + i, str.charCodeAt(i));
  }

  writeString(0, 'RIFF');
  view.setUint32(4, 36 + dataSize, true);
  writeString(8, 'WAVE');
  writeString(12, 'fmt ');
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, numChannels, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, byteRate, true);
  view.setUint16(32, blockAlign, true);
  view.setUint16(34, bitsPerSample, true);
  writeString(36, 'data');
  view.setUint32(40, dataSize, true);

  for (let i = 0; i < samples.length; i++) {
    const s = Math.max(-1, Math.min(1, samples[i]));
    view.setInt16(44 + i * 2, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
  }

  return buffer;
}
