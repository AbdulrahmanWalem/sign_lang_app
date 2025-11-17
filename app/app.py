import cv2
import mediapipe as mp
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import threading

class SignLanguageApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Sign Language")

        self.mp_hands = mp.solutions.hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils

        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Unable to open camera")

        self.frame_counter = 0

        top = ttk.Frame(self.root)
        top.pack(fill="both", expand=True, padx=10, pady=10)

        cam_frame = ttk.LabelFrame(top, text="Camera")
        cam_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.video_label = ttk.Label(cam_frame)
        self.video_label.pack(fill="both", expand=True)

        trans_frame = ttk.LabelFrame(top, text="Translation")
        trans_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        self.translation_label = tk.Label(
            trans_frame,
            text="Camera or voice translation will appear here.",
            font=("Arial", 16),
            wraplength=300,
            justify="center"
        )
        self.translation_label.pack(fill="both", expand=True, padx=10, pady=10)

        bottom = ttk.Frame(self.root)
        bottom.pack(fill="x", padx=10, pady=10)

        mic_btn = ttk.Button(bottom, text="🎤 Voice Input", command=self.start_voice_mode)
        mic_btn.pack(side="left", padx=5)

        exit_btn = ttk.Button(bottom, text="Exit", command=self.on_closing)
        exit_btn.pack(side="right", padx=5)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.update_frame()

    def update_frame(self):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.mp_hands.process(frame_rgb)

                if results.multi_hand_landmarks:
                    for handLms in results.multi_hand_landmarks:
                        self.mp_draw.draw_landmarks(
                            frame,
                            handLms,
                            mp.solutions.hands.HAND_CONNECTIONS
                        )
                        break

                    self.frame_counter += 1
                    if self.frame_counter % 10 == 0:
                        self.predict_from_hand()

                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(img)
                img = img.resize((480, 360))
                imgtk = ImageTk.PhotoImage(img)

                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)

        self.root.after(15, self.update_frame)

    def predict_from_hand(self):
        predicted = "A"
        self.translation_label.config(text=f"Camera translation (demo): {predicted}")

    def start_voice_mode(self):
        t = threading.Thread(target=self.voice_worker, daemon=True)
        t.start()

    def voice_worker(self):
        try:
            import speech_recognition as sr
        except ImportError:
            self.translation_label.config(text="Please install SpeechRecognition first.")
            return

        r = sr.Recognizer()

        try:
            try:
                mic = sr.Microphone()
            except Exception:
                self.translation_label.config(
                    text="Unable to access microphone (PyAudio not installed or no mic connected)."
                )
                return

            with mic as source:
                self.translation_label.config(text="Listening...")
                r.adjust_for_ambient_noise(source, duration=0.5)
                audio = r.listen(source)

            try:
                text = r.recognize_google(audio, language="ar-SA")
                self.translation_label.config(text=f"Voice translation:\n{text}")
            except sr.UnknownValueError:
                self.translation_label.config(text="Could not understand the audio, please try again.")
            except sr.RequestError as e:
                self.translation_label.config(text=f"Speech recognition service error: {e}")

        except Exception as e:
            self.translation_label.config(text=f"Microphone error: {e}")

    def on_closing(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.mp_hands.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SignLanguageApp(root)
    root.mainloop()