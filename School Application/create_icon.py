from PIL import Image, ImageDraw

# Create a new image with a transparent background
size = (256, 256)
image = Image.new('RGBA', size, (0, 0, 0, 0))
draw = ImageDraw.Draw(image)

# Draw a rounded rectangle for the background
background_color = (52, 53, 65, 255)  # Dark theme color
draw.rounded_rectangle([20, 20, 236, 236], radius=30, fill=background_color)

# Draw some simple shapes to represent the application
accent_color = (86, 182, 194, 255)  # Accent color

# Draw a clock shape for timer
draw.ellipse([50, 50, 130, 130], outline=accent_color, width=8)
draw.line([90, 90, 90, 60], fill=accent_color, width=8)  # Hour hand
draw.line([90, 90, 110, 90], fill=accent_color, width=8)  # Minute hand

# Draw a list shape for name picker
draw.rectangle([150, 50, 206, 130], outline=accent_color, width=8)
draw.line([160, 70, 196, 70], fill=accent_color, width=4)
draw.line([160, 90, 196, 90], fill=accent_color, width=4)
draw.line([160, 110, 196, 110], fill=accent_color, width=4)

# Draw a trophy shape for tournament
draw.line([90, 150, 166, 150], fill=accent_color, width=8)  # Base
draw.line([128, 150, 128, 200], fill=accent_color, width=8)  # Stem
draw.arc([108, 180, 148, 220], 0, 180, fill=accent_color, width=8)  # Cup bottom
draw.line([108, 180, 148, 180], fill=accent_color, width=8)  # Cup top

# Save the image as ICO
image.save('icon.ico', format='ICO', sizes=[(256, 256)]) 