from flask import Flask, render_template, request
from PIL import Image
import io

app = Flask(__name__)

# --- Znaky pro stínování (od nejtmavšího po nejsvětlejší) ---
ASCII_CHARS = ["@", "%", "#", "*", "+", "=", "-", ":", ".", " "]

def resize_image(image, new_width=100):
    width, height = image.size
    ratio = height / width
    # DŮLEŽITÉ: Koeficient 0.5 kompenzuje to, že písmenka jsou 2x vyšší než širší
    new_height = int(new_width * ratio * 0.5)
    resized_image = image.resize((new_width, new_height))
    return resized_image

def pixels_to_color_ascii(image):
    pixels = image.getdata()
    width, height = image.size
    ascii_str = ""
    
    # Procházíme pixely
    for i, pixel in enumerate(pixels):
        # Pixel je (R, G, B) - například (255, 0, 0) je červená
        r, g, b = pixel
        
        # Spočítáme jas pro výběr znaku (průměr barev)
        brightness = int((r + g + b) / 3)
        char_index = int(brightness / 255 * (len(ASCII_CHARS) - 1))
        char = ASCII_CHARS[char_index]
        
        # Pokud je znak mezera, nahradíme ji nedělitelnou mezerou, aby se HTML nerozsypalo
        if char == " ":
            char = "&nbsp;"
            
        # Zabalíme znak do barvy
        ascii_str += f'<span style="color: rgb({r},{g},{b})">{char}</span>'
        
        # Na konci řádku přidáme odřádkování <br>
        if (i + 1) % width == 0:
            ascii_str += "<br>"
            
    return ascii_str

@app.route("/", methods=["GET", "POST"])
def index():
    ascii_art = None
    width = 80 # Výchozí šířka
    
    if request.method == "POST":
        if 'file' not in request.files:
            return render_template('index.html', error="Žádný soubor.")
        
        file = request.files['file']
        width_str = request.form.get('width')
        if width_str:
            width = int(width_str)

        if file.filename == '':
            return render_template('index.html', error="Nevybral jsi soubor.")

        try:
            image = Image.open(io.BytesIO(file.read()))
            # Převedeme na RGB (aby to fungovalo i u PNG s průhledností)
            image = image.convert("RGB")
            
            # Změna velikosti a převod
            resized_img = resize_image(image, new_width=width)
            ascii_art = pixels_to_color_ascii(resized_img)
            
        except Exception as e:
             return render_template('index.html', error=f"Chyba: {e}")

    # Posíláme 'safe' HTML, aby Flask nevypsal <span> jako text, ale jako kód
    from markupsafe import Markup
    if ascii_art:
        ascii_art = Markup(ascii_art)

    return render_template("index.html", ascii_art=ascii_art, current_width=width)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)