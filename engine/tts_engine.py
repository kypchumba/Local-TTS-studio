
from pathlib import Path
import soundfile as sf
from kokoro_onnx import Kokoro


class TTSEngine:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent
        self.models_dir = self.base_dir / "models"

        self.model_path = self.models_dir / "kokoro-v1.0.onnx"
        self.voices_path = self.models_dir / "voices-v1.0.bin"

        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found: {self.model_path}")

        if not self.voices_path.exists():
            raise FileNotFoundError(f"Voice file not found: {self.voices_path}")

        print("Loading Kokoro model...")

        self.tts = Kokoro(
            str(self.model_path),
            str(self.voices_path)
        )

        self.voices = self.tts.get_voices()

        print("Kokoro model loaded successfully!")

    def get_voices(self):
        return self.voices

    def generate(self, text, voice="af_heart", speed=1.0, output_path=None):
        if not text or not text.strip():
            raise ValueError("Please enter some text.")

        samples, sample_rate = self.tts.create(
            text.strip(),
            voice=voice,
            speed=float(speed),
            lang="en-us"
        )

        if output_path:
            sf.write(output_path, samples, sample_rate, subtype="PCM_16")

        return samples, sample_rate
