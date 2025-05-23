import base64
# Convert DejaVuSans.ttf file to base64 format
with open("DejaVuSans.ttf", "rb") as font_file:
    encoded_font = base64.b64encode(font_file.read()).decode("utf-8")
# Create embedded_font.py file
with open("embedded_font.py", "w") as output_file:
    output_file.write(f"embedded_font = '''{encoded_font}'''")