from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import numpy as np
from io import BytesIO
from PIL import Image
import tensorflow as tf
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# endpoint = "http://localhost:8501/v1/models/potato-disease:predict"
MODEL = tf.keras.models.load_model("./saved_models/1")
CLASS_NAMES = ["Early Blight", "Late Blight", "Healthy"]

@app.get('/ping')
async def ping():
    return "Hello I'm alive!"

def read_file_as_image(data) -> np.ndarray:
    image = np.array(Image.open(BytesIO(data)))
    return image

@app.post('/predict')
async def predict(
    file: UploadFile = File(...)
):
    image = read_file_as_image(await file.read())
    img_batch = np.expand_dims(image, 0)
    predictions = MODEL.predict(img_batch)
    # json_data = {
    #     "instances": img_batch.tolist()
    # }
    # response = requests.post(endpoint, json=json_data)
    # prediction = response.json()["predictions"][0]
    prediction = predictions[0]
    predicted_class = CLASS_NAMES[np.argmax(prediction)]
    confidence = np.max(prediction)
    return {
        'class': predicted_class,
        'confidence': float(confidence),
    }

if __name__ == '__main__':
    uvicorn.run(app, host='localhost', port=8000)