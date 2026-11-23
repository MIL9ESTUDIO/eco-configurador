"""Compila el configurador de la Silla Eco.

Uso (desde cualquier carpeta):  python src/build.py

Fuente (src/):
  head.html    cabecera base (head + estilos); se usa todo lo anterior a <body>
  extra.css    CSS adicional, se inyecta al final del <style>
  body.html    HTML + JS del configurador
  colors.json  paletas (laqueada, especiales, epoxy)

Salida:
  index.html               en la raíz del repo (lo que publica GitHub Pages);
                           las imágenes se cargan desde la raíz.
  src/prueba.html          versión con imágenes embebidas en base64, para probar
                           sin servidor (no se versiona, ver .gitignore).
"""
import base64
import glob
import json
import os

SRC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SRC)


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as f:
        return f.read()


colors = json.loads(read("colors.json"))
src = read("head.html")
head = src[: src.index("<body>")]
head = head.replace("</style>", read("extra.css") + "</style>")

body = read("body.html")
body = (
    body.replace("__LAQUEADA__", json.dumps(colors["laqueada"], ensure_ascii=False))
    .replace("__ESPECIALES__", json.dumps(colors["especiales"], ensure_ascii=False))
    .replace("__EPOXY__", json.dumps(colors["epoxy"], ensure_ascii=False))
)
# Logo ECO (vector, sacado del .ai): se define una vez como <symbol> y los títulos lo usan con <use href="#ecoLogo">
body = read("logo.html") + body

page = head + "<body>\n\n" + body + "\n</body>\n</html>\n"

# Publicable: imágenes en la raíz del repo.
with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8", newline="\n") as f:
    f.write(page.replace('"img/" + FILE(n)', "FILE(n)"))

# Prueba local: imágenes embebidas.
data = {}
for path in glob.glob(os.path.join(ROOT, "*.webp")) + glob.glob(os.path.join(ROOT, "thumb-*.jpg")):
    name = os.path.splitext(os.path.basename(path))[0]
    mime = "image/jpeg" if path.endswith(".jpg") else "image/webp"
    with open(path, "rb") as f:
        data[name] = "data:%s;base64,%s" % (mime, base64.b64encode(f.read()).decode())
with open(os.path.join(SRC, "prueba.html"), "w", encoding="utf-8", newline="\n") as f:
    f.write(page.replace("const IMGDATA = null; /*EMBED*/", "const IMGDATA = " + json.dumps(data) + ";"))

print("index.html:", len(page), "caracteres")
