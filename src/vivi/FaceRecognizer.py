import cv2

class FaceRecognizer:
    def __init__(self):
        """Prototype - SFace Recognizer"""
        self.sface_model = "src/vivi/face_recognition_sface_2021dec.onnx"
        self.recognizer = None # (Temp) Singleton
        self.face_vector = None

    def run(self, frame, face):
        self.recognizer = cv2.FaceRecognizerSF.create(self.sface_model, "")
        aligned_face = self.recognizer.alignCrop(frame, face)
        self.face_vector = self.recognizer.feature(aligned_face)
