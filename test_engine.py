
from engine.tts_engine import TTSEngine

print("Starting Kokoro test...")

engine = TTSEngine()

voices = engine.get_voices()

print("\nAvailable voices:")
print(voices)

print("\nKokoro engine is ready!")
