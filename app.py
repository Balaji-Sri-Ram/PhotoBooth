from flask import Flask, request, jsonify, render_template
from PIL import Image
import google.generativeai as genai
import base64
import io
import traceback

app = Flask(__name__)

# ✅ Configure Gemini (replace with your actual API key)
genai.configure(api_key="AIzaSyC90IKUxsCklSmoAVWstXfxm0tBT1YfRJo")
model = genai.GenerativeModel('gemini-1.5-flash')

# ✅ Home route
@app.route('/')
def home():
    return render_template("index.html")

# ✅ Analyze uploaded file
@app.route('/image', methods=['POST'])
def analyze_uploaded_image():
    try:
        if 'image' not in request.files:
            return jsonify({'response': "❗ No image uploaded."}), 400

        file = request.files['image']
        image = Image.open(file).convert("RGB")

        image_part = pil_to_gemini_part(image)

        prompt = (
            "You are a friendly photo booth assistant. "
            "Describe what's happening in the photo. Mention people, expressions, objects, and backgrounds. "
            "Give fun or helpful suggestions to improve the photo or make it more fun."
        )

        response = model.generate_content([prompt, image_part])
        return jsonify({'response': response.text})

    except Exception as e:
        traceback.print_exc()
        return jsonify({'response': f"Oops! Couldn't analyze the image. Error: {str(e)}"}), 500

# ✅ Analyze base64 image from camera
@app.route('/analyze', methods=['POST'])
def analyze_captured_image():
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'response': "❗ No image data received."}), 400

        base64_data = data['image'].split(",")[1]  # Strip off the data:image/... prefix
        image_data = base64.b64decode(base64_data)
        image = Image.open(io.BytesIO(image_data)).convert("RGB")

        image_part = pil_to_gemini_part(image)

        prompt = (
            "You are a friendly photo booth assistant. "
            "Describe what's happening in the photo. Mention people, expressions, objects, and backgrounds. "
            "Give fun or helpful suggestions to improve the photo or make it more fun."
        )

        response = model.generate_content([prompt, image_part])
        return jsonify({'response': response.text})

    except Exception as e:
        traceback.print_exc()
        return jsonify({'response': f"Oops! Couldn't analyze the image. Error: {str(e)}"}), 500

# ✅ Convert PIL Image to Gemini-compatible part
def pil_to_gemini_part(pil_img):
    img_byte_arr = io.BytesIO()
    pil_img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    return {
        "mime_type": "image/jpeg",
        "data": img_byte_arr.read()
    }

# ✅ Run app
if __name__ == "__main__":
    app.run(debug=True)
