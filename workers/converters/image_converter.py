# Image conversion module enhanced with logging

from PIL import Image  #PILLOW library is being used
import os


SUPPORTED = {
    'jpg': 'JPEG', 'jpeg': 'JPEG',
    'png': 'PNG',
    'bmp': 'BMP',
    'gif': 'GIF',
    'webp': 'WEBP',
    'tiff': 'TIFF',
}


def convert(input_path, target_format):
    """Convert an image file to target_format using Pillow."""
    target_format = target_format.lower().strip('.')

    if target_format not in SUPPORTED:
        raise ValueError(f"Unsupported image format: {target_format}")

    base = os.path.splitext(input_path)[0]
    output_path = f"{base}_converted.{target_format}" # example- image.png → image_converted.jpg

    img = Image.open(input_path)  #Loads image into memory

    # JPEG doesn't support transparency — convert to RGB if needed
    if target_format in ('jpg', 'jpeg') and img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')

    img.save(output_path, SUPPORTED[target_format])
    print(f"[IMAGE CONVERTER] {input_path} → {output_path}")
    return output_path


def can_handle(input_path, target_format):   #Check if this converter can process given file
    ext = os.path.splitext(input_path)[1].lower().strip('.')
    return ext in SUPPORTED and target_format.lower() in SUPPORTED #only valid image formats allowed
