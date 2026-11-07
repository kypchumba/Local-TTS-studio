
from pathlib import Path
from uuid import uuid4

from flask import (
    Flask,
    jsonify,
    request,
    send_from_directory,
    render_template,
)

from engine.tts_engine import TTSEngine


# --------------------------------------------------
# APPLICATION CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

# Runtime directories
MODELS_DIR = BASE_DIR / "models"
OUTPUT_DIR = BASE_DIR / "outputs"

PREVIEW_DIR = OUTPUT_DIR / "previews"
PREVIEW_DIR.mkdir(parents=True, exist_ok=True)

MODELS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)

MAX_TEXT_LENGTH = 20000


# --------------------------------------------------
# LOAD KOKORO ENGINE
# --------------------------------------------------

print("Initializing Narrate Studio...")

tts_engine = TTSEngine()

print("Narrate Studio is ready!")


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


# --------------------------------------------------
# AVAILABLE VOICES
# --------------------------------------------------

@app.route("/api/voices", methods=["GET"])
def get_voices():
    return jsonify({
        "success": True,
        "voices": tts_engine.get_voices()
    })

@app.route("/api/voice-library", methods=["GET"])
def get_voice_library():
    return jsonify({
        "success": True,
        "voices": tts_engine.get_voice_library()
    })


@app.route("/api/preview", methods=["POST"])
def preview_voice():
    try:
        data = request.get_json(silent=True) or {}
        voice = data.get("voice", "")

        speed = float(data.get("speed", 1.0))
        
        if not 0.5 <= speed <= 2.0:
            return jsonify({
                "success": False,
                "error": "Speed must be between 0.5 and 2.0."
            }), 400

        voice_info = next(
            (item for item in tts_engine.get_voice_library()
             if item["id"] == voice),
            None
        )

        if not voice_info:
            return jsonify({
                "success": False,
                "error": "Invalid voice selected."
            }), 400

        speed_key = f"{speed:.2f}".replace(".", "_")
        filename = f"preview_{voice}_{speed_key}.wav"
        output_path = PREVIEW_DIR / filename

        if not output_path.exists():
            sample_texts = {
                "American English": "Hello! Welcome to Narrate. This is a preview of my voice.",
                "British English": "Hello! Welcome to Narrate. This is a preview of my voice.",
                "Spanish": "Hola. Bienvenido a Narrate. Esta es una muestra de mi voz.",
                "French": "Bonjour. Bienvenue sur Narrate. Voici un aperçu de ma voix.",
                "Hindi": "नमस्ते। Narrate में आपका स्वागत है।",
                "Italian": "Ciao! Benvenuto su Narrate. Questa è un'anteprima della mia voce.",
                "Japanese": "こんにちは。Narrateへようこそ。",
                "Brazilian Portuguese": "Olá! Bem-vindo ao Narrate. Esta é uma amostra da minha voz.",
                "Chinese": "你好！欢迎使用 Narrate。",
            }

            sample_text = sample_texts.get(
                voice_info["language"],
                "Hello! Welcome to Narrate."
            )

            tts_engine.generate(
                text=sample_text,
                voice=voice,
                speed=speed,
                output_path=output_path,
                lang=voice_info["lang"]
            )

        return jsonify({
            "success": True,
            "audio_url": f"/outputs/previews/{filename}"
        })

    except Exception as error:
        print(f"Preview error: {error}")
        return jsonify({
            "success": False,
            "error": "Could not generate voice preview."
        }), 500


# --------------------------------------------------
# GENERATE SPEECH
# --------------------------------------------------

@app.route("/api/generate", methods=["POST"])
def generate_speech():

    try:
        data = request.get_json(silent=True) or {}

        text = data.get("text", "").strip()
        voice = data.get("voice", "af_heart")
        speed = data.get("speed", 1.0)

        # Validate text
        if not text:
            return jsonify({
                "success": False,
                "error": "Please enter some text."
            }), 400

        if len(text) > MAX_TEXT_LENGTH:
            return jsonify({
                "success": False,
                "error": f"Text cannot exceed {MAX_TEXT_LENGTH} characters."
            }), 400

        # Validate voice
        if voice not in tts_engine.get_voices():
            return jsonify({
                "success": False,
                "error": "Invalid voice selected."
            }), 400

        # Validate speed
        try:
            speed = float(speed)
        except (TypeError, ValueError):
            return jsonify({
                "success": False,
                "error": "Invalid speaking speed."
            }), 400

        if not 0.5 <= speed <= 2.0:
            return jsonify({
                "success": False,
                "error": "Speed must be between 0.5 and 2.0."
            }), 400

        # Generate unique filename
        filename = f"narration_{uuid4().hex[:12]}.wav"

        output_path = OUTPUT_DIR / filename

        # Generate audio
        samples, sample_rate = tts_engine.generate(
            text=text,
            voice=voice,
            speed=speed,
            output_path=output_path
        )

        duration = len(samples) / sample_rate

        return jsonify({
            "success": True,
            "message": "Speech generated successfully.",
            "filename": filename,
            "audio_url": f"/outputs/{filename}",
            "duration": round(duration, 2),
            "sample_rate": sample_rate
        })

    except Exception as error:

        print(f"Generation error: {error}")

        return jsonify({
            "success": False,
            "error": "Speech generation failed. Please try again."
        }), 500


# --------------------------------------------------
# SERVE GENERATED AUDIO
# --------------------------------------------------

@app.route("/outputs/previews/<filename>")
def serve_preview(filename):
    if not filename.endswith(".wav"):
        return jsonify({"error": "Invalid audio file."}), 400

    return send_from_directory(
        PREVIEW_DIR,
        filename,
        as_attachment=False
    )

@app.route("/outputs/<filename>")
def serve_audio(filename):

    if not filename.endswith(".wav"):
        return jsonify({"error": "Invalid audio file."}), 400

    return send_from_directory(
        OUTPUT_DIR,
        filename,
        as_attachment=False
    )


# --------------------------------------------------
# RUN APPLICATION
# --------------------------------------------------

if __name__ == "__main__":

    print("\n--------------------------------")
    print("       NARRATE STUDIO")
    print("--------------------------------")
    print("Local server: http://127.0.0.1:5000")
    print("Press CTRL+C to stop the server.")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        threaded=False
    )
