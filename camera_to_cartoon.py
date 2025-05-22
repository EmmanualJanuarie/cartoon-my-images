import threading
import cv2
from PIL import Image, ImageTk
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import numpy as np
import ctypes
import sys
import time
import os
from datetime import datetime

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class CartoonCameraApp(ctk.CTkToplevel):

    def __init__(self, parent):
        super().__init__()

        self.title("Camera to Cartoon")
        self.geometry("1300x700")
        self.overrideredirect(True)

        self._offsetx = 0
        self._offsety = 0
        self.selected_style = tk.StringVar(value="Original")
        self.freeze_frame = False
        self.last_frame = None

        if sys.platform.startswith("win"):
            self.after(50, self.make_window_rounded)

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True)

        # Header
        header = ctk.CTkFrame(self.main_frame, height=40, fg_color="#1a3a60", corner_radius=20)
        header.pack(fill="x", side="top")

        title = ctk.CTkLabel(header, text="📸 Camera to Cartoon", text_color="white", font=("Arial", 16))
        title.pack(side="left", padx=20, pady=5)

        exit_btn = ctk.CTkButton(header, text="Exit", width=100, height=30, fg_color="#e94560", command=self.on_close)
        exit_btn.pack(side="right", padx=10, pady=5)

        header.bind("<Button-1>", self.start_move)
        header.bind("<B1-Motion>", self.do_move)

        # Camera display
        self.camera_preview = ctk.CTkLabel(self.main_frame, text="", corner_radius=20)
        self.camera_preview.pack(pady=(5, 10), padx=10, fill="both", expand=True)

        # Controls
        controls = ctk.CTkFrame(self.main_frame, fg_color="#1a3a60", corner_radius=20)
        controls.pack(fill="x", padx=20, pady=(0, 10))

        styles = [
            "Original",
            "Pencil Sketch",
            "Detail Enhance",
            "Watercolor",
            "Color Quantization",
            "Sketch Effect",
            "Vignette",
            "Lomo"
        ]
        self.style_menu = ctk.CTkOptionMenu(
            controls,
            variable=self.selected_style,
            values=styles,
            fg_color="#4579e9",
            button_color="#4579e9",
            button_hover_color="#35b0c6",
            text_color="white"
        )
        self.style_menu.pack(side="left", padx=20, pady=10)

        snap_btn = ctk.CTkButton(
            controls,
            text="📸 Snap",
            command=self.snap_and_freeze,
            fg_color="#e94560",
            hover_color="#c63550",
            width=200
        )
        snap_btn.pack(side="left", padx=10, pady=10)

        threading.Thread(target=self.update_camera_feed, daemon=True).start()

    def make_window_rounded(self):
        hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
        radius = 20
        ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 2, ctypes.byref(ctypes.c_int(1)), 4)
        region = ctypes.windll.gdi32.CreateRoundRectRgn(0, 0, self.winfo_width(), self.winfo_height(), radius, radius)
        ctypes.windll.user32.SetWindowRgn(hwnd, region, True)

    def start_move(self, event):
        self._offsetx = event.x
        self._offsety = event.y

    def do_move(self, event):
        x = self.winfo_pointerx() - self._offsetx
        y = self.winfo_pointery() - self._offsety
        self.geometry(f"+{x}+{y}")

    def update_camera_feed(self):
        self.cap = cv2.VideoCapture(0)
        while True:
            if not self.freeze_frame:
                ret, frame = self.cap.read()
                if not ret:
                    break
                frame = cv2.resize(frame, (1200, 550))
                self.last_frame = frame.copy()
                selected = self.selected_style.get()
                styled_frame = self.apply_style(frame, selected)
                self.show_image(styled_frame)
            time.sleep(0.03)
        self.cap.release()

    def make_window_rounded(self, window, radius=25):
        if sys.platform.startswith("win"):
            hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 2, ctypes.byref(ctypes.c_int(1)), 4)
            region = ctypes.windll.gdi32.CreateRoundRectRgn(0, 0, window.winfo_width(), window.winfo_height(), radius, radius)
            ctypes.windll.user32.SetWindowRgn(hwnd, region, True)

    def show_custom_message(self, message):
        popup = ctk.CTkToplevel(self)
        popup.overrideredirect(True)
        popup.resizable(False, False)
        popup.geometry("360x190")

        # Position popup centered above the main window
        main_x = self.winfo_rootx()
        main_y = self.winfo_rooty()
        main_w = self.winfo_width()
        main_h = self.winfo_height()
        popup_w, popup_h = 360, 190
        pos_x = main_x + (main_w // 2) - (popup_w // 2)
        pos_y = main_y + (main_h // 2) - (popup_h // 2) - 60
        popup.geometry(f"+{pos_x}+{pos_y}")

        # Background frame with subtle shadow effect
        bg_frame = ctk.CTkFrame(popup, fg_color="#202f4f", corner_radius=25, border_width=2, border_color="#4579e9")
        bg_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Message label - modern font and spacing
        label = ctk.CTkLabel(
            bg_frame,
            text=message,
            text_color="#e0e6f0",
            font=("Segoe UI Semibold", 16),
            justify="center",
            wraplength=320
        )
        label.pack(pady=(30, 20), padx=20)

        # Modern flat style OK button
        ok_button = ctk.CTkButton(
            bg_frame,
            text="OK",
            fg_color="#4579e9",
            hover_color="#3a68c4",
            command=popup.destroy,
            corner_radius=20,
            width=80,
            height=40,
            font=("Segoe UI", 14)
        )
        ok_button.pack(pady=(0, 25))

        # Rounded corners for popup window (Win only)
        self.after(50, lambda: self.make_window_rounded(popup, radius=25))

        # Fade in effect (opacity from 0 to 1)
        def fade_in(alpha=0):
            alpha += 0.1
            if alpha > 1:
                alpha = 1
                popup.attributes("-alpha", alpha)
            if alpha < 1:
                popup.after(25, lambda: fade_in(alpha))

                popup.attributes("-alpha", 0)
                fade_in()

    def save_image(self, image):
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        captured_dir = os.path.join(downloads_path, "captured")
        os.makedirs(captured_dir, exist_ok=True)

        filename = f"captured_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        file_path = os.path.join(captured_dir, filename)

        cv2.imwrite(file_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))

        # Schedule the popup on the main thread
        self.after(0, lambda: self.show_custom_message(
            f"✅ Image saved to:\nDownloads/captured/\n\n📁 {filename}"))



    def show_image(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(img)
        self.camera_preview.configure(image=imgtk)
        self.camera_preview.image = imgtk

    def snap_and_freeze(self):
        if self.last_frame is not None:
            self.freeze_frame = True
            styled = self.apply_style(self.last_frame.copy(), self.selected_style.get())
            self.show_image(styled)
            self.save_image(styled)  # Auto save
            self.after(1000, self.resume_camera)

    def resume_camera(self):
        self.freeze_frame = False

    def apply_style(self, img, style_name):
        if style_name == "Pencil Sketch":
            gray, color = cv2.pencilSketch(img, sigma_s=60, sigma_r=0.07, shade_factor=0.05)
            return color
        elif style_name == "Detail Enhance":
            return cv2.detailEnhance(img, sigma_s=10, sigma_r=0.15)
        elif style_name == "Watercolor":
            return self.watercolor_effect(img)
        elif style_name == "Color Quantization":
            return self.color_quantization(img)
        elif style_name == "Sketch Effect":
            sketch = self.sketch_effect(img)
            return cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)
        elif style_name == "Vignette":
            return self.vignette(img)
        elif style_name == "Lomo":
            return self.lomo(img)
        else:
            return img

    def watercolor_effect(self, img):
        color = cv2.bilateralFilter(img, 9, 300, 300)
        gray = cv2.cvtColor(color, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 7)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                      cv2.THRESH_BINARY, 9, 9)
        return cv2.bitwise_and(color, color, mask=edges)

    def color_quantization(self, img, k=8):
        data = np.float32(img).reshape((-1, 3))
        _, labels, centers = cv2.kmeans(data, k, None,
                                        (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2),
                                        10, cv2.KMEANS_RANDOM_CENTERS)
        centers = np.uint8(centers)
        quantized = centers[labels.flatten()]
        return quantized.reshape(img.shape)

    def sketch_effect(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        inverted = cv2.bitwise_not(gray)
        blurred = cv2.GaussianBlur(inverted, (21, 21), 0)
        inverted_blurred = cv2.bitwise_not(blurred)
        return cv2.divide(gray, inverted_blurred, scale=256.0)

    def vignette(self, img, strength=1.0):
        rows, cols = img.shape[:2]
        kernel_x = cv2.getGaussianKernel(cols, cols / 3)
        kernel_y = cv2.getGaussianKernel(rows, rows / 3)
        mask = kernel_y * kernel_x.T
        mask = mask / mask.max()
        output = np.copy(img)
        for i in range(3):
            output[:, :, i] = output[:, :, i] * mask * strength
        return output

    def lomo(self, img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hsv[:, :, 1] = cv2.add(hsv[:, :, 1], 50)
        lomo = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        return cv2.GaussianBlur(lomo, (15, 15), 0)

    def on_close(self):
        self.freeze_frame = True
        self.destroy()


if __name__ == "__main__":
    app = CartoonCameraApp()
    app.mainloop()
