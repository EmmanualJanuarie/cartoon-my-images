import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
import sounddevice as sd
import numpy as np
import speech_recognition as sr
from PIL import Image, ImageTk
import cv2

class VoiceToCartoonApp(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()

        self.title("🎤 Voice to Cartoon")
        self.geometry("1300x700")
        self.recording = False
        self.audio_data = None
        self.transcribed_text = ""
        self.selected_style = tk.StringVar(value="Original")

        # Main container frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True)

        # Header bar
        header = ctk.CTkFrame(self.main_frame, height=40, fg_color="#1a3a60", corner_radius=10)
        header.pack(fill="x", side="top")

        title = ctk.CTkLabel(header, text="🎤 Voice to Cartoon", text_color="white", font=("Arial", 16))
        title.pack(side="left", padx=20, pady=5)

        exit_btn = ctk.CTkButton(
            header,
            text="Exit",
            width=120,
            height=30,
            fg_color="#e94560",
            hover_color="#c63550",
            command=self.on_close
        )
        exit_btn.pack(side="right", padx=10, pady=5)

        # Transcription display
        self.transcription_label = ctk.CTkLabel(self.main_frame, text="Press '🎙️ Record' and speak", font=("Arial", 20))
        self.transcription_label.pack(pady=20)

        # Cartoon preview label
        self.cartoon_label = ctk.CTkLabel(self.main_frame, text="", corner_radius=20)
        self.cartoon_label.pack(pady=10, padx=10, fill="both", expand=True)

        # Controls frame
        controls = ctk.CTkFrame(self.main_frame, fg_color="#1a3a60", corner_radius=20)
        controls.pack(fill="x", padx=20, pady=10)

        # Style dropdown
        self.style_menu = ctk.CTkOptionMenu(
            controls,
            variable=self.selected_style,
            values=["Original", "Sketch", "Soft Paint", "Bold Edges"],
            fg_color="#4579e9",
            button_color="#4579e9",
            button_hover_color="#35b0c6",
            text_color="white",
            command=self.on_style_change
        )
        self.style_menu.pack(side="left", padx=10, pady=10)

        # Record button
        self.record_btn = ctk.CTkButton(
            controls,
            text="🎙️ Record",
            width=200,
            fg_color="#4579e9",
            hover_color="#35b0c6",
            command=self.toggle_recording
        )
        self.record_btn.pack(side="left", padx=40, pady=10)

    def on_close(self):
        self.recording = False
        self.destroy()

    def toggle_recording(self):
        if self.recording:
            # If already recording, ignore clicks
            return

        self.recording = True
        self.record_btn.configure(text="⏳ Listening...")
        self.transcription_label.configure(text="Listening... Please speak now.")
        threading.Thread(target=self.record_and_recognize, daemon=True).start()

    def record_and_recognize(self):
        fs = 16000  # Sample rate
        seconds = 5  # Duration to record

        try:
            # Record audio using sounddevice
            audio = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype='int16')
            sd.wait()
            self.audio_data = audio.flatten()

            # Recognize speech with SpeechRecognition
            recognizer = sr.Recognizer()
            audio_data = sr.AudioData(self.audio_data.tobytes(), fs, 2)

            try:
                text = recognizer.recognize_google(audio_data)
            except sr.UnknownValueError:
                text = "[Could not understand audio]"
            except sr.RequestError as e:
                text = f"[Recognition error: {e}]"

            self.transcribed_text = text

            # Update transcription label and generate cartoon image
            self.after(0, self.update_transcription_and_cartoon)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Audio capture failed:\n{e}"))

        self.recording = False
        self.after(0, lambda: self.record_btn.configure(text="🎙️ Record"))

    def update_transcription_and_cartoon(self):
        self.transcription_label.configure(text=f"Recognized: {self.transcribed_text}")

        # Generate a cartoon image from the text prompt
        cartoon_img = self.generate_cartoon_from_text(self.transcribed_text)
        if cartoon_img is not None:
            self.display_cartoon(cartoon_img)

    def generate_cartoon_from_text(self, prompt):
        # For demo, generate a simple image with the prompt text overlaid on blank background
        # Replace this method with your actual AI cartoon generation code using prompt

        img = Image.new("RGB", (640, 480), (30, 30, 30))
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        lines = self.wrap_text(prompt, font, img.width - 20)

        y = 20
        for line in lines:
            draw.text((10, y), line, font=font, fill=(200, 200, 255))
            y += 15

        # Apply style effect to img based on selected_style
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        styled_cv = self.apply_style(img_cv, self.selected_style.get())
        styled_img = Image.fromarray(cv2.cvtColor(styled_cv, cv2.COLOR_BGR2RGB))
        return styled_img

    def wrap_text(self, text, font, max_width):
        # Helper to wrap text for drawing
        lines = []
        words = text.split()
        line = ""
        for word in words:
            test_line = f"{line} {word}".strip()
            width, _ = font.getsize(test_line)
            if width <= max_width:
                line = test_line
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
        return lines

    def display_cartoon(self, pil_img):
        pil_img = pil_img.resize((640, 480))
        tk_img = ImageTk.PhotoImage(pil_img)
        self.cartoon_label.configure(image=tk_img)
        self.cartoon_label.image = tk_img

    def apply_style(self, img, style):
        if style == "Sketch":
            return self.sketch_effect(img)
        elif style == "Soft Paint":
            return self.watercolor_effect(img)
        elif style == "Bold Edges":
            return self.pencil_sketch(img)[1]
        return img

    # --- Cartoon Style Functions ---
    def pencil_sketch(self, img, sigma_s=60, sigma_r=0.07, shade_factor=0.05):
        gray, color = cv2.pencilSketch(img, sigma_s=sigma_s, sigma_r=sigma_r, shade_factor=shade_factor)
        return gray, color

    def watercolor_effect(self, img, d=9):
        color = cv2.bilateralFilter(img, d, 300, 300)
        gray = cv2.cvtColor(color, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 7)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                      cv2.THRESH_BINARY, 9, 9)
        return cv2.bitwise_and(color, color, mask=edges)

    def sketch_effect(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        inverted = cv2.bitwise_not(gray)
        blurred = cv2.GaussianBlur(inverted, (21, 21), 0)
        inverted_blurred = cv2.bitwise_not(blurred)
        sketch = cv2.divide(gray, inverted_blurred, scale=256.0)
        return cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)

    def on_style_change(self, choice):
        # Re-generate cartoon image on style change
        if self.transcribed_text:
            cartoon_img = self.generate_cartoon_from_text(self.transcribed_text)
            if cartoon_img is not None:
                self.display_cartoon(cartoon_img)


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = VoiceToCartoonApp()
    app.mainloop()
