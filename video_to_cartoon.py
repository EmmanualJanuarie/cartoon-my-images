import cv2
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import threading
import ctypes
import sys

class VideoToCartoonApp(ctk.CTkToplevel):
    def __init__(self, parent=None):
        super().__init__()
        self.title("Video to Cartoon")

        self.geometry("1300x700")
        self.overrideredirect(True)

        self._offsetx = 0
        self._offsety = 0
        self.selected_style = tk.StringVar(value="Original")
        self.recording = False
        self.camera_running = True
        self.frames = []

        if sys.platform.startswith("win"):
            self.after(50, self.make_window_rounded)

        # --- Layout ---
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True)

        header = ctk.CTkFrame(self.main_frame, height=40, fg_color="#1a3a60", corner_radius=10)
        header.pack(fill="x", side="top")

        title = ctk.CTkLabel(header, text="🎬 Video to Cartoon", text_color="white", font=("Arial", 16))
        title.pack(side="left", padx=20, pady=5)

        exit_btn = ctk.CTkButton(header, text="Exit", width=120, height=30,
                                 fg_color="#e94560", hover_color="#c63550", command=self.on_close)
        exit_btn.pack(side="right", padx=10, pady=5)

        header.bind("<Button-1>", self.start_move)
        header.bind("<B1-Motion>", self.do_move)

        self.camera_label = ctk.CTkLabel(self.main_frame, text="", corner_radius=20)
        self.camera_label.pack(pady=(5, 10), padx=10, fill="both", expand=True)

        controls = ctk.CTkFrame(self.main_frame, fg_color="#1a3a60", corner_radius=20)
        controls.pack(fill="x", padx=20, pady=(0, 10))

        controls_inner = ctk.CTkFrame(controls, fg_color="transparent", height=40, width=700)
        controls_inner.pack(pady=10)
        controls_inner.pack_propagate(False)

        self.style_menu = ctk.CTkOptionMenu(controls_inner, variable=self.selected_style,
                                            values=["Original", "Sketch", "Soft Paint", "Bold Edges"],
                                            fg_color="#4579e9", button_color="#4579e9",
                                            button_hover_color="#35b0c6", text_color="white")
        self.style_menu.pack(side="left", padx=10)

        self.capture_btn = ctk.CTkButton(controls_inner, text="🎥 Capture", width=140,
                                         command=self.toggle_recording,
                                         fg_color="#e94560", hover_color="#c63550")
        self.capture_btn.pack(side="left", padx=10)

        self.gif_btn = ctk.CTkButton(controls_inner, text="💾 Save as GIF", width=140,
                                     command=self.save_gif,
                                     fg_color="#3aa675", hover_color="#2e805c")
        self.gif_btn.pack(side="left", padx=10)

        threading.Thread(target=self.update_video_feed, daemon=True).start()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

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

    def on_close(self):
        self.camera_running = False
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
        self.destroy()

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            style = self.selected_style.get()
            styled_frame = self.apply_style(frame.copy(), style)
            styled_frame = cv2.cvtColor(styled_frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(styled_frame)
            img = img.resize((640, 480))
            self.tk_image = ImageTk.PhotoImage(img)
            self.camera_label.configure(image=self.tk_image)

            if self.recording:
                self.frames.append(styled_frame)

        self.after(10, self.update_frame)

    def update_video_feed(self):
        self.cap = cv2.VideoCapture(0)
        self.after(0, self.update_frame)

    def toggle_recording(self):
        if not self.recording:
            self.capture_btn.configure(text="🛑 Stop")
            self.frames = []
            self.recording = True
        else:
            self.recording = False
            self.capture_btn.configure(text="🎥 Capture")
            threading.Thread(target=self.save_video, daemon=True).start()

    def save_video(self):
        if not self.frames:
            messagebox.showerror("Error", "No frames captured.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".avi",
                                                 filetypes=[("AVI files", "*.avi")])
        if not file_path:
            return

        height, width, _ = self.frames[0].shape
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(file_path, fourcc, 20.0, (width, height))

        for frame in self.frames:
            bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            out.write(bgr_frame)
        out.release()

        messagebox.showinfo("Saved", f"Video saved to:\n{file_path}")

    def save_gif(self):
        if not self.frames:
            messagebox.showerror("Error", "No frames captured.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".gif",
                                                 filetypes=[("GIF files", "*.gif")])
        if not file_path:
            return

        try:
            pil_frames = [Image.fromarray(frame) for frame in self.frames]
            pil_frames[0].save(file_path, save_all=True, append_images=pil_frames[1:], duration=50, loop=0)
            messagebox.showinfo("Saved", f"GIF saved to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save GIF:\n{e}")

    def apply_style(self, img, style):
        if style == "Sketch":
            return self.sketch_effect(img)
        elif style == "Soft Paint":
            return self.watercolor_effect(img)
        elif style == "Bold Edges":
            return self.pencil_sketch(img)[1]
        return img

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

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = VideoToCartoonApp()
    app.mainloop()
