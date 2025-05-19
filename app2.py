import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
import time

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
            
            # Store the cartoonify button reference
            if text == "🎨 Cartoonify":
                self.cartoonify_btn = btn
                self.cartoonify_btn.configure(state=ctk.DISABLED)
        
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
        
        # Add Cartoon Style Selection
        self.create_style_selection()
        
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
            "Detailed Style": {
                "filter_d": 7,
                "edge_threshold": 100,
                "effect_strength": 75
            },
            "Watercolor Sketch": {
                "filter_d": 9,
                "edge_threshold": 150,
                "effect_strength": 90
            },
            "Disney Look": {
                "filter_d": 6,
                "edge_threshold": 80,
                "effect_strength": 85
            },
            "Comic Pop": {
                "filter_d": 5,
                "edge_threshold": 200,
                "effect_strength": 100
            },
            "Pastel Art": {
                "filter_d": 12,
                "edge_threshold": 70,
                "effect_strength": 60
            },
            "Anime Glow": {
                "filter_d": 10,
                "edge_threshold": 120,
                "effect_strength": 95
            }
        }
        
        # Create style option buttons with thumbnails
        self.style_frames = []
        self.style_buttons = {}
        
        # Create buttons container
        self.style_buttons_container = ctk.CTkFrame(self.styles_content, fg_color="#0f3460", corner_radius=0)
        self.style_buttons_container.pack(fill=ctk.X, padx=10, pady=5)
        
        # Create style buttons
        for i, style_name in enumerate(self.styles.keys()):
            style_frame = ctk.CTkFrame(self.style_buttons_container, fg_color="#0f3460", corner_radius=10, width=120, height=140)
            style_frame.grid(row=0, column=i, padx=10, pady=5)
            style_frame.grid_propagate(False)
            
            # Create a frame for the thumbnail (using a colored rectangle as placeholder)
            thumb_frame = ctk.CTkFrame(style_frame, fg_color="#233559", corner_radius=8, width=100, height=100)
            thumb_frame.pack(padx=5, pady=5)
            
            # Label for style name
            style_label = ctk.CTkLabel(
                style_frame, 
                text=style_name, 
                font=("Arial", 12),
                text_color="#ffffff"
            )
            style_label.pack(pady=(0, 5))
            
            # Store references
            self.style_frames.append(style_frame)
            
            # Make the whole frame clickable
            thumb_frame.bind("<Button-1>", lambda e, sn=style_name: self.select_style(sn))
            style_label.bind("<Button-1>", lambda e, sn=style_name: self.select_style(sn))
            style_frame.bind("<Button-1>", lambda e, sn=style_name: self.select_style(sn))
            
            # Add the button to dictionary for later reference
            self.style_buttons[style_name] = style_frame
        
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
        
    def select_style(self, style_name):
        # Update selected style
        self.selected_style = style_name
        
        # Update the style info in status bar
        self.style_info_label.configure(text=f"Style: {style_name}")
        
        # Highlight the selected style and dim others
        for name, frame in self.style_buttons.items():
            if name == style_name:
                frame.configure(fg_color="#e94560")  # Highlight selected
            else:
                frame.configure(fg_color="#0f3460")  # Reset others
        
        # Apply the style parameters
        style_params = self.styles[style_name]
        self.effect_slider.set(style_params["effect_strength"])
        self.update_effect_strength(style_params["effect_strength"])
        self.param_sliders["Bilateral Filter d"].set(style_params["filter_d"])
        self.param_sliders["Edge Threshold"].set(style_params["edge_threshold"])
        
        # Cartoonify with the new style if an image is loaded
        if self.original_image is not None:
            self.cartoonify_image()
            
    def open_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.update_status("Loading image...")
                self.show_progress(0.2)
                
                # Store the file path
                self.current_file_path = file_path
                
                # Read the image with OpenCV
                self.original_image = cv2.imread(file_path)
                if self.original_image is None:
                    raise Exception("Unable to read the image file.")
                
                # Update image info
                h, w = self.original_image.shape[:2]
                file_size = os.path.getsize(file_path) / 1024  # Size in KB
                file_name = os.path.basename(file_path)
                self.info_label.configure(text=f"{file_name} | {w}x{h} | {file_size:.1f} KB")
                
                self.show_progress(0.5)
                
                # Display the original image
                self.display_image(self.original_image, self.original_label)
                
                # Enable the cartoonify and generate buttons
                self.cartoonify_btn.configure(state=ctk.NORMAL)
                self.generate_btn.configure(state=ctk.NORMAL)
                
                # Reset cartoonified image
                self.cartoonified_image = None
                self.cartoon_label.configure(image=None, text="Click 'Cartoonify' to process the image")
                self.save_btn.configure(state=ctk.DISABLED)
                
                self.show_progress(1.0)
                self.update_status("Image loaded successfully")
                
                # Reset progress bar after a delay
                self.root.after(1000, lambda: self.show_progress(0))
                
            except Exception as e:
                messagebox.showerror("Error", f"Error opening image: {str(e)}")
                self.update_status("Error loading image")
                self.show_progress(0)
    
    def display_image(self, img, label):
        if img is None:
            return
            
        # Resize image for display if needed
        h, w = img.shape[:2]
        max_height = 450  # Maximum display height
        max_width = 500   # Maximum display width
        
        # Calculate new dimensions while maintaining aspect ratio
        if h > max_height or w > max_width:
            # Calculate scale factors
            scale_h = max_height / h
            scale_w = max_width / w
            
            # Use the smaller scale factor
            scale = min(scale_h, scale_w)
            
            new_h = int(h * scale)
            new_w = int(w * scale)
            
            img = cv2.resize(img, (new_w, new_h))
        
        # Convert BGR to RGB for display
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Convert to PhotoImage
        img_pil = Image.fromarray(img_rgb)
        img_tk = ImageTk.PhotoImage(image=img_pil)
        
        # Update label
        label.configure(image=img_tk, text="")
        label.image = img_tk  # Keep a reference to prevent garbage collection
    
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
            
            # Get parameter values
            d = int(self.param_sliders["Bilateral Filter d"].get())
            edge_threshold = int(self.param_sliders["Edge Threshold"].get())
            
            # Effect strength factor (0-100%)
            strength = self.effect_strength / 100
            
            # Step 1: Apply bilateral filter for smoothing
            self.show_progress(0.3)
            smoothed = cv2.bilateralFilter(
                self.original_image, 
                d, 
                150 * strength, 
                150 * strength
            )
            
            # Step 2: Convert to grayscale
            self.show_progress(0.5)
            gray = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
            
            # Step 3: Apply median blur
            gray_blur = cv2.medianBlur(gray, 5)
            
            # Step 4: Create edge mask using adaptive thresholding
            self.show_progress(0.7)
            edges = cv2.adaptiveThreshold(
                gray_blur, 
                255, 
                cv2.ADAPTIVE_THRESH_MEAN_C, 
                cv2.THRESH_BINARY, 
                9, 
                edge_threshold / 100
            )
            
            # Step 5: Combine the smoothed color image with the edges
            self.show_progress(0.9)
            color = cv2.bilateralFilter(
                self.original_image, 
                d=int(9 * strength), 
                sigmaColor=int(300 * strength), 
                sigmaSpace=int(300 * strength)
            )
            
            # Apply style-specific effects based on selected style
            cartoon = None
            
            if self.selected_style == "Watercolor Sketch":
                # Apply a more painterly effect
                color = cv2.detailEnhance(color, sigma_s=10, sigma_r=0.15)
                cartoon = cv2.bitwise_and(color, color, mask=edges)
                
            elif self.selected_style == "Comic Pop":
                # Higher contrast, more defined edges
                color = cv2.convertScaleAbs(color, alpha=1.2, beta=10)
                edges = cv2.dilate(edges, np.ones((2, 2), np.uint8))
                cartoon = cv2.bitwise_and(color, color, mask=edges)
                
            elif self.selected_style == "Disney Look":
                # Softer colors, more smoothed
                color = cv2.bilateralFilter(color, 9, 250, 250)
                edges = cv2.medianBlur(edges, 3)
                cartoon = cv2.bitwise_and(color, color, mask=edges)
                
            elif self.selected_style == "Pastel Art":
                # Lighter colors, softer edges
                color = cv2.convertScaleAbs(color, alpha=0.9, beta=30)
                edges = cv2.dilate(edges, np.ones((3, 3), np.uint8))
                cartoon = cv2.bitwise_and(color, color, mask=edges)
                
            elif self.selected_style == "Anime Glow":
                # Vibrant colors, defined edges
                color = cv2.convertScaleAbs(color, alpha=1.3, beta=-15)
                edges = cv2.erode(edges, np.ones((2, 2), np.uint8))
                cartoon = cv2.bitwise_and(color, color, mask=edges)
                
            else:  # Detailed Style or default
                # Apply the effect with varying intensity based on strength
                cartoon = cv2.bitwise_and(color, color, mask=edges)
            
            # Apply general strength blending if strength is less than 100%
            if strength < 1.0:
                # Blend original and cartoon based on strength
                original_weight = 1 - strength
                cartoon = cv2.addWeighted(
                    self.original_image, 
                    original_weight, 
                    cartoon, 
                    strength, 
                    0
                )
            
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