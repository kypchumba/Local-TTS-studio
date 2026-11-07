
from engine.tts_engine import TTSEngine
import inspect

engine = TTSEngine()

print("\n--- ONNX MODEL INPUTS ---")

for item in engine.tts.sess.get_inputs():
    print(
        f"Name: {item.name} | "
        f"Type: {item.type} | "
        f"Shape: {item.shape}"
    )

print("\n--- KOKORO AUDIO GENERATION CODE ---")

print(inspect.getsource(engine.tts._create_audio))
