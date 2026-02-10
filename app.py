from flask import Flask, render_template, request
from PIL import Image
from markupsafe import Markup
import io

app = Flask(__name__)

# --- Znaky pro stínování (od nejtmavšího po nejsvětlejší) ---
ASCII_CHARS = ["@", "%", "#", "*", "+", "=", "-", ":", ".", " "]

def resize_image(image, new_width=100):
    width, height = image.size
    ratio = height / width
    # Korekce poměru stran (0.5 pro srovnání výšky řádku)
    new_height = int(new_width * ratio * 0.5)
    resized_image = image.resize((new_width, new_height))
    return resized_image

def pixels_to_ascii(image, mode='color'):
    pixels = image.getdata()
    width, height = image.size
    ascii_str = ""
    
    for i, pixel in enumerate(pixels):
        r, g, b = pixel
        
        # Spočítáme jas (průměr barev)
        brightness = int((r + g + b) / 3)
        
        # Vybereme znak podle jasu
        char_index = int(brightness / 255 * (len(ASCII_CHARS) - 1))
        char = ASCII_CHARS[char_index]
        
        if char == " ":
            char = "&nbsp;"
            
        # ROZHODOVÁNÍ: Barevné nebo Černobílé?
        if mode == 'color':
            # Použijeme barvu pixelu
            ascii_str += f'<span style="color: rgb({r},{g},{b})">{char}</span>'
        else:
            # Režim B&W: Použijeme bílou barvu (nebo hex #e6edf3)
            # Můžeme použít i odstíny šedi, ale čistě bílá je víc "retro"
            ascii_str += f'<span style="color: #e6edf3">{char}</span>'
        
        # Odřádkování na konci řádku
        if (i + 1) % width == 0:
            ascii_str += "<br>"
            
    return ascii_str

@app.route("/", methods=["GET", "POST"])
def index():
    ascii_art = None
    width = 80
    mode = 'color' # Výchozí režim
    
    if request.method == "POST":
        if 'file' not in request.files:
            return render_template('index.html', error="Žádný soubor.")
        
        file = request.files['file']
        
        # Načtení hodnot z formuláře
        width_str = request.form.get('width')
        if width_str:
            width = int(width_str)
            
        mode = request.form.get('mode') # Získáme 'color' nebo 'bw'

        if file.filename == '':
            return render_template('index.html', error="Nevybral jsi soubor.")

        try:
            image = Image.open(io.BytesIO(file.read()))
            image = image.convert("RGB")
            
            resized_img = resize_image(image, new_width=width)
            
            # Posíláme i zvolený režim (mode)
            raw_ascii = pixels_to_ascii(resized_img, mode=mode)
            ascii_art = Markup(raw_ascii)
            
        except Exception as e:
             return render_template('index.html', error=f"Chyba: {e}")

    return render_template("index.html", ascii_art=ascii_art, current_width=width, current_mode=mode)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)