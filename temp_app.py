from flask import Flask, request, render_template, session, redirect, url_for
import base64
import os
import vertexai
from vertexai.generative_models import GenerativeModel, Part
import vertexai.preview.generative_models as generative_models
from google.cloud import storage

# Bucket Information
client = storage.Client()
BUCKET_NAME = 'kunal_bucket_hckthn'

# Initialize Vertex AI
vertexai.init(project="fair-gradient-419306", location="us-east1")

# Load Generative Model
#model = GenerativeModel("gemini-1.0-pro-vision-001")
#model = GenerativeModel("gemini-1.0-pro-vision-001")
model = GenerativeModel("gemini-1.5-pro-preview-0409")


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

def genai_func(prompt, image_path):
    image = Part.from_uri(image_path, mime_type="image/jpeg")

    responses = model.generate_content(
        [prompt, image],
        generation_config=generation_config,
        #safety_settings=safety_settings,
        stream=True
    )

    generated_text = ""
    for response in responses:
        generated_text += response.text

    print(generated_text)

if __name__ == "__main__":
    prompt = input()
    image_path = 'gs://kunal_bucket_hckthn/Taj_Mahal.jpeg'
    genai_func(prompt, image_path)



