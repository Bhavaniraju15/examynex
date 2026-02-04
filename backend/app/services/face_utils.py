import face_recognition
import numpy as np

def extract_face_embedding(image):
    rgb = image[:, :, ::-1]  # BGR → RGB
    encodings = face_recognition.face_encodings(rgb)

    if not encodings:
        return None

    return encodings[0]

def compare_faces(ref_embedding, live_embedding, threshold=0.6):
    distance = np.linalg.norm(ref_embedding - live_embedding)
    return distance < threshold, distance
