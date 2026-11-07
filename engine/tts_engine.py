
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
        self.tts = Kokoro(str(self.model_path), str(self.voices_path))
        self.voices = self.tts.get_voices()
        print("Kokoro model loaded successfully!")

    def get_voices(self):
        return self.voices

        
    def get_voice_library(self):
        voice_groups = {
            "af": ("American English", "Female", "en-us"),
            "am": ("American English", "Male", "en-us"),
            "bf": ("British English", "Female", "en-gb"),
            "bm": ("British English", "Male", "en-gb"),
            "ef": ("Spanish", "Female", "es"),
            "em": ("Spanish", "Male", "es"),
            "ff": ("French", "Female", "fr-fr"),
            "hf": ("Hindi", "Female", "hi"),
            "hm": ("Hindi", "Male", "hi"),
            "if": ("Italian", "Female", "it"),
            "im": ("Italian", "Male", "it"),
            "jf": ("Japanese", "Female", "ja"),
            "jm": ("Japanese", "Male", "ja"),
            "pf": ("Brazilian Portuguese", "Female", "pt-br"),
            "pm": ("Brazilian Portuguese", "Male", "pt-br"),
            "zf": ("Chinese", "Female", "zh"),
            "zm": ("Chinese", "Male", "zh"),
        }
    
        library = []
    
        for voice_id in self.voices:
            prefix, voice_name = voice_id.split("_", 1)
    
            language, gender, lang_code = voice_groups.get(
                prefix,
                ("Other", "Unknown", "en-us")
            )
    
            library.append({
                "id": voice_id,
                "name": voice_name.replace("_", " ").title(),
                "language": language,
                "gender": gender,
                "lang": lang_code
            })
    
        return library
    

    def generate(
        self,
        text,
        voice="af_heart",
        speed=1.0,
        output_path=None,
        lang="en-us"
    ):
        if not text or not text.strip():
            raise ValueError("Please enter some text.")

        samples, sample_rate = self.tts.create(
            text.strip(),
            voice=voice,
            speed=float(speed),
            lang=lang
        )

        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            sf.write(
                output_path,
                samples,
                sample_rate,
                subtype="PCM_16"
            )

        return samples, sample_rate
