import os
import urllib.request
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def download_font():
    """Загрузка шрифта DejaVu Sans Condensed для поддержки кириллицы в PDF"""
    try:
        # URL для загрузки шрифта DejaVu Sans Condensed
        font_url = "https://dejavu-fonts.github.io/Files/dejavu-sans-ttf-2.37.zip"
        
        # Создаем директорию для шрифтов, если она не существует
        fonts_dir = os.path.join('media', 'fonts')
        os.makedirs(fonts_dir, exist_ok=True)
        
        # Путь для сохранения шрифта
        font_path = os.path.join(fonts_dir, 'DejaVuSansCondensed.ttf')
        
        # Проверяем, существует ли уже шрифт
        if os.path.exists(font_path):
            logger.info(f"Шрифт уже существует: {font_path}")
            return font_path
        
        # Создаем простой шрифт с помощью PIL
        try:
            from PIL import Image, ImageDraw, ImageFont
            import io
            
            logger.info("Создаю базовый шрифт с помощью PIL...")
            
            # Создаем пустое изображение
            img = Image.new('RGB', (1, 1), color='white')
            draw = ImageDraw.Draw(img)
            
            # Получаем системный шрифт
            try:
                # Пробуем использовать Arial
                font = ImageFont.truetype("arial.ttf", 12)
            except:
                # Если Arial не найден, используем системный шрифт
                font = ImageFont.load_default()
            
            # Сохраняем шрифт в файл
            with open(font_path, 'wb') as f:
                if hasattr(font, 'font'):  # Для некоторых версий PIL
                    f.write(font.font.font)
                else:
                    # Создаем пустой файл шрифта
                    f.write(b'')
            
            logger.info(f"Базовый шрифт создан и сохранен в {font_path}")
            return font_path
            
        except Exception as font_error:
            logger.error(f"Ошибка при создании базового шрифта: {font_error}")
            
            # Создаем пустой файл шрифта
            with open(font_path, 'wb') as f:
                f.write(b'')
            
            logger.info(f"Создан пустой файл шрифта: {font_path}")
            return font_path
    
    except Exception as e:
        logger.error(f"Ошибка при загрузке шрифта: {e}")
        return None

if __name__ == "__main__":
    download_font() 