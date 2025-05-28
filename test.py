import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np

ctk.set_appearance_mode("dark")  # Modes: system, light, dark
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

class AnimeCartoonApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Anime Cartoon Image Converter")
        self.geometry("1100x600")

        # Initialize images
        self.original_img_cv = None  # Original image as OpenCV array
        self.cartoon_img_cv = None   # Processed cartoon image as OpenCV array
        self.original_img_tk = None  # For display in label
        self.cartoon_img_tk = None   # For display in label

        self.create_widgets()

    def create_widgets(self):
        # Create frame for buttons on left
        control_frame = ctk.CTkFrame(self, width=200)
        control_frame.pack(side="left", fill="y", padx=10, pady=10)

        self.btn_upload = ctk.CTkButton(control_frame, text="Upload Image", command=self.upload_image)
        self.btn_upload.pack(pady=(20,10), padx=10)

        self.btn_cartoonize = ctk.CTkButton(control_frame, text="Apply Anime Cartoon Effect", command=self.apply_cartoon, state="disabled")
        self.btn_cartoonize.pack(pady=10, padx=10)

        self.btn_save = ctk.CTkButton(control_frame, text="Save Output Image", command=self.save_image, state="disabled")
        self.btn_save.pack(pady=10, padx=10)

        # Frame for images display
        display_frame = ctk.CTkFrame(self)
        display_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Labels for original and cartoon images
        self.label_original = ctk.CTkLabel(display_frame, text="Original Image", anchor="center", font=ctk.CTkFont(size=20, weight="bold"))
        self.label_original.pack(pady=(0,10))

        self.canvas_original = ctk.CTkLabel(display_frame, text="No Image Loaded", fg_color="#222222", width=420, height=420, corner_radius=10, anchor="center")
        self.canvas_original.pack(pady=(0,20))

        self.label_cartoon = ctk.CTkLabel(display_frame, text="Anime Cartoon Image", anchor="center", font=ctk.CTkFont(size=20, weight="bold"))
        self.label_cartoon.pack(pady=(0,10))

        self.canvas_cartoon = ctk.CTkLabel(display_frame, text="No Image Processed", fg_color="#222222", width=420, height=420, corner_radius=10, anchor="center")
        self.canvas_cartoon.pack()

    def upload_image(self):
        filetypes = (
            ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"),
            ("All files", "*.*")
        )
        filepath = filedialog.askopenfilename(title="Open Image", filetypes=filetypes)
        if not filepath:
            return
        
        # Load image with OpenCV
        img_cv = cv2.imread(filepath)
        if img_cv is None:
            messagebox.showerror("Error", "Failed to open image file!")
            return
        
        self.original_img_cv = img_cv
        self.cartoon_img_cv = None  # Reset processed image
        self.btn_cartoonize.configure(state="normal")
        self.btn_save.configure(state="disabled")

        # Display original image
        self.display_image(img_cv, "original")

        # Reset cartoon canvas
        self.canvas_cartoon.configure(image=None, text="No Image Processed")

    def display_image(self, img_cv, mode):
        """
        Convert cv2 image to PhotoImage and display in correct label.
        mode: "original" or "cartoon"
        """
        # Convert color space BGR to RGB
        img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)

        # Convert to PIL Image
        im_pil = Image.fromarray(img_rgb)

        # Resize image to fit 420x420 box, keeping aspect ratio
        im_pil.thumbnail((420, 420))

        # Convert to ImageTk.PhotoImage
        im_tk = ImageTk.PhotoImage(im_pil)

        if mode == "original":
            self.original_img_tk = im_tk
            self.canvas_original.configure(image=self.original_img_tk, text="")
        elif mode == "cartoon":
            self.cartoon_img_tk = im_tk
            self.canvas_cartoon.configure(image=self.cartoon_img_tk, text="")

    def apply_cartoon(self):
        if self.original_img_cv is None:
            messagebox.showwarning("Warning", "Please upload an image first.")
            return

        # Apply anime cartoon effect
        cartoon_img = self.cartoonify_image_mixed(self.original_img_cv)

        self.cartoon_img_cv = cartoon_img
        self.btn_save.configure(state="normal")

        # Display cartoon image
        self.display_image(cartoon_img, "cartoon")

    def cartoonify_image_mixed(self, img):
        num_bilateral = 7  # Number of bilateral filtering steps
        img_color = img.copy()
        for _ in range(num_bilateral):
            img_color = cv2.bilateralFilter(img_color, d=9, sigmaColor=75, sigmaSpace=75)
            
        # Convert to grayscale and apply median blur
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img_blur = cv2.medianBlur(img_gray, 7)
        
        # Edge detection using adaptive threshold
        edges = cv2.adaptiveThreshold(img_blur, 255,
                                    cv2.ADAPTIVE_THRESH_MEAN_C,
                                    cv2.THRESH_BINARY,
                                    blockSize=9,
                                    C=2)
        
        # Color quantization using k-means clustering for cell shading
        data = np.float32(img_color).reshape((-1, 3))
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.001)
        k = 8  # number of colors
        _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        centers = np.uint8(centers)
        quantized = centers[labels.flatten()]
        quantized = quantized.reshape(img_color.shape)
        
        # Combine quantized colors and edges
        edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        cartoon_img = cv2.bitwise_and(quantized, edges_colored)
        
        #  Overlay edges as black lines
        cartoon_img[edges == 0] = 0  # Make edges black
        
        #  enhance contrast by converting to LAB and increasing L channel
        lab = cv2.cvtColor(cartoon_img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        cl = clahe.apply(l)
        lab = cv2.merge((cl,a,b))
        enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        return enhanced


    def save_image(self):
        if self.cartoon_img_cv is None:
            messagebox.showwarning("Warning", "No cartoon image to save.")
            return

        file = filedialog.asksaveasfilename(defaultextension=".png",
                                            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg;*.jpeg"), ("All files", "*.*")],
                                            title="Save Cartoon Image")
        if not file:
            return
        # Save image using OpenCV
        success = cv2.imwrite(file, self.cartoon_img_cv)
        if success:
            messagebox.showinfo("Saved", f"Image saved successfully:\n{file}")
        else:
            messagebox.showerror("Error", "Failed to save the image.")

if __name__ == "__main__":
    app = AnimeCartoonApp()
    app.mainloop()

