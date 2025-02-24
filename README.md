```markdown:README.md
# CarrotDrawy

[English](#english) | [ภาษาไทย](#thai)

## <a name="english"></a>English

### Description
CarrotDrawy is an automated drawing tool that converts images into drawings using your mouse cursor. It supports multiple drawing modes and can simulate hand-drawn artwork from digital images.

### Features
- **Multiple Drawing Modes**:
  - Binary Mode: Converts image to black and white
  - Shading Mode: Creates multiple layers of shading
  - Color Mode: Draws with multiple colors
- **Ghost Image Preview**: Helps position your drawing accurately
- **Adjustable Settings**:
  - Drawing speed control
  - Pixel size adjustment
  - Image size scaling
  - Threshold controls for binary mode
  - Number of layers for shading/color modes

### Installation

1. Clone the repository:
```bash
git clone https://github.com/panwan1040/carrotdrawy.git
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

### Usage

1. Launch the application:
```bash
python carrotdrawy.py
```

2. Basic Steps:
   - Load an image using "Load Image" button
   - Select drawing mode (Binary/Shading/Color)
   - Adjust settings as needed
   - Click "Arm Drawing" to enable drawing
   - Use ghost image to position (optional)
   - Press Enter or click "Draw Now" to start

3. Controls:
   - ESC: Stop drawing
   - Enter: Start drawing
   - Left mouse: Position ghost image

### Requirements
- Python 3.10 or higher
- See requirements.txt for complete list of dependencies

---

## <a name="thai"></a>ภาษาไทย

### คำอธิบาย
CarrotDrawy เป็นเครื่องมือวาดภาพอัตโนมัติที่แปลงรูปภาพให้เป็นภาพวาดโดยใช้เคอร์เซอร์เมาส์ รองรับโหมดการวาดหลายรูปแบบและสามารถจำลองการวาดภาพด้วยมือจากภาพดิจิทัล

### คุณสมบัติ
- **โหมดการวาดหลายรูปแบบ**:
  - โหมดขาว-ดำ: แปลงภาพเป็นขาวดำ
  - โหมดแรเงา: สร้างเลเยอร์แรเงาหลายระดับ
  - โหมดสี: วาดด้วยสีหลายสี
- **ภาพพรีวิวแบบโปร่งใส**: ช่วยในการจัดตำแหน่งภาพวาด
- **การตั้งค่าที่ปรับแต่งได้**:
  - ควบคุมความเร็วในการวาด
  - ปรับขนาดพิกเซล
  - ปรับขนาดภาพ
  - ควบคุมค่าเทรชโฮลด์สำหรับโหมดขาว-ดำ
  - กำหนดจำนวนเลเยอร์สำหรับโหมดแรเงา/สี

### การติดตั้ง

1. โคลนโปรเจค:
```bash
git clone https://github.com/panwan1040/carrotdrawy.git
```

2. ติดตั้งแพ็คเกจที่จำเป็น:
```bash
pip install -r requirements.txt
```

### วิธีใช้งาน

1. เปิดโปรแกรม:
```bash
python carrotdrawy.py
```

2. ขั้นตอนพื้นฐาน:
   - โหลดรูปภาพด้วยปุ่ม "Load Image"
   - เลือกโหมดการวาด (Binary/Shading/Color)
   - ปรับการตั้งค่าตามต้องการ
   - กดปุ่ม "Arm Drawing" เพื่อเปิดใช้งานการวาด
   - ใช้ภาพพรีวิวแบบโปร่งใสในการจัดตำแหน่ง (ตัวเลือก)
   - กด Enter หรือคลิก "Draw Now" เพื่อเริ่มวาด

3. การควบคุม:
   - ESC: หยุดการวาด
   - Enter: เริ่มการวาด
   - เมาส์ซ้าย: จัดตำแหน่งภาพพรีวิวแบบโปร่งใส

### ความต้องการของระบบ
- Python 3.10 หรือสูงกว่า
- ดูรายการแพ็คเกจที่จำเป็นทั้งหมดได้ใน requirements.txt

### หมายเหตุ
- ควรใช้งานในพื้นที่วาดที่มีพื้นหลังสีขาว
- แนะนำให้ทดลองปรับการตั้งค่าต่างๆ ก่อนเริ่มวาดภาพจริง
- สามารถกด ESC เพื่อหยุดการวาดได้ตลอดเวลา
```
