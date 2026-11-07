
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
OUTPUT_DIR = BASE_DIR / "outputs"

OUTPUT_DIR.mkdir(exist_ok=True)

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
