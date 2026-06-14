import asyncio
import io
import wave
import numpy as np
import sounddevice as sd


class AudioPlayer:
    async def play(self, wav_bytes: bytes) -> None:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._play_sync, wav_bytes)

    def _play_sync(self, wav_bytes: bytes) -> None:
        with wave.open(io.BytesIO(wav_bytes)) as wf:
            sample_rate = wf.getframerate()
            n_channels = wf.getnchannels()
            raw = wf.readframes(wf.getnframes())

        audio = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
        if n_channels > 1:
            audio = audio.reshape(-1, n_channels)

        sd.play(audio, samplerate=sample_rate)
        sd.wait()
