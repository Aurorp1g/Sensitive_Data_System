import os

# 基础路径，指向根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# tshark工具路径
TSHARK_PATH = os.path.join(BASE_DIR, 'tshark', 'tshark.exe')

# 临时缓存目录
Temp_path = os.path.join(BASE_DIR, 'Temp')

# 临时结果缓存目录
Temp_result_1 = os.path.join(Temp_path, "Temp_result_1.csv")
Temp_result_2 = os.path.join(Temp_path, "Temp_result_2.csv")

# 临时图片缓存目录
Temp_img = os.path.join(Temp_path, "Temp_img")

# OCR模型路径
OCR_model = os.path.join(BASE_DIR,'image_ocr' ,'OCR_model')

# 最终结果目录
Final_result = os.path.join(BASE_DIR, 'Final_result', "Result.csv")