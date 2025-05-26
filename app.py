import os
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
import threading

# Set the appearance mode and color theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class CartoonifyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cartoonify | Modern Image Cartoonification")
        self.root.geometry("1300x800")
        self.root.minsize(1100, 700)
        
        # Variables
        self.original_image = None
        self.cartoonified_image = None
        self.current_file_path = None
        self.processing = False
        self.effect_strength = 75  # Default effect strength
        self.selected_style = "Detailed Style"  # Default style
        
        # Store previews for styles to avoid garbage collection
        self.style_previews = {}
        
        # Create frames
        self.create_frames()
        
        # Create widgets
        self.create_widgets()
        
        # Create status bar
        self.create_status_bar()
        
    def create_frames(self):
        # Main container (fills the entire window)
        self.container = ctk.CTkFrame(self.root, fg_color="#1a1a2e", corner_radius=0)
        self.container.pack(fill=ctk.BOTH, expand=True)
        
        # Header frame
        self.header_frame = ctk.CTkFrame(self.container, fg_color="#16213e", height=70, corner_radius=0)
        self.header_frame.pack(fill=ctk.X, pady=(0, 15))
        self.header_frame.pack_propagate(False)
        
        # Content area (contains sidebar and main content)
        self.content_area = ctk.CTkFrame(self.container, fg_color="#1a1a2e", corner_radius=0)
        self.content_area.pack(fill=ctk.BOTH, expand=True, padx=15, pady=0)
        
        # Sidebar frame
        self.sidebar_frame = ctk.CTkFrame(self.content_area, width=250, fg_color="#0f3460", corner_radius=15)
        self.sidebar_frame.pack(side=ctk.LEFT, fill=ctk.Y, padx=(0, 15), pady=0)
        self.sidebar_frame.pack_propagate(False)  # Prevent the frame from shrinking
        
        # Main content frame
        self.main_content = ctk.CTkFrame(self.content_area, fg_color="#1a1a2e", corner_radius=0)
        self.main_content.pack(side=ctk.RIGHT, fill=ctk.BOTH, expand=True)
        
        # Image display frame
        self.images_frame = ctk.CTkFrame(self.main_content, fg_color="#1a1a2e", corner_radius=0)
        self.images_frame.pack(fill=ctk.BOTH, expand=True, pady=(0, 15))
        
        # Original image frame
        self.original_frame = ctk.CTkFrame(self.images_frame, fg_color="#16213e", corner_radius=15)
        self.original_frame.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True, padx=(0, 8), pady=0)
        
        # Title for original image
        self.original_title_frame = ctk.CTkFrame(self.original_frame, fg_color="#16213e", height=40, corner_radius=15)
        self.original_title_frame.pack(fill=ctk.X, padx=10, pady=10)
        self.original_title = ctk.CTkLabel(self.original_title_frame, text="ORIGINAL IMAGE", font=("Arial Bold", 14))
        self.original_title.pack(fill=ctk.X)
        
        # Original image container
        self.original_container = ctk.CTkFrame(self.original_frame, fg_color="#0f3460", corner_radius=15)
        self.original_container.pack(fill=ctk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Cartoonified image frame
        self.cartoon_frame = ctk.CTkFrame(self.images_frame, fg_color="#16213e", corner_radius=15)
        self.cartoon_frame.pack(side=ctk.RIGHT, fill=ctk.BOTH, expand=True, padx=(8, 0), pady=0)
        
        # Title for cartoon image
        self.cartoon_title_frame = ctk.CTkFrame(self.cartoon_frame, fg_color="#16213e", height=40, corner_radius=15)
        self.cartoon_title_frame.pack(fill=ctk.X, padx=10, pady=10)
        self.cartoon_title = ctk.CTkLabel(self.cartoon_title_frame, text="CARTOONIFIED IMAGE", font=("Arial Bold", 14))
        self.cartoon_title.pack(fill=ctk.X)
        
        # Cartoon image container
        self.cartoon_container = ctk.CTkFrame(self.cartoon_frame, fg_color="#0f3460", corner_radius=15)
        self.cartoon_container.pack(fill=ctk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Add new Cartoon Style selection frame
        self.style_frame = ctk.CTkFrame(self.main_content, fg_color="#16213e", corner_radius=15, height=190)
        self.style_frame.pack(fill=ctk.X, expand=False, pady=(0, 10))
        
        # Status bar at the bottom
        self.status_frame = ctk.CTkFrame(self.container, fg_color="#16213e", height=25, corner_radius=0)
        self.status_frame.pack(fill=ctk.X, side=ctk.BOTTOM)

    #function for voice gen
    def voice_gen():
        print("Clicked the Voice generation button")

    #function for camera_to_cartoon
    def camera_to_cartoon(self):
       from camera_to_cartoon import CartoonCameraApp
       CartoonCameraApp(self)


    def update_camera_feed(self):
        self.cap = cv2.VideoCapture(0)
        while self.camera_running:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.resize(frame, (800, 500))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(img)
                self.camera_preview.configure(image=imgtk)
                self.camera_preview.image = imgtk
            else:
                break
        self.cap.release()

    

    def snap_image(self):
        if hasattr(self, 'cap') and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                selected = self.selected_style.get()
                if selected != "Original" and hasattr(self, 'apply_cartoon_style'):
                    cartooned = self.apply_cartoon_style(frame, selected)
                    self.captured_image = cartooned
                else:
                    self.captured_image = frame
                messagebox.showinfo("Image Captured", "Image has been captured and styled.")
            else:
                messagebox.showerror("Error", "Failed to capture image.")
        else:
            messagebox.showerror("Error", "Camera not available.")

    def save_snapped_image(self):
        if self.captured_image is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                    filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")])
            if file_path:
                cv2.imwrite(file_path, cv2.cvtColor(self.captured_image, cv2.COLOR_RGB2BGR))
                messagebox.showinfo("Saved", f"Image saved to:\n{file_path}")
        else:
            messagebox.showwarning("Warning", "No image to save.")

    #function for video_to_cartoon
    def video_to_cartoon(self):
        from video_to_cartoon import VideoToCartoonApp
        VideoToCartoonApp(self)
            
    def create_widgets(self):
        # Header content
        self.logo_label = ctk.CTkLabel(
            self.header_frame, 
            text="CARTOONIFY", 
            font=("Arial Black", 22),
            text_color="#5045e9"
        )
        self.logo_label.pack(side=ctk.LEFT, padx=20)
        
        self.subtitle_label = ctk.CTkLabel(
            self.header_frame, 
            text="Transform your images into cartoons", 
            font=("Arial", 14),
            text_color="#ffffff"
        )
        self.subtitle_label.pack(side=ctk.LEFT, padx=10)
        
        # Add header buttons on the right
        self.save_btn = ctk.CTkButton(
            self.header_frame, 
            text="Save Image", 
            command=self.save_image,
            fg_color="#e94560",
            hover_color="#c63550",
            font=("Arial Bold", 12),
            state=ctk.DISABLED,
            width=120,
            height=35,
            corner_radius=8
        )
        self.save_btn.pack(side=ctk.RIGHT, padx=20)
        
        # Sidebar title
        self.sidebar_title = ctk.CTkLabel(
            self.sidebar_frame, 
            text="CONTROLS", 
            font=("Arial Bold", 16),
            text_color="#ffffff"
        )
        self.sidebar_title.pack(pady=(20, 10), padx=20, anchor="w")
        
        # Separator
        self.separator = ctk.CTkFrame(self.sidebar_frame, height=2, fg_color="#e94560")
        self.separator.pack(fill=ctk.X, padx=20, pady=(0, 20))
        
        # Sidebar buttons with cleaner design and icons
        buttons = [
            ("📂 Open Image", "#4579e9", self.open_image),
            ("🎨 Cartoonify", "#4579e9", self.cartoonify_image),
            ("🔄 Reset", "#4579e9", self.reset_image)
        ]
        
        for text, color, command in buttons:
            btn = ctk.CTkButton(
                self.sidebar_frame, 
                text=text, 
                fg_color=color, 
                corner_radius=8, 
                command=command,
                font=("Arial Bold", 14),
                text_color="white",
                hover_color="#35b0c6",
                height=40,
                width=200
            )
            btn.pack(padx=20, pady=10)

        # Dropdown menu for additional actions
        self.action_var = ctk.StringVar(value="Select Action")

        self.action_menu = ctk.CTkOptionMenu(
            self.sidebar_frame,
            variable=self.action_var,  # Use 'variable=' explicitly for clarity
            values=["🎤 Voice Gen", "📸 Camera to Cartoon", "🎥 Video to Cartoon"],
            command=self.action_selected
        )
        self.action_menu.pack(padx=20, pady=(20, 10), fill=ctk.X)

        # Button to execute the selected action
        self.execute_action_btn = ctk.CTkButton(
            self.sidebar_frame,
            text="Execute Action",
            command=self.execute_action,
            fg_color="#4579e9",
            hover_color="#35b0c6",
            font=("Arial Bold", 14),
            height=40,
            width=200
        )
        self.execute_action_btn.pack(padx=20, pady=(0, 10))

        # Add effect strength control
        self.effect_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="#0f3460")
        self.effect_frame.pack(fill=ctk.X, padx=20, pady=(30, 10))
        
        self.effect_label = ctk.CTkLabel(
            self.effect_frame, 
            text="Effect Strength", 
            font=("Arial Bold", 14),
            text_color="#ffffff"
        )
        self.effect_label.pack(pady=(10, 5), padx=10)
        
        self.effect_slider = ctk.CTkSlider(
            self.effect_frame,
            from_=0,
            to=100,
            number_of_steps=100,
            command=self.update_effect_strength
        )
        self.effect_slider.set(self.effect_strength)
        self.effect_slider.pack(padx=10, pady=5, fill=ctk.X)
        
        self.effect_value = ctk.CTkLabel(
            self.effect_frame, 
            text=f"{self.effect_strength}%", 
            font=("Arial", 12)
        )
        self.effect_value.pack(pady=(0, 10))
        
        # Add parameters section
        self.params_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="ADVANCED PARAMETERS", 
            font=("Arial Bold", 16),
            text_color="#ffffff"
        )
        self.params_label.pack(pady=(30, 10), padx=20, anchor="w")
        
        # Separator
        self.separator2 = ctk.CTkFrame(self.sidebar_frame, height=2, fg_color="#e94560")
        self.separator2.pack(fill=ctk.X, padx=20, pady=(0, 15))
        
        # Parameter sliders
        parameters = [
            ("Bilateral Filter d", 5, 15, 7),
            ("Edge Threshold", 50, 200, 100)
        ]
        
        self.param_sliders = {}
        for name, min_val, max_val, default in parameters:
            param_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="#0f3460")
            param_frame.pack(fill=ctk.X, padx=20, pady=5)
            
            param_label = ctk.CTkLabel(
                param_frame, 
                text=name, 
                font=("Arial", 12),
                text_color="#ffffff"
            )
            param_label.pack(pady=(5, 0), padx=10, anchor="w")
            
            slider = ctk.CTkSlider(
                param_frame,
                from_=min_val,
                to=max_val,
                number_of_steps=int(max_val-min_val)
            )
            slider.set(default)
            slider.pack(padx=10, pady=(0, 5), fill=ctk.X)
            
            # Store the slider reference
            self.param_sliders[name] = slider
        
        # Image display labels
        self.original_label = ctk.CTkLabel(
            self.original_container, 
            text="No image loaded\n\nClick 'Open Image' to begin",
            font=("Arial", 14),
            text_color="#ffffff"
        )
        self.original_label.pack(fill=ctk.BOTH, expand=True)
        
        self.cartoon_label = ctk.CTkLabel(
            self.cartoon_container, 
            text="Your cartoonified image will appear here", 
            font=("Arial", 14),
            text_color="#ffffff"
        )
        self.cartoon_label.pack(fill=ctk.BOTH, expand=True)
        
        # Add a progress bar for cartoonification
        self.progress_container = ctk.CTkFrame(self.sidebar_frame, fg_color="#0f3460")
        self.progress_container.pack(fill=ctk.X, padx=20, pady=(30, 0))
        
        self.progress_label = ctk.CTkLabel(
            self.progress_container, 
            text="Processing:", 
            font=("Arial", 12),
            text_color="#ffffff"
        )
        self.progress_label.pack(pady=(10, 5), padx=10, anchor="w")
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_container)
        self.progress_bar.pack(padx=10, pady=(0, 10), fill=ctk.X)
        self.progress_bar.set(0)

        for text, color, command in buttons:
            btn = ctk.CTkButton(
                self.sidebar_frame,
                text=text,
                fg_color=color,
                corner_radius=8,
                command=command,
                font=("Arial Bold", 14),
                text_color="white",
                hover_color="#35b0c6",
                height=40,
                width=200
            )
            btn.pack(padx=20, pady=10)

            if text == "🎨 Cartoonify":
                self.cartoonify_btn = btn  # ✅ Save reference for later use

        
        # Add Cartoon Style Selection
        self.create_style_selection()

    # Method to handle action selection
    def action_selected(self, value):
        print(f"Selected action: {value}")

    # Method to execute the selected action
    def execute_action(self):
        selected_action = self.action_var.get()
        if selected_action == "🎤 Voice Gen":
            self.voice_gen()
        elif selected_action == "📸 Camera to Cartoon":
            self.camera_to_cartoon()
        elif selected_action == "🎥 Video to Cartoon":
            self.video_to_cartoon()
        else:
            messagebox.showwarning("Warning", "Please select a valid action.")


        
    def create_style_selection(self):
        # Title for style selection
        self.style_title_frame = ctk.CTkFrame(self.style_frame, fg_color="#16213e", height=40, corner_radius=15)
        self.style_title_frame.pack(fill=ctk.X, padx=10, pady=10)
        
        self.style_title = ctk.CTkLabel(
            self.style_title_frame, 
            text="CHOOSE A CARTOON STYLE", 
            font=("Arial Bold", 16),
            text_color="#ffffff"
        )
        self.style_title.pack(fill=ctk.X)
        
        self.style_subtitle = ctk.CTkLabel(
            self.style_title_frame, 
            text="Click one of the styles below to apply it to your image", 
            font=("Arial", 12),
            text_color="#ffffff"
        )
        self.style_subtitle.pack(fill=ctk.X)
        
        # Create style options container
        self.styles_container = ctk.CTkFrame(self.style_frame, fg_color="#0f3460", corner_radius=15)
        self.styles_container.pack(fill=ctk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Style options frame
        self.styles_content = ctk.CTkFrame(self.styles_container, fg_color="#0f3460", corner_radius=0)
        self.styles_content.pack(fill=ctk.BOTH, expand=True, padx=20, pady=10)
        
        # Define styles with their parameters
        self.styles = {
            "Pencil Sketch": {
                "effect_function": self.cartoonify_image_mixed,
                "effect_strength": 75
            },
            "Detail Enhance": {
                "effect_function": self.detail_enhance,
                "effect_strength": 75
            },
            "Watercolor Effect": {
                "effect_function": self.watercolor_effect,  
                "effect_strength": 90
            },
            "Quantize": {
                "effect_function": self.color_quantization,
                "effect_strength": 80
            },
            "Sketch Effect": {
                "effect_function": self.sketch_effect,
                "effect_strength": 70
            },
            "Vignette": {
                "effect_function": self.vignette,
                "effect_strength": 60
            },
            "Lomo": {
                "effect_function": self.lomo,
                "effect_strength": 70
            },
            "Cartoon Style 1":{
                "effect_function": self.cartoonify_image_mixed,
                "effect_strength": 74
            }
        }

        
        # Create style option buttons with thumbnails
        self.style_frames = []
        self.style_buttons = {}
        self.style_thumb_labels = {}

        self.style_buttons_container = ctk.CTkFrame(self.styles_content, fg_color="#0f3460", corner_radius=0)
        self.style_buttons_container.pack(fill=ctk.X, padx=10, pady=5)
        
        # Create style buttons with an image label for preview
        for i, style_name in enumerate(self.styles.keys()):
            style_frame = ctk.CTkFrame(self.style_buttons_container, fg_color="#0f3460", corner_radius=10, width=120, height=140)
            style_frame.grid(row=0, column=i, padx=10, pady=5)
            style_frame.grid_propagate(False)
            
            # Thumbnail image label placeholder (initially blank)
            thumb_label = ctk.CTkLabel(style_frame, fg_color="#233559", corner_radius=8, width=100, height=100, text="No Preview", font=("Arial", 10))
            thumb_label.pack(padx=5, pady=5)
            
            # Style name label
            style_label = ctk.CTkLabel(
                style_frame, 
                text=style_name, 
                font=("Arial", 12),
                text_color="#ffffff"
            )
            style_label.pack(pady=(0, 5))
            
            self.style_frames.append(style_frame)
            self.style_buttons[style_name] = style_frame
            self.style_thumb_labels[style_name] = thumb_label
            
            # Bind the whole frame and labels for style selection on click
            thumb_label.bind("<Button-1>", lambda e, sn=style_name: self.select_style(sn))
            style_label.bind("<Button-1>", lambda e, sn=style_name: self.select_style(sn))
            style_frame.bind("<Button-1>", lambda e, sn=style_name: self.select_style(sn))
        
        # Add Generate button
        self.generate_btn = ctk.CTkButton(
            self.style_frame, 
            text="Generate Cartoon", 
            command=self.cartoonify_image,
            fg_color="#4579e9",
            hover_color="#35b0c6",
            font=("Arial Bold", 14),
            state=ctk.DISABLED,
            height=40,
            width=200
        )
        self.generate_btn.pack(pady=(0, 10))
        
    def create_status_bar(self):
        # Status bar content
        self.status_label = ctk.CTkLabel(
            self.status_frame, 
            text="Ready", 
            font=("Arial", 11),
            text_color="#ffffff"
        )
        self.status_label.pack(side=ctk.LEFT, padx=10)
        
        # Add image info to the right
        self.info_label = ctk.CTkLabel(
            self.status_frame, 
            text="No image loaded", 
            font=("Arial", 11),
            text_color="#ffffff"
        )
        self.info_label.pack(side=ctk.RIGHT, padx=10)
        
        # Add selected style info to center
        self.style_info_label = ctk.CTkLabel(
            self.status_frame, 
            text="Style: Detailed Style", 
            font=("Arial", 11),
            text_color="#ffffff"
        )
        self.style_info_label.pack(side=ctk.RIGHT, padx=10)
        
    def update_effect_strength(self, value):
        self.effect_strength = int(value)
        self.effect_value.configure(text=f"{self.effect_strength}%")
        
    def update_status(self, message):
        self.status_label.configure(text=message)
        self.root.update()
        
    def show_progress(self, value):
        self.progress_bar.set(value)
        self.root.update()
        
    def open_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.update_status("Loading image...")
                self.show_progress(0.2)
                
                self.current_file_path = file_path
                self.original_image = cv2.imread(file_path)
                if self.original_image is None:
                    raise Exception("Unable to read the image file.")
                
                h, w = self.original_image.shape[:2]
                file_size = os.path.getsize(file_path) / 1024
                file_name = os.path.basename(file_path)
                self.info_label.configure(text=f"{file_name} | {w}x{h} | {file_size:.1f} KB")
                
                self.show_progress(0.5)
                self.display_image(self.original_image, self.original_label)
                
                self.cartoonify_btn.configure(state=ctk.NORMAL)
                self.generate_btn.configure(state=ctk.NORMAL)
                
                self.cartoonified_image = None
                self.cartoon_label.configure(image=None, text="Click 'Cartoonify' to process the image")
                self.save_btn.configure(state=ctk.DISABLED)
                
                # Generate previews for each style and update the style cards
                self.generate_all_style_previews()
                
                self.show_progress(1.0)
                self.update_status("Image loaded successfully with style previews")
                self.root.after(1000, lambda: self.show_progress(0))
                
            except Exception as e:
                messagebox.showerror("Error", f"Error opening image: {str(e)}")
                self.update_status("Error loading image")
                self.show_progress(0)
    
    def generate_all_style_previews(self):
        if self.original_image is None:
            return
        
        for style_name in self.styles.keys():
            preview_img = self.generate_style_preview(self.original_image, style_name)
            if preview_img is not None:
                h, w = preview_img.shape[:2]
                max_dim = 100
                scale = min(max_dim / w, max_dim / h, 1)
                new_w, new_h = int(w * scale), int(h * scale)
                resized_img = cv2.resize(preview_img, (new_w, new_h))
                rgb_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(rgb_img)
                img_tk = ImageTk.PhotoImage(pil_img)
                
                self.style_previews[style_name] = img_tk
                
                thumb_label = self.style_thumb_labels.get(style_name)
                if thumb_label:
                    thumb_label.configure(image=img_tk, text="")
                    thumb_label.image = img_tk
                    
    def pencil_sketch(self, img, sigma_s=60, sigma_r=0.07, shade_factor=0.05):
        gray, color = cv2.pencilSketch(img, sigma_s=sigma_s, sigma_r=sigma_r, shade_factor=shade_factor)
        return gray, color
    
    def cartoonify_image_mixed(self, img, sigma_s=75, **kwargs):
        num_bilateral = 7  # Number of bilateral filtering steps
        img_color = img.copy()

        for _ in range(num_bilateral):
            img_color = cv2.bilateralFilter(img_color, d=9, sigmaColor=sigma_s, sigmaSpace=sigma_s)

        # Convert to grayscale and apply median blur
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img_blur = cv2.medianBlur(img_gray, 7)

        # Edge detection using adaptive threshold
        edges = cv2.adaptiveThreshold(
            img_blur, 255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY,
            blockSize=9,
            C=2
        )

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

        # Overlay edges as black lines
        cartoon_img[edges == 0] = 0  # Make edges black

        # Enhance contrast by converting to LAB and increasing L channel
        lab = cv2.cvtColor(cartoon_img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        cl = clahe.apply(l)
        lab = cv2.merge((cl, a, b))
        enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

        return cv2.cvtColor(cartoon_img, cv2.COLOR_BGR2GRAY), enhanced




    def detail_enhance(self, img, sigma_s=10, sigma_r=0.15):
        return cv2.detailEnhance(img, sigma_s=sigma_s, sigma_r=sigma_r)

    def watercolor_effect(self, img, d=9):
        color = cv2.bilateralFilter(img, d, 300, 300)
        gray = cv2.cvtColor(color, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 7)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                    cv2.THRESH_BINARY, 9, 9)
        return cv2.bitwise_and(color, color, mask=edges)

    def color_quantization(self, img, k=8):
        data = np.float32(img).reshape((-1, 3))
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
        _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        centers = np.uint8(centers)
        quantized = centers[labels.flatten()]
        return quantized.reshape(img.shape)

    def sketch_effect(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        inverted = cv2.bitwise_not(gray)
        blurred = cv2.GaussianBlur(inverted, (21, 21), 0)
        inverted_blurred = cv2.bitwise_not(blurred)
        return cv2.divide(gray, inverted_blurred, scale=256.0)
    
    def anime_style_effect(self, img):

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
        anime_img = cv2.bitwise_and(quantized, edges_colored)
        
        #  Overlay edges as black lines
        anime_img[edges == 0] = 0  # Make edges black
        
        #  enhance contrast by converting to LAB and increasing L channel
        lab = cv2.cvtColor(anime_img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        cl = clahe.apply(l)
        lab = cv2.merge((cl,a,b))
        enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        return enhanced



    def vignette(self, img, strength=1.0):
        rows, cols = img.shape[:2]
        kernel_x = cv2.getGaussianKernel(cols, cols/3)
        kernel_y = cv2.getGaussianKernel(rows, rows/3)
        kernel = kernel_y * kernel_x.T
        mask = kernel / kernel.max()
        masked = np.copy(img)
        for i in range(3):
            masked[:, :, i] = img[:, :, i] * mask * strength
        return masked

    def lomo(self, img, saturation_increase=50):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        img[:, :, 1] = cv2.add(img[:, :, 1], saturation_increase)
        img = cv2.cvtColor(img, cv2.COLOR_HSV2BGR)
        return cv2.GaussianBlur(img, (15, 15), 0)


    
    def generate_style_preview(self, img, style_name):
        try: 
            params = self.styles[style_name]
            effect_function = params["effect_function"]
            
            result = effect_function(img)
            # Handle if effect_function returns tuple (like pencil_sketch)
            if isinstance(result, tuple):
                # Prefer the color image part (usually second element)
                cartoon = result[1]
            else:
                cartoon = result
            
            return cartoon
        except Exception as e:
            print(f"Error generating preview for style {style_name}: {e}")
            return None
        
    def select_style(self, style_name):
        self.selected_style = style_name
        self.style_info_label.configure(text=f"Style: {style_name}")
        for name, frame in self.style_buttons.items():
            if name == style_name:
                frame.configure(fg_color="#e94560")
            else:
                frame.configure(fg_color="#0f3460")
        style_params = self.styles[style_name]
        self.effect_slider.set(style_params.get("effect_strength", 75))
        # Update sliders if present
        if "filter_d" in style_params:
            self.param_sliders["Bilateral Filter d"].set(style_params["filter_d"])
        if "edge_threshold" in style_params:
            self.param_sliders["Edge Threshold"].set(style_params["edge_threshold"])
        self.update_effect_strength(self.effect_slider.get())
        # Remove or comment out the auto cartoonify call
        # if self.original_image is not None:
        #     self.cartoonify_image()
            
    def display_image(self, img, label):
        if img is None:
            return
            
        h, w = img.shape[:2]
        max_height = 450
        max_width = 500
        
        if h > max_height or w > max_width:
            scale_h = max_height / h
            scale_w = max_width / w
            scale = min(scale_h, scale_w)
            new_h = int(h * scale)
            new_w = int(w * scale)
            img = cv2.resize(img, (new_w, new_h))
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_tk = ImageTk.PhotoImage(image=img_pil)
        
        label.configure(image=img_tk, text="")
        label.image = img_tk
    
    def cartoonify_image(self):
        if self.original_image is None:
            messagebox.showwarning("Warning", "Please open an image first.")
            return
        
        if self.processing:
            return
                
        self.processing = True
        try:
            self.update_status(f"Processing image with {self.selected_style}...")
            self.show_progress(0.1)
            
            # Fetch the effect function for the selected style
            effect_function = self.styles[self.selected_style]["effect_function"]
            
            # Prepare parameters from sliders
            params = {}
            if self.selected_style == "Pencil Sketch":
                params = {
                    "sigma_s": self.effect_strength,
                    "sigma_r": 0.07,
                    "shade_factor": 0.05
                }
            elif self.selected_style == "Detail Enhance":
                params = {
                    "sigma_s": self.effect_strength,
                    "sigma_r": 0.15
                }
            elif self.selected_style == "Watercolor Effect":
                params = {
                    "d": int(self.param_sliders["Bilateral Filter d"].get())
                }
            # Add similar parameter handling for other styles as needed
            
            # Apply the effect function on the original image
            result = effect_function(self.original_image, **params)
            
            # Handle tuple output (e.g. pencil_sketch)
            if isinstance(result, tuple):
                cartoon = result[1]
            else:
                cartoon = result
            
            # Store the cartoonified image
            self.cartoonified_image = cartoon
            
            # Display the cartoonified image
            self.display_image(cartoon, self.cartoon_label)
            
            # Enable the save button
            self.save_btn.configure(state=ctk.NORMAL)
            
            self.show_progress(1.0)
            self.update_status(f"Image cartoonified with {self.selected_style} style")
            
            # Reset progress bar after a delay
            self.root.after(1000, lambda: self.show_progress(0))
            
        except Exception as e:
            messagebox.showerror("Error", f"Error during cartoonification: {str(e)}")
            self.update_status("Error processing image")
            self.show_progress(0)
        finally:
            self.processing = False


    
    def save_image(self):
        if self.cartoonified_image is None:
            messagebox.showwarning("Warning", "No cartoonified image to save.")
            return
        
        # Get original filename without extension
        if self.current_file_path:
            original_filename = os.path.splitext(os.path.basename(self.current_file_path))[0]
            suggested_name = f"{original_filename}_{self.selected_style.lower().replace(' ', '_')}.jpg"
        else:
            suggested_name = f"cartoonified_image_{self.selected_style.lower().replace(' ', '_')}.jpg"
        
        # Open save file dialog
        file_path = filedialog.asksaveasfilename(
            title="Save Cartoonified Image",
            defaultextension=".jpg",
            initialfile=suggested_name,
            filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.update_status("Saving image...")
                self.show_progress(0.5)
                
                # Save the image
                cv2.imwrite(file_path, self.cartoonified_image)
                
                self.show_progress(1.0)
                self.update_status(f"Image saved: {os.path.basename(file_path)}")
                messagebox.showinfo("Success", f"Image saved successfully to:\n{file_path}")
                
                # Reset progress bar after a delay
                self.root.after(1000, lambda: self.show_progress(0))
                
            except Exception as e:
                messagebox.showerror("Error", f"Error saving image: {str(e)}")
                self.update_status("Error saving image")
                self.show_progress(0)
    
    def reset_image(self):
        if self.original_image is not None:
            # Reset the cartoonified image to show original
            self.cartoonified_image = None
            self.cartoon_label.configure(image=None, text="Click 'Cartoonify' to process the image")
            self.save_btn.configure(state=ctk.DISABLED)
            
            # Reset sliders to defaults
            self.effect_slider.set(75)
            self.update_effect_strength(75)
            self.param_sliders["Bilateral Filter d"].set(7)
            self.param_sliders["Edge Threshold"].set(100)
            
            self.update_status("Reset complete")
    
def main():
    root = ctk.CTk()
    app = CartoonifyApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

