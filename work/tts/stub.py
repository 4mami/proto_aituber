import struct
import math


class StubTTS:
    async def synthesize(self, text: str) -> bytes:
        print(f"[TTS stub] {text}")
        return _silent_wav(duration_sec=1.0)


def _silent_wav(duration_sec: float = 1.0, sample_rate: int = 24000) -> bytes:
    num_samples = int(sample_rate * duration_sec)
    data = b"\x00\x00" * num_samples  # 16bit silence
    return _wav_header(sample_rate, num_samples) + data


def _wav_header(sample_rate: int, num_samples: int) -> bytes:
    data_size = num_samples * 2
    return struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF", 36 + data_size, b"WAVE",
        b"fmt ", 16, 1, 1,
        sample_rate, sample_rate * 2, 2, 16,
        b"data", data_size,
    )
