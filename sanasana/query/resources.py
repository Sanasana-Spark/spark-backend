import os
import base64
from datetime import datetime


# Function to Save Image
def save_image(base64_string, trip_id):
    folder = "odometer_images"
    os.makedirs(folder, exist_ok=True)  # Create folder if it doesn't exist

    filename = f"{trip_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.png"
    filepath = os.path.join(folder, filename)

    with open(filepath, "wb") as img_file:
        img_file.write(base64.b64decode(base64_string.split(",")[1]))  # Decode Base64

    return filepath