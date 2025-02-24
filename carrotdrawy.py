from tkinter import *
from tkinter import filedialog, ttk, messagebox
from PIL import ImageTk, Image, ImageOps, ImageFilter
import pyautogui
import numpy as np
from numpy import asarray
import cv2
import keyboard
import time
import threading

class Picture:
    def __init__(self):
        self.source = Image.new(mode="RGB", size=(0,0))
        self.preview = Image.new(mode="RGB", size=(0,0))
        self.current_layer = None
        
class Settings:
    def __init__(self):
        self.size = (70, 50)
        self.armed = False
        self.interrupted = False
        self.mode = "Binary"
        self.pixel_size = 1
        self.speed = "Fast"
        self.drawing = False
        self.start_pos = None
        self.use_ghost = False
        self.last_update = 0

class AutoDrawer:
    def __init__(self):
        self.root = Tk()
        self.root.title('carrotdrawy v1.8.2')
        self.root.geometry('900x600')
        self.pic = Picture()
        self.settings = Settings()
        self.layers = []
        self.current_layer_index = 0
        self.ghost_window = None
        self.size_ratio = 1.0
        
        pyautogui.PAUSE = 0.001
        
        self.setup_ui()
        self.setup_bindings()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=BOTH, expand=True)
        
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=LEFT, fill=Y, padx=(0, 10))
        
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=RIGHT, fill=BOTH, expand=True)
        
        top_frame = ttk.LabelFrame(left_frame, text="Controls", padding="5")
        top_frame.pack(fill=X, pady=(0, 10))
        
        Button(top_frame, text="Load Image", command=self.load_image).pack(side=LEFT, padx=5)
        self.arm_button = Button(top_frame, text="Arm Drawing", command=self.toggle_arm)
        self.arm_button.pack(side=LEFT, padx=5)
        Button(top_frame, text="Stop", command=self.interrupt, fg="red").pack(side=LEFT, padx=5)
        self.ghost_var = BooleanVar(value=False)
        ttk.Checkbutton(top_frame, text="Use Ghost Image", variable=self.ghost_var,
                       command=self.toggle_ghost).pack(side=LEFT, padx=5)
        
        settings_frame = ttk.LabelFrame(left_frame, text="Settings", padding="5")
        settings_frame.pack(fill=X, pady=5)
        
        ttk.Label(settings_frame, text="Image Size:").grid(row=0, column=0, padx=5, pady=5)
        self.size_scale_var = IntVar(value=70)
        ttk.Scale(settings_frame, from_=10, to=500, orient=HORIZONTAL,
                 variable=self.size_scale_var, command=self.update_size).grid(row=0, column=1, columnspan=2, padx=5, sticky="ew")
        self.size_label = ttk.Label(settings_frame, text="70x50")
        self.size_label.grid(row=0, column=3, padx=5)
        
        ttk.Label(settings_frame, text="Drawing Speed:").grid(row=1, column=0, padx=5, pady=5)
        self.speed_var = StringVar(value="Fast")
        ttk.Combobox(settings_frame, textvariable=self.speed_var, 
                    values=["Fastest", "Fast", "Medium", "Slow"],
                    width=10).grid(row=1, column=1, padx=5)
        
        ttk.Label(settings_frame, text="Pixel Size:").grid(row=2, column=0, padx=5, pady=5)
        self.pixel_size_var = IntVar(value=1)
        ttk.Spinbox(settings_frame, from_=1, to=10, textvariable=self.pixel_size_var, 
                   width=5, command=self.update_settings).grid(row=2, column=1, padx=5)
        
        self.notebook = ttk.Notebook(left_frame)
        self.notebook.pack(fill=BOTH, expand=True, pady=5)
        
        self.setup_modes()
        
        preview_frame = ttk.LabelFrame(right_frame, text="Preview", padding="5")
        preview_frame.pack(fill=BOTH, expand=True)
        
        self.canvas = Canvas(preview_frame, width=500, height=300, bg="white")
        self.canvas.pack(fill=BOTH, expand=True)
        
        self.status_var = StringVar(value="Ready")
        ttk.Label(right_frame, textvariable=self.status_var).pack(side=BOTTOM, pady=5)
        
    def setup_modes(self):
        self.binary_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.binary_frame, text='Binary Mode')
        
        ttk.Label(self.binary_frame, text="Threshold:").pack(pady=5)
        self.threshold_var = IntVar(value=128)
        ttk.Scale(self.binary_frame, from_=0, to=255, orient=HORIZONTAL,
                 variable=self.threshold_var, command=self.debounce_preview).pack(fill=X, padx=10)
        ttk.Button(self.binary_frame, text="Invert Colors", 
                  command=self.invert_image).pack(pady=5)
        ttk.Button(self.binary_frame, text="Draw Now", 
                  command=lambda: self.draw_current("Binary")).pack(pady=5)
        
        self.shading_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.shading_frame, text='Shading Mode')
        
        ttk.Label(self.shading_frame, text="Number of Layers:").pack(pady=5)
        self.shading_layers_var = IntVar(value=3)
        ttk.Spinbox(self.shading_frame, from_=2, to=10,
                   textvariable=self.shading_layers_var, width=5,
                   command=self.update_preview).pack()
        ttk.Button(self.shading_frame, text="Prepare Layers",
                  command=self.prepare_shading).pack(pady=5)
        ttk.Button(self.shading_frame, text="Draw Next Layer",
                  command=self.draw_next_layer).pack(pady=5)
        self.shading_order_label = ttk.Label(self.shading_frame, text="Layer Order: N/A")
        self.shading_order_label.pack(pady=5)
        
        self.color_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.color_frame, text='Color Mode')
        
        ttk.Label(self.color_frame, text="Number of Colors:").pack(pady=5)
        self.color_count_var = IntVar(value=5)
        ttk.Spinbox(self.color_frame, from_=2, to=10,
                   textvariable=self.color_count_var, width=5,
                   command=self.update_preview).pack()
        ttk.Button(self.color_frame, text="Prepare Colors",
                  command=self.prepare_colors).pack(pady=5)
        ttk.Button(self.color_frame, text="Draw Next Color",
                  command=self.draw_next_layer).pack(pady=5)
        self.color_info = ttk.Label(self.color_frame, text="")
        self.color_info.pack(pady=5)
        self.color_preview = Canvas(self.color_frame, width=50, height=20)
        self.color_preview.pack(pady=5)
        self.color_list_frame = ttk.Frame(self.color_frame)
        self.color_list_frame.pack(fill=X, pady=5)
        self.color_list_canvas = []
        self.color_order_label = ttk.Label(self.color_frame, text="Color Order: N/A")
        self.color_order_label.pack(pady=5)
        
    def setup_bindings(self):
        self.root.bind('<Return>', lambda e: self.draw_current(self.get_current_mode()))
        keyboard.add_hotkey('esc', self.interrupt)
        
    def load_image(self):
        filename = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")])
        if filename:
            self.pic.source = Image.open(filename).convert("RGB")
            w, h = self.pic.source.size
            self.size_ratio = w / h
            max_size = min(500, max(w, h))
            self.size_scale_var.set(int(max_size * min(500/w, 300/h)))
            self.update_size()
            self.status_var.set(f"Image loaded: {filename.split('/')[-1]}")
            self.settings.start_pos = None
            self.layers = []
            self.current_layer_index = 0
            self.clear_color_list()
            
    def update_size(self, *args):
        width = self.size_scale_var.get()
        height = int(width / self.size_ratio)
        if width < 10:
            width = 10
            height = int(width / self.size_ratio)
        elif width > 500:
            width = 500
            height = int(width / self.size_ratio)
        self.settings.size = (width, height)
        self.size_label.config(text=f"{width}x{height}")
        self.size_scale_var.set(width)
        self.debounce_preview()
        if self.ghost_window:
            self.show_ghost()
            
    def debounce_preview(self, *args):
        current_time = time.time()
        if current_time - self.settings.last_update > 0.1:
            self.update_preview()
            self.settings.last_update = current_time
            
    def update_preview(self, *args):
        if self.pic.source.size == (0,0):
            return
            
        current_mode = self.get_current_mode()
        
        if current_mode == "Binary":
            img_gray = self.pic.source.convert('L')
            threshold = self.threshold_var.get()
            preview = img_gray.point(lambda p: 0 if p > threshold else 255)
        elif current_mode == "Shading" and self.layers and self.current_layer_index < len(self.layers):
            preview = self.layers[self.current_layer_index]
            self.shading_order_label.config(text=f"Layer Order: Dark to Light ({self.current_layer_index + 1}/{len(self.layers)})")
        elif current_mode == "Color" and self.layers and self.current_layer_index < len(self.layers):
            color = self.layers[self.current_layer_index]['color']
            mask = self.layers[self.current_layer_index]['mask'].resize(self.settings.size)
            preview_data = np.full((self.settings.size[1], self.settings.size[0], 3), 255, dtype=np.uint8)
            mask_data = asarray(mask)
            preview_data[mask_data == 0] = color
            preview = Image.fromarray(preview_data)
            self.color_info.config(text=f"Current Color: RGB{color}")
            self.color_preview.delete("all")
            self.color_preview.create_rectangle(0, 0, 50, 20, fill=f'#{color[0]:02x}{color[1]:02x}{color[2]:02x}')
            self.update_color_list()
            self.color_order_label.config(text=f"Color Order: {self.current_layer_index + 1}/{len(self.layers)}")
        else:
            preview = self.pic.source
            
        preview = preview.resize(self.settings.size)
        preview.thumbnail((500, 300))
        self.pic.preview = ImageTk.PhotoImage(preview)
        self.canvas.delete("all")
        self.canvas.create_image(250, 150, image=self.pic.preview)
        
    def update_color_list(self):
        self.clear_color_list()
        
        for i, layer in enumerate(self.layers):
            frame = ttk.Frame(self.color_list_frame)
            frame.pack(fill=X)
            
            canvas = Canvas(frame, width=20, height=20)
            canvas.pack(side=LEFT, padx=(0, 5))
            color = layer['color']
            hex_color = f'#{color[0]:02x}{color[1]:02x}{color[2]:02x}'
            canvas.create_rectangle(0, 0, 20, 20, fill=hex_color, 
                                  outline='red' if i == self.current_layer_index else 'black')
            
            label = ttk.Label(frame, text=f"Layer {i+1}: RGB{color} | {hex_color}")
            label.pack(side=LEFT)
            
            self.color_list_canvas.append((canvas, label))
            
    def clear_color_list(self):
        for widget in self.color_list_frame.winfo_children():
            widget.destroy()
        self.color_list_canvas = []
        
    def toggle_arm(self):
        self.settings.armed = not self.settings.armed
        self.arm_button.config(text="Disarm" if self.settings.armed else "Arm Drawing",
                             fg="red" if self.settings.armed else "black")
        self.status_var.set("Drawing armed" if self.settings.armed else "Drawing disarmed")
        if not self.settings.armed and self.ghost_window:
            self.hide_ghost()
            
    def toggle_ghost(self):
        self.settings.use_ghost = self.ghost_var.get()
        if self.settings.use_ghost and self.settings.armed and self.pic.source.size != (0,0):
            self.show_ghost()
        elif self.ghost_window:
            self.hide_ghost()
            
    def show_ghost(self):
        if self.ghost_window:
            self.hide_ghost()
            
        self.ghost_window = Toplevel(self.root)
        self.ghost_window.attributes('-alpha', 0.3)
        self.ghost_window.attributes('-topmost', True)
        self.ghost_window.overrideredirect(True)
        
        # ใช้ขนาดจริงจาก settings.size และ pixel_size
        draw_width = self.settings.size[0] * self.settings.pixel_size
        draw_height = self.settings.size[1] * self.settings.pixel_size
        ghost_image = self.pic.source.resize(self.settings.size, Image.Resampling.LANCZOS)
        ghost_img = ImageTk.PhotoImage(ghost_image)
        label = Label(self.ghost_window, image=ghost_img)
        label.image = ghost_img
        label.pack()
        
        # ปรับขนาด Ghost ให้ตรงกับการวาดจริง
        x, y = pyautogui.position()
        self.ghost_window.geometry(f'{draw_width}x{draw_height}+{x}+{y}')
        
        label.bind('<Button-1>', lambda e: self.start_drag(e, self.ghost_window))
        label.bind('<B1-Motion>', lambda e: self.drag(e, self.ghost_window))
        label.bind('<ButtonRelease-1>', lambda e: self.stop_drag(e))
        
    def hide_ghost(self):
        if self.ghost_window:
            self.ghost_window.destroy()
            self.ghost_window = None
            
    def start_drag(self, event, window):
        window._drag_start_x = event.x
        window._drag_start_y = event.y
        
    def drag(self, event, window):
        deltax = event.x - window._drag_start_x
        deltay = event.y - window._drag_start_y
        x = window.winfo_x() + deltax
        y = window.winfo_y() + deltay
        window.geometry(f'+{x}+{y}')
        
    def stop_drag(self, event):
        if self.ghost_window:
            x, y = self.ghost_window.winfo_x(), self.ghost_window.winfo_y()
            self.settings.start_pos = (x, y)
            
    def update_settings(self):
        self.settings.pixel_size = self.pixel_size_var.get()
        speed_map = {"Fastest": 0, "Fast": 0.001, "Medium": 0.005, "Slow": 0.01}
        pyautogui.PAUSE = speed_map[self.speed_var.get()]
        if self.ghost_window:
            self.show_ghost()
        
    def prepare_shading(self):
        if self.pic.source.size == (0,0):
            messagebox.showwarning("Warning", "Please load an image first!")
            return
            
        n_layers = self.shading_layers_var.get()
        img_gray = self.pic.source.convert('L').filter(ImageFilter.GaussianBlur(radius=1))
        
        self.layers = []
        # ใช้ Multi-level Thresholding แทน KMeans
        hist, bins = np.histogram(asarray(img_gray), bins=256, range=(0, 256))
        thresholds = self.get_multi_thresholds(hist, n_layers)
        
        for i in range(n_layers):
            lower = 0 if i == 0 else thresholds[i-1]
            upper = 255 if i == n_layers-1 else thresholds[i]
            layer = img_gray.point(lambda p: 0 if lower <= p < upper else 255)
            self.layers.append(layer)
            
        self.current_layer_index = 0
        self.pic.current_layer = self.layers[0]
        self.update_preview()
        self.status_var.set(f"Prepared {n_layers} shading layers (Dark to Light)")
    
    def get_multi_thresholds(self, hist, n):
        # ใช้ Otsu’s method สำหรับ Multi-level Thresholding
        thresholds = []
        current_hist = hist.copy()
        for _ in range(n - 1):
            max_variance = -1
            threshold = 0
            for t in range(1, 256):
                w0 = np.sum(current_hist[:t]) / np.sum(current_hist)
                w1 = np.sum(current_hist[t:]) / np.sum(current_hist)
                if w0 == 0 or w1 == 0:
                    continue
                mean0 = np.sum(np.arange(t) * current_hist[:t]) / np.sum(current_hist[:t])
                mean1 = np.sum(np.arange(t, 256) * current_hist[t:]) / np.sum(current_hist[t:])
                variance = w0 * w1 * (mean0 - mean1) ** 2
                if variance > max_variance:
                    max_variance = variance
                    threshold = t
            thresholds.append(threshold)
            current_hist[threshold:] = 0
        thresholds.sort()
        return thresholds

    def prepare_colors(self):
        if self.pic.source.size == (0,0):
            messagebox.showwarning("Warning", "Please load an image first!")
            return
            
        n_colors = self.color_count_var.get()
        img_array = asarray(self.pic.source)
        
        # กรอง noise ด้วย Gaussian Blur
        img_pil = Image.fromarray(img_array).filter(ImageFilter.GaussianBlur(radius=1))
        img_gray = img_pil.convert('L')
        img_gray_array = asarray(img_gray)
        
        # ใช้ Thresholding แบบหลายระดับสำหรับภาพสี
        hist, bins = np.histogram(img_gray_array, bins=256, range=(0, 256))
        thresholds = self.get_multi_thresholds(hist, n_colors)
        
        self.layers = []
        for i in range(n_colors):
            lower = 0 if i == 0 else thresholds[i-1]
            upper = 255 if i == n_colors-1 else thresholds[i]
            # สร้าง mask จากความสว่าง
            mask = np.where((img_gray_array >= lower) & (img_gray_array < upper), 0, 255).astype('uint8')
            # คำนวณค่า RGB เฉลี่ยในแต่ละเลเยอร์
            region_mask = mask == 0
            if np.any(region_mask):
                color = tuple(np.mean(img_array[region_mask], axis=0).astype(int))
                # กรอง mask เพื่อลบจุดเดี่ยวๆ
                mask = self.clean_mask(mask)
                self.layers.append({
                    'mask': Image.fromarray(mask),
                    'color': color,
                    'brightness': sum(color)
                })
            else:
                self.status_var.set(f"No valid region for layer {i+1}")
                continue
        
        if not self.layers:
            messagebox.showwarning("Warning", "No valid color layers could be generated. Try adjusting Number of Colors.")
            return
            
        self.layers.sort(key=lambda x: x['brightness'])
        
        self.current_layer_index = 0
        self.pic.current_layer = self.layers[0]['mask']
        self.update_preview()
        self.status_var.set(f"Prepared {len(self.layers)} colors (Dark to Light)")

    def clean_mask(self, mask):
        # กรอง mask เพื่อลบจุดเดี่ยวๆ และรักษาพื้นที่ใหญ่
        cleaned = np.copy(mask)
        for y in range(cleaned.shape[0]):
            for x in range(cleaned.shape[1]):
                if cleaned[y, x] == 0:
                    # นับพิกเซลรอบๆ (8-connected) ถ้ามีน้อยกว่า 2 พิกเซล 0 รอบๆ ให้ลบ
                    neighbors = 0
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            ny, nx = y + dy, x + dx
                            if 0 <= ny < cleaned.shape[0] and 0 <= nx < cleaned.shape[1] and cleaned[ny, nx] == 0:
                                neighbors += 1
                    if neighbors < 2:  # ถ้ามีพิกเซล 0 รอบๆ น้อยกว่า 2 ให้เปลี่ยนเป็น 255
                        cleaned[y, x] = 255
        return cleaned

    def draw_layer(self, layer):
        if not self.settings.armed:
            messagebox.showwarning("Warning", "Please arm the drawer first!")
            return
            
        self.settings.interrupted = False
        self.settings.drawing = True
        
        # ใช้ขนาดจริงจาก settings.size และ pixel_size
        draw_width = self.settings.size[0] * self.settings.pixel_size
        draw_height = self.settings.size[1] * self.settings.pixel_size
        resized = layer.resize(self.settings.size, Image.Resampling.LANCZOS)
        data = asarray(resized)
        
        if self.settings.start_pos is None:
            if self.settings.use_ghost and self.ghost_window:
                x, y = self.ghost_window.winfo_x(), self.ghost_window.winfo_y()
                self.settings.start_pos = (x, y)
            else:
                x, y = pyautogui.position()
                self.settings.start_pos = (x, y)
        else:
            x, y = self.settings.start_pos
            
        pixel_size = self.settings.pixel_size
        
        self.status_var.set(f"Drawing layer {self.current_layer_index + 1}/{len(self.layers)} at {draw_width}x{draw_height}")
        
        for row_idx, row in enumerate(data):
            if self.settings.interrupted:
                break
                
            pyautogui.moveTo(x, y + (row_idx * pixel_size))
            current_pos = x
            for col_idx, value in enumerate(row):
                if self.settings.interrupted:
                    break
                if value == 0:
                    if current_pos != x + (col_idx * pixel_size):
                        pyautogui.moveTo(x + (col_idx * pixel_size), y + (row_idx * pixel_size))
                    pyautogui.drag(pixel_size, 0, duration=0.001)
                    current_pos = x + ((col_idx + 1) * pixel_size)
        
        self.settings.drawing = False
        self.status_var.set("Drawing completed" if not self.settings.interrupted else "Drawing interrupted")
        
    def draw_next_layer(self):
        if not self.settings.armed:
            messagebox.showwarning("Warning", "Please arm the drawer first!")
            return
            
        if not self.layers:
            if self.get_current_mode() == "Shading":
                self.prepare_shading()
            elif self.get_current_mode() == "Color":
                self.prepare_colors()
            else:
                messagebox.showwarning("Warning", "Please prepare layers first!")
                return
                
        if self.current_layer_index < len(self.layers):
            threading.Thread(target=self._draw_next_layer_thread, daemon=True).start()
            
    def _draw_next_layer_thread(self):
        layer = self.layers[self.current_layer_index]
        if isinstance(layer, dict):
            self.draw_layer(layer['mask'])
        else:
            self.draw_layer(layer)
            
        if not self.settings.interrupted:
            self.current_layer_index += 1
            if self.current_layer_index < len(self.layers):
                self.pic.current_layer = (self.layers[self.current_layer_index]['mask'] 
                    if isinstance(self.layers[self.current_layer_index], dict)
                    else self.layers[self.current_layer_index])
                self.update_preview()
            else:
                self.status_var.set("All layers completed")
        
    def draw_current(self, mode):
        if not self.settings.armed:
            messagebox.showwarning("Warning", "Please arm the drawer first!")
            return
            
        if self.settings.use_ghost and not self.ghost_window:
            self.show_ghost()
            messagebox.showinfo("Position Ghost", "Move the ghost image to desired position and press Enter")
            return
            
        self.update_settings()
        if self.settings.use_ghost and self.ghost_window:
            self.hide_ghost()
            
        if mode == "Binary":
            threading.Thread(target=self._draw_binary_thread, daemon=True).start()
        else:
            self.draw_next_layer()
            
    def _draw_binary_thread(self):
        img_gray = self.pic.source.convert('L')
        threshold = self.threshold_var.get()
        binary = img_gray.point(lambda p: 0 if p > threshold else 255)
        self.draw_layer(binary)
        
    def interrupt(self):
        self.settings.interrupted = True
        
    def invert_image(self):
        if self.pic.source.size == (0,0):
            messagebox.showwarning("Warning", "Please load an image first!")
            return
            
        self.pic.source = ImageOps.invert(self.pic.source)
        self.update_preview()
        self.status_var.set("Image inverted")
        
    def get_current_mode(self):
        current_tab = self.notebook.select()
        if current_tab == str(self.binary_frame):
            return "Binary"
        elif current_tab == str(self.shading_frame):
            return "Shading"
        return "Color"
        
    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    app = AutoDrawer()
    app.run()