
from pathlib import Path
import soundfile as sf
from kokoro_onnx import Kokoro


class TTSEngine:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent
        self.models_dir = self.base_dir / "models"

        self.hf_cache_dir = self.models_dir / "huggingface"
        self.hf_cache_dir.mkdir(parents=True, exist_ok=True)

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

        # Swahili model is loaded only when needed.
        self.swahili_model = None
        self.swahili_tokenizer = None

        self.swahili_voice_id = "sw_swahili"

    def get_voices(self):
        return [*self.voices, self.swahili_voice_id]

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

        library.append({
            "id": self.swahili_voice_id,
            "name": "Swahili",
            "language": "Swahili",
            "gender": "Female",
            "lang": "sw"
        })

        return library
    
    def load_swahili_model(self):
        if self.swahili_model is not None:
            return
    
        print("Loading Swahili MMS-TTS model...")
    
        import torch
        from transformers import AutoTokenizer, VitsModel
    
        model_id = "facebook/mms-tts-swh"
        cache_dir = str(self.hf_cache_dir)
    
        self.swahili_tokenizer = AutoTokenizer.from_pretrained(
            model_id,
            cache_dir=cache_dir
        )
    
        self.swahili_model = VitsModel.from_pretrained(
            model_id,
            cache_dir=cache_dir
        )
    
        self.swahili_model.eval()
    
        print("Swahili model loaded successfully!")

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

        text = text.strip()

        if voice == self.swahili_voice_id:
            self.load_swahili_model()

            import torch

            inputs = self.swahili_tokenizer(
                text,
                return_tensors="pt"
            )

            with torch.no_grad():
                output = self.swahili_model(**inputs).waveform

            samples = output.squeeze().cpu().numpy()
            sample_rate = self.swahili_model.config.sampling_rate

        else:
            samples, sample_rate = self.tts.create(
                text,
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
