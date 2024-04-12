from flask import Flask, request, render_template, session, redirect, url_for
import base64
import os
import vertexai
from vertexai.generative_models import GenerativeModel, Part
import vertexai.preview.generative_models as generative_models
from google.cloud import storage

app = Flask(__name__)

# Set a secret key for the session
app.secret_key = os.urandom(24)

# Bucket Information
client = storage.Client()
BUCKET_NAME = 'kunal_bucket_hckthn'

# Initialize Vertex AI
#vertexai.init(project="fair-gradient-419306", location="us-central1")

# Load Generative Model
model = GenerativeModel("gemini-1.0-pro-vision-001")
#
# gemini-1.5-pro-preview-0409 # For larger outputs

# Define generation config and safety settings
generation_config = {
    "max_output_tokens": 2048, # 2048 # 8192
    "temperature": 0.6,
    "top_p": 1,
    "top_k": 32,
}

safety_settings = {
    generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
}

def upload_image_to_gcs(image_file):
    bucket = client.bucket(BUCKET_NAME)
    filename = image_file.filename
    blob = bucket.blob(filename)
    blob.upload_from_string(
        image_file.read(),
        content_type=image_file.content_type
    )

    return filename

@app.route('/')
def index():
    return render_template('index.html', error=None)

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    if request.method == 'POST':
        prompt = request.form['prompt']
        image_file = request.files['image']
        try:
            image_name = upload_image_to_gcs(image_file)
            image_path = f"gs://{BUCKET_NAME}/{image_name}"
            image = Part.from_uri(image_path, mime_type="image/jpeg")

            responses = model.generate_content(
                [f"{prompt}", image],
                generation_config=generation_config,
                #safety_settings=safety_settings,
                stream=True
            )

            generated_text = ""
            for response in responses:
                generated_text += response.text
            public_image_path = f"https://storage.googleapis.com/{BUCKET_NAME}/{image_name}"
            return render_template('result.html', generated_text=generated_text, image_path=public_image_path, error=None)
        except Exception as e:
            error = str(e)
            return render_template('index.html', error=error)
    else:
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
