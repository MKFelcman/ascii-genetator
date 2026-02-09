from flask import Flask, render_template, request
from PIL import Image
import io

app = Flask(__name__)

# --- Nastavení ASCII ---
# Znaky od nejtmavšího po nejsvětlejší
ASCII_CHARS = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]

def resize_image(image, new_width=100):
    """Zmenší obrázek při zachování poměru stran."""
    width, height = image.size
    ratio = height / width
    # ASCII znaky jsou vyšší než širší, kompenzujeme to (ratio * 0.55)
    new_height = int(new_width * ratio * 0.55)
    resized_image = image.resize((new_width, new_height))
    return resized_image

def grayify(image):
    """Převede obrázek do odstínů šedi."""
    return image.convert("L")

def pixels_to_ascii(image):
    """Převede pixely na ASCII znaky podle jasu."""
    pixels = image.getdata()
    characters = "".join([ASCII_CHARS[pixel // 25] for pixel in pixels])
    return characters

def convert_image_to_ascii(image, new_width=100):
    """Hlavní funkce spojující kroky."""
    new_image_data = pixels_to_ascii(grayify(resize_image(image, new_width)))
    
    pixel_count = len(new_image_data)
    ascii_image = "\n".join([new_image_data[index:(index+new_width)] for index in range(0, pixel_count, new_width)])
    return ascii_image

# --- Webové cesty (Routes) ---

@app.route("/", methods=["GET", "POST"])
def index():
    ascii_art = None
    if request.method == "POST":
        # Zkontroluj, zda byl nahrán soubor
        if 'file' not in request.files:
            return render_template('index.html', error="Žádný soubor nebyl vybrán.")
        
        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', error="Nevybral jsi žádný název souboru.")

        try:
            # Načtení obrázku přímo z paměti (neukládáme ho na disk)
            image = Image.open(io.BytesIO(file.read()))
            # Převod na ASCII
            ascii_art = convert_image_to_ascii(image)
        except Exception as e:
             return render_template('index.html', error=f"Chyba při zpracování: {e}")

    return render_template("index.html", ascii_art=ascii_art)

if __name__ == "__main__":
    # Aplikace poběží na portu 5000 a bude dostupná zvenčí (host 0.0.0.0)
    #app.run(host='0.0.0.0', port=5000)
    #app.run(debug=True, host='0.0.0.0', port=5000)
    app.run(debug=True, host='0.0.0.0', port=8080)

