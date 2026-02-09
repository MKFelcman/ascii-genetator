from flask import Flask, render_template, request
from PIL import Image
import io

app = Flask(__name__)

# --- Vylepšená sada znaků (70 úrovní jasu) ---
ASCII_CHARS = ["$", "@", "B", "%", "8", "&", "W", "M", "#", "*", "o", "a", "h", "k", "b", "d", "p", "q", "w", "m", "Z", "O", "0", "Q", "L", "C", "J", "U", "Y", "X", "z", "c", "v", "u", "n", "x", "r", "j", "f", "t", "/", "\\", "|", "(", ")", "1", "{", "}", "[", "]", "?", "-", "_", "+", "~", "<", ">", "i", "!", "l", "I", ";", ":", ",", "\"", "^", "`", ".", " "]

def resize_image(image, new_width=100):
    width, height = image.size
    ratio = height / width
    # Korekce poměru stran (znaky jsou vysoké)
    new_height = int(new_width * ratio * 0.55)
    resized_image = image.resize((new_width, new_height))
    return resized_image

def grayify(image):
    return image.convert("L")

def pixels_to_ascii(image):
    pixels = image.getdata()
    # Mapování pixelů na znaky
    # 255 (bílá) / délka seznamu znaků = krok
    interval = 256 / len(ASCII_CHARS)
    characters = "".join([ASCII_CHARS[int(pixel // interval)] for pixel in pixels])
    return characters

def convert_image_to_ascii(image, new_width=100):
    new_image_data = pixels_to_ascii(grayify(resize_image(image, new_width)))
    
    pixel_count = len(new_image_data)
    ascii_image = "\n".join([new_image_data[index:(index+new_width)] for index in range(0, pixel_count, new_width)])
    return ascii_image

@app.route("/", methods=["GET", "POST"])
def index():
    ascii_art = None
    width = 150 # Výchozí šířka
    
    if request.method == "POST":
        if 'file' not in request.files:
            return render_template('index.html', error="Žádný soubor.")
        
        file = request.files['file']
        
        # Získání šířky z formuláře (pokud uživatel vybral)
        width_str = request.form.get('width')
        if width_str:
            width = int(width_str)

        if file.filename == '':
            return render_template('index.html', error="Nevybral jsi soubor.")

        try:
            image = Image.open(io.BytesIO(file.read()))
            ascii_art = convert_image_to_ascii(image, new_width=width)
        except Exception as e:
             return render_template('index.html', error=f"Chyba: {e}")

    return render_template("index.html", ascii_art=ascii_art, current_width=width)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)