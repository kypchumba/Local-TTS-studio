
from pathlib import Path
from engine.tts_engine import TTSEngine

# Create output folder
output_dir = Path("outputs")
output_dir.mkdir(exist_ok=True)

# Load Kokoro
engine = TTSEngine()

# Test narration
text = """
Hello and welcome to Narrate.
This is my first locally generated voice narration
using the Kokoro text to speech engine.
"""

output_path = output_dir / "test.wav"

print("\nGenerating speech...")

samples, sample_rate = engine.generate(
    text=text,
    voice="af_heart",
    speed=1.0,
    output_path=output_path
)

print("\nSpeech generated successfully!")
print(f"Sample rate: {sample_rate}")
print(f"Audio duration: {len(samples) / sample_rate:.2f} seconds")
print(f"Saved to: {output_path.resolve()}")
