from fastapi import FastAPI, File, UploadFile
import uvicorn
import numpy as np
from PIL import Image
from io import BytesIO
import tensorflow as tf
from pathlib import Path

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "model" / "1" / "1.keras"
MODEL = tf.keras.models.load_model(MODEL_PATH)

CLASS_NAMES = ["Early Blight", "Late Blight", "Healthy"]

@app.get("/ping")

async def ping():
    return {"jaiiii": "Hoooooo!"}


def read_file_as_image(data) -> np.ndarray:
    return np.array(Image.open(BytesIO(data)))


@app.post("/predict")
async def predict(
    file: UploadFile = File(...)
):
    image = read_file_as_image(await file.read())
    image_batch = np.expand_dims(image, axis=0)
    predictions = MODEL.predict(image_batch)
    predicted_index = int(np.argmax(predictions[0]))
    confidence = float(np.max(predictions[0]))
    class_scores = {
        class_name: float(score)
        for class_name, score in zip(CLASS_NAMES, predictions[0])
    }



    # Confirm it's a numpy array
    print(f"Type: {type(image)}")
    print(f"Shape: {image.shape}")
    print(f"Data type: {image.dtype}")
    
    return {
        "type": str(type(image)),
        "shape": image.shape,
        "dtype": str(image.dtype),
        "image_batch_shape": list(image_batch.shape),
        "prediction_batch": predictions.tolist(),
        "class_scores": class_scores,
        "predicted_class": CLASS_NAMES[predicted_index],
        "confidence": confidence,
    }


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)