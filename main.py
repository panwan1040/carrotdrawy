import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import numpy as np
import math

class DitheringApp:
    def __init__(self, root):
        self.root = root
        self.root.title("แปลงภาพเป็นขาวดำด้วย Dithering แบบปรับความหนาแน่นได้")
        self.root.geometry("900x700")

        # สร้าง GUI elements
        self.create_widgets()
        
        # ตัวแปรสำหรับเก็บภาพ
        self.original_image = None
        self.dithered_image = None

    def create_widgets(self):
        # สร้างเฟรมหลัก
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # เฟรมสำหรับปุ่มและการตั้งค่า
        control_frame = ttk.LabelFrame(main_frame, text="การควบคุม", padding="10")
        control_frame.pack(fill=tk.X, pady=10)

        # ปุ่มควบคุม
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="เลือกภาพ", command=self.load_image).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(button_frame, text="แปลงเป็นขาวดำ", command=self.apply_dithering).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(button_frame, text="บันทึกภาพ", command=self.save_image).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(button_frame, text="รีเซ็ตค่า", command=self.reset_settings).grid(row=0, column=3, padx=5, pady=5)

        # การตั้งค่า - ใช้สองคอลัมน์เพื่อจัดระเบียบให้ดีขึ้น
        settings_frame = ttk.Frame(control_frame)
        settings_frame.pack(fill=tk.X, pady=10)

        # คอลัมน์ซ้าย
        left_settings = ttk.Frame(settings_frame)
        left_settings.grid(row=0, column=0, padx=10)

        # คอลัมน์ขวา
        right_settings = ttk.Frame(settings_frame)
        right_settings.grid(row=0, column=1, padx=10)

        # การตั้งค่าระดับความละเอียด
        ttk.Label(left_settings, text="ระดับความละเอียด (2-16):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.quant_levels = tk.IntVar(value=2)
        ttk.Scale(left_settings, from_=2, to=16, orient=tk.HORIZONTAL, variable=self.quant_levels, length=200).grid(row=0, column=1, padx=5, pady=2)
        
        # การตั้งค่าขนาดพิกเซล - ใช้ช่วงที่กว้างขึ้น
        ttk.Label(left_settings, text="ขนาดพิกเซล (1-30):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.pixel_size = tk.IntVar(value=1)
        ttk.Scale(left_settings, from_=1, to=30, orient=tk.HORIZONTAL, variable=self.pixel_size, length=200).grid(row=1, column=1, padx=5, pady=2)
        
        # การตั้งค่าความคมชัด
        ttk.Label(left_settings, text="ความคมชัด (1-20):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.contrast = tk.IntVar(value=1)
        ttk.Scale(left_settings, from_=1, to=20, orient=tk.HORIZONTAL, variable=self.contrast, length=200).grid(row=2, column=1, padx=5, pady=2)
        
        # การตั้งค่าความเข้มของการกระจาย
        ttk.Label(right_settings, text="ความเข้มการกระจาย (1-10):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.diffusion_intensity = tk.IntVar(value=10)
        ttk.Scale(right_settings, from_=1, to=10, orient=tk.HORIZONTAL, variable=self.diffusion_intensity, length=200).grid(row=0, column=1, padx=5, pady=2)
        
        # เลือกรูปแบบการ dithering
        ttk.Label(right_settings, text="รูปแบบ Dithering:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.dither_pattern = tk.StringVar(value="Floyd-Steinberg")
        patterns = ["Floyd-Steinberg", "Jarvis-Judice-Ninke", "Stucki", "Atkinson", "Sierra", "ความหนาแน่นต่ำ", "ความหนาแน่นสูง"]
        pattern_dropdown = ttk.Combobox(right_settings, textvariable=self.dither_pattern, values=patterns, state="readonly", width=20)
        pattern_dropdown.grid(row=1, column=1, padx=5, pady=2)
        
        # ตัวเลือกพิเศษ - การเน้นขอบ
        self.edge_mode = tk.BooleanVar(value=False)
        ttk.Checkbutton(right_settings, text="เน้นขอบ", variable=self.edge_mode).grid(row=2, column=0, sticky=tk.W, pady=2)
        
        # ตัวเลือกขยายพิกเซล
        self.pixel_expansion = tk.BooleanVar(value=False)
        ttk.Checkbutton(right_settings, text="ขยายพิกเซล", variable=self.pixel_expansion).grid(row=2, column=1, sticky=tk.W, pady=2)

        # เฟรมข้อมูลเพิ่มเติม
        info_frame = ttk.Frame(control_frame)
        info_frame.pack(fill=tk.X, pady=5)

        # คำอธิบายการตั้งค่า
        info_text = (
            "ระดับความละเอียด: จำนวนสีในภาพ (2=ขาว/ดำ, 16=หลายระดับสีเทา)\n"
            "ขนาดพิกเซล: ค่ามาก = จุดห่าง, พิกเซลใหญ่ | ค่าน้อย = จุดถี่, พิกเซลเล็ก\n"
            "ความคมชัด: ค่ามาก = เพิ่มความแตกต่างระหว่างพื้นที่สว่างและมืด\n"
            "ความเข้มการกระจาย: ค่ามาก = กระจายสม่ำเสมอ | ค่าน้อย = กระจายน้อย เกิดจุดเดี่ยว"
        )
        ttk.Label(info_frame, text=info_text, justify="left").pack(anchor="w")

        # สถานะการทำงาน
        self.status_var = tk.StringVar(value="พร้อมทำงาน")
        ttk.Label(main_frame, textvariable=self.status_var).pack(anchor="w", pady=5)

        # เฟรมสำหรับแสดงภาพ
        self.image_frame = ttk.Frame(main_frame)
        self.image_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # เฟรมสำหรับภาพต้นฉบับ
        original_frame = ttk.LabelFrame(self.image_frame, text="ภาพต้นฉบับ")
        original_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.original_image_label = ttk.Label(original_frame)
        self.original_image_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # เฟรมสำหรับภาพที่แปลงแล้ว
        dithered_frame = ttk.LabelFrame(self.image_frame, text="ภาพขาวดำ")
        dithered_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.dithered_image_label = ttk.Label(dithered_frame)
        self.dithered_image_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def reset_settings(self):
        """รีเซ็ตการตั้งค่าทั้งหมดให้เป็นค่าเริ่มต้น"""
        self.quant_levels.set(2)
        self.pixel_size.set(1)
        self.contrast.set(1)
        self.diffusion_intensity.set(10)
        self.dither_pattern.set("Floyd-Steinberg")
        self.edge_mode.set(False)
        self.pixel_expansion.set(False)

    def load_image(self):
        """โหลดภาพจากไฟล์"""
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")])
        if file_path:
            try:
                self.status_var.set(f"กำลังโหลดภาพ: {file_path}")
                self.root.update()
                
                self.original_image = Image.open(file_path).convert('RGB')
                # ปรับขนาดภาพเพื่อแสดงใน GUI
                display_size = (400, 400)
                display_image = self.original_image.copy()
                display_image.thumbnail(display_size, Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(display_image)
                self.original_image_label.configure(image=photo)
                self.original_image_label.image = photo
                self.dithered_image_label.configure(image='')
                
                self.status_var.set(f"โหลดภาพแล้ว: {file_path}")
            except Exception as e:
                messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถโหลดภาพได้: {str(e)}")
                self.status_var.set("เกิดข้อผิดพลาด")

    def apply_dithering(self):
        """ประมวลผลภาพด้วยการสร้าง dithering"""
        if self.original_image is None:
            messagebox.showwarning("คำเตือน", "กรุณาเลือกภาพก่อน")
            return

        self.status_var.set("กำลังประมวลผลภาพ...")
        self.root.update()
        
        try:
            # คำนวณขนาดพิกเซลแบบเอ็กซ์โพเนนเชียลเพื่อให้ปรับได้ละเอียดขึ้น
            pixel_scale_raw = self.pixel_size.get()
            pixel_scale = int(1.2 ** (pixel_scale_raw - 1))  # การคำนวณแบบเอ็กซ์โพเนนเชียล
            
            # ลดขนาดภาพตามขนาดพิกเซล
            original_size = self.original_image.size
            scaled_size = (max(1, original_size[0] // pixel_scale), max(1, original_size[1] // pixel_scale))
            if scaled_size[0] < 3 or scaled_size[1] < 3:
                messagebox.showwarning("คำเตือน", "ขนาดพิกเซลใหญ่เกินไปสำหรับภาพนี้")
                self.status_var.set("ขนาดพิกเซลใหญ่เกินไป")
                return
            
            # แปลงภาพเป็นภาพระดับสีเทา
            img = self.original_image.resize(scaled_size, Image.Resampling.LANCZOS).convert('L')
            width, height = img.size
            pixels = np.array(img, dtype=np.float32)
            
            # ปรับความคมชัด
            contrast_value = self.contrast.get()
            if contrast_value > 1:
                # ปรับความคมชัดก่อนการ dithering
                mid = 128
                for y in range(height):
                    for x in range(width):
                        # ปรับค่าให้ห่างจากกลาง (128) มากขึ้น
                        pixel_value = pixels[y, x]
                        if pixel_value > mid:
                            pixels[y, x] = mid + (pixel_value - mid) * contrast_value
                        else:
                            pixels[y, x] = mid - (mid - pixel_value) * contrast_value
                        # ป้องกันค่าเกินขอบเขต
                        pixels[y, x] = min(255, max(0, pixels[y, x]))
            
            # ประมวลผลภาพตามรูปแบบขอบ (ถ้าเลือก)
            edges = None
            if self.edge_mode.get():
                # คำนวณค่าขอบด้วยวิธี Sobel
                dx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], np.float32)
                dy = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], np.float32)
                
                # คำนวณ gradient
                from scipy import ndimage
                gx = ndimage.convolve(pixels, dx)
                gy = ndimage.convolve(pixels, dy)
                edges = np.sqrt(gx*gx + gy*gy)
                # ปรับให้อยู่ในช่วง 0-1
                edges = np.clip(edges / edges.max(), 0, 1)
            
            # จำนวนระดับความละเอียด
            levels = self.quant_levels.get()
            step = 255 / (levels - 1)
            
            # ค่าความเข้มของการกระจาย
            diffusion_scale = self.diffusion_intensity.get() / 10.0
            
            # Floyd-Steinberg dithering หรือรูปแบบที่เลือก
            for y in range(height):
                for x in range(width):
                    old_pixel = pixels[y, x]
                    # หาระดับที่ใกล้ที่สุด
                    new_pixel = round(old_pixel / step) * step
                    new_pixel = min(255, max(0, new_pixel))  # จำกัดค่าให้อยู่ในช่วง 0-255
                    pixels[y, x] = new_pixel
                    error = old_pixel - new_pixel
                    
                    # ปรับความเข้มของขอบ (ถ้าเลือก)
                    local_diffusion_scale = diffusion_scale
                    if self.edge_mode.get() and edges is not None:
                        # ลดการกระจายที่ขอบเพื่อให้ขอบคมชัดขึ้น
                        edge_intensity = edges[y, x]
                        local_diffusion_scale *= (1.0 - edge_intensity * 0.7)
                    
                    # กระจาย error ไปยังพิกเซลข้างเคียงตามรูปแบบที่เลือก
                    self.apply_dithering_pattern(pixels, x, y, width, height, error, local_diffusion_scale)
            
            # แปลงกลับเป็นภาพ
            dithered_scaled = Image.fromarray(pixels.astype(np.uint8))
            
            # ขยายพิกเซลแบบชัดเจน (ถ้าเลือก)
            if self.pixel_expansion.get():
                # ใช้ Nearest neighbor เพื่อให้เห็นพิกเซลชัดเจน
                resize_method = Image.Resampling.NEAREST
            else:
                # ใช้ Lanczos เพื่อให้ภาพดูนุ่มนวลขึ้น
                resize_method = Image.Resampling.LANCZOS
            
            # แปลงกลับเป็นภาพและขยายกลับไปขนาดเดิม
            self.dithered_image = dithered_scaled.resize(original_size, resize_method)
            
            # แสดงภาพที่แปลงแล้ว
            display_size = (400, 400)
            display_image = self.dithered_image.copy()
            display_image.thumbnail(display_size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(display_image)
            self.dithered_image_label.configure(image=photo)
            self.dithered_image_label.image = photo
            
            self.status_var.set("แปลงภาพสำเร็จ")
        
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"เกิดข้อผิดพลาดระหว่างการแปลงภาพ: {str(e)}")
            import traceback
            traceback.print_exc()
            self.status_var.set("เกิดข้อผิดพลาด")

    def apply_dithering_pattern(self, pixels, x, y, width, height, error, scale=1.0):
        """กระจายค่าความผิดพลาดตามรูปแบบที่เลือก"""
        pattern = self.dither_pattern.get()
        
        if pattern == "Floyd-Steinberg":
            # รูปแบบพื้นฐาน
            if x < width - 1:
                pixels[y, x + 1] += error * 7 / 16 * scale
            if y < height - 1:
                if x > 0:
                    pixels[y + 1, x - 1] += error * 3 / 16 * scale
                pixels[y + 1, x] += error * 5 / 16 * scale
                if x < width - 1:
                    pixels[y + 1, x + 1] += error * 1 / 16 * scale
        
        elif pattern == "Jarvis-Judice-Ninke":
            # รูปแบบที่กระจายกว้างกว่า (5x3 พิกเซล)
            divisor = 48
            if x < width - 1:
                pixels[y, x + 1] += error * 7 / divisor * scale
            if x < width - 2:
                pixels[y, x + 2] += error * 5 / divisor * scale
                
            if y < height - 1:
                if x > 1:
                    pixels[y + 1, x - 2] += error * 3 / divisor * scale
                if x > 0:
                    pixels[y + 1, x - 1] += error * 5 / divisor * scale
                pixels[y + 1, x] += error * 7 / divisor * scale
                if x < width - 1:
                    pixels[y + 1, x + 1] += error * 5 / divisor * scale
                if x < width - 2:
                    pixels[y + 1, x + 2] += error * 3 / divisor * scale
                
            if y < height - 2:
                if x > 1:
                    pixels[y + 2, x - 2] += error * 1 / divisor * scale
                if x > 0:
                    pixels[y + 2, x - 1] += error * 3 / divisor * scale
                pixels[y + 2, x] += error * 5 / divisor * scale
                if x < width - 1:
                    pixels[y + 2, x + 1] += error * 3 / divisor * scale
                if x < width - 2:
                    pixels[y + 2, x + 2] += error * 1 / divisor * scale
        
        elif pattern == "Stucki":
            # รูปแบบคล้าย Jarvis แต่สัมประสิทธิ์ต่างกัน
            divisor = 42
            if x < width - 1:
                pixels[y, x + 1] += error * 8 / divisor * scale
            if x < width - 2:
                pixels[y, x + 2] += error * 4 / divisor * scale
                
            if y < height - 1:
                if x > 1:
                    pixels[y + 1, x - 2] += error * 2 / divisor * scale
                if x > 0:
                    pixels[y + 1, x - 1] += error * 4 / divisor * scale
                pixels[y + 1, x] += error * 8 / divisor * scale
                if x < width - 1:
                    pixels[y + 1, x + 1] += error * 4 / divisor * scale
                if x < width - 2:
                    pixels[y + 1, x + 2] += error * 2 / divisor * scale
                
            if y < height - 2:
                if x > 1:
                    pixels[y + 2, x - 2] += error * 1 / divisor * scale
                if x > 0:
                    pixels[y + 2, x - 1] += error * 2 / divisor * scale
                pixels[y + 2, x] += error * 4 / divisor * scale
                if x < width - 1:
                    pixels[y + 2, x + 1] += error * 2 / divisor * scale
                if x < width - 2:
                    pixels[y + 2, x + 2] += error * 1 / divisor * scale
        
        elif pattern == "Atkinson":
            # รูปแบบที่กระจายน้อยกว่า เหมาะกับภาพที่ต้องการความคมชัดสูง
            divisor = 8  # รวมสัมประสิทธิ์ = 6/8 (ไม่เต็ม 1)
            if x < width - 1:
                pixels[y, x + 1] += error * 1 / divisor * scale
            if x < width - 2:
                pixels[y, x + 2] += error * 1 / divisor * scale
                
            if y < height - 1:
                if x > 0:
                    pixels[y + 1, x - 1] += error * 1 / divisor * scale
                pixels[y + 1, x] += error * 1 / divisor * scale
                if x < width - 1:
                    pixels[y + 1, x + 1] += error * 1 / divisor * scale
                
            if y < height - 2:
                pixels[y + 2, x] += error * 1 / divisor * scale
        
        elif pattern == "Sierra":
            # รูปแบบ Sierra (2-row)
            divisor = 16
            if x < width - 1:
                pixels[y, x + 1] += error * 4 / divisor * scale
            if x < width - 2:
                pixels[y, x + 2] += error * 3 / divisor * scale
                
            if y < height - 1:
                if x > 1:
                    pixels[y + 1, x - 2] += error * 1 / divisor * scale
                if x > 0:
                    pixels[y + 1, x - 1] += error * 2 / divisor * scale
                pixels[y + 1, x] += error * 3 / divisor * scale
                if x < width - 1:
                    pixels[y + 1, x + 1] += error * 2 / divisor * scale
                if x < width - 2:
                    pixels[y + 1, x + 2] += error * 1 / divisor * scale
        
        elif pattern == "ความหนาแน่นต่ำ":
            # รูปแบบกระจายน้อย เกิดจุดเดี่ยวมากกว่า
            if x < width - 1:
                pixels[y, x + 1] += error * 5 / 16 * scale
            if y < height - 1:
                if x < width - 1:
                    pixels[y + 1, x + 1] += error * 1 / 16 * scale
        
        elif pattern == "ความหนาแน่นสูง":
            # รูปแบบกระจายมาก กว้าง ทำให้เกิดรูปแบบที่ซับซ้อน
            divisor = 200  # ใช้ค่าที่มากเพื่อให้กระจายน้อยลงต่อจุด แต่กระจายไปหลายจุด
            
            # แถวปัจจุบัน
            if x < width - 1:
                pixels[y, x + 1] += error * 30 / divisor * scale
            if x < width - 2:
                pixels[y, x + 2] += error * 20 / divisor * scale
            if x < width - 3:
                pixels[y, x + 3] += error * 10 / divisor * scale
                
            # แถวถัดไป
            if y < height - 1:
                for dx in range(-3, 4):
                    if 0 <= x + dx < width:
                        weight = 20 - abs(dx) * 5  # น้ำหนักลดลงตามระยะห่าง
                        pixels[y + 1, x + dx] += error * max(0, weight) / divisor * scale
                        
            # แถวที่ 2
            if y < height - 2:
                for dx in range(-2, 3):
                    if 0 <= x + dx < width:
                        weight = 15 - abs(dx) * 5
                        pixels[y + 2, x + dx] += error * max(0, weight) / divisor * scale
                        
            # แถวที่ 3
            if y < height - 3:
                for dx in range(-1, 2):
                    if 0 <= x + dx < width:
                        weight = 10 - abs(dx) * 5
                        pixels[y + 3, x + dx] += error * max(0, weight) / divisor * scale

    def save_image(self):
        """บันทึกภาพที่แปลงแล้ว"""
        if self.dithered_image is None:
            messagebox.showwarning("คำเตือน", "กรุณาแปลงภาพก่อน")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("BMP files", "*.bmp")]
        )
        
        if file_path:
            try:
                self.status_var.set(f"กำลังบันทึกภาพไปที่ {file_path}")
                self.root.update()
                
                self.dithered_image.save(file_path)
                messagebox.showinfo("สำเร็จ", "บันทึกภาพเรียบร้อยแล้ว")
                self.status_var.set(f"บันทึกภาพแล้ว: {file_path}")
            except Exception as e:
                messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถบันทึกภาพได้: {str(e)}")
                self.status_var.set("เกิดข้อผิดพลาดในการบันทึกภาพ")

if __name__ == "__main__":
    root = tk.Tk()
    app = DitheringApp(root)
    root.mainloop()