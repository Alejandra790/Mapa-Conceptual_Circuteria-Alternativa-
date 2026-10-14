#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mapa conceptual: circuitería de entrada/salida (E/S) de una computadora.

Programa escrito SOLO con la biblioteca estándar de Python (no necesita
instalar nada con pip).  Dibuja el mapa con estilo de plantilla colorida
(título con contorno, cajas pastel, notas amarillas, flechas dibujadas a
mano y decoraciones) y lo guarda como imagen vectorial SVG en "salida/".

El SVG se abre en cualquier navegador (Edge, Chrome...), se puede insertar
en Word o PowerPoint y no pierde calidad al ampliarlo o imprimirlo.

Estructura del programa:
  1. Constantes de color, fuente y tamaño del lienzo.
  2. Clase Lienzo: escribe las formas básicas en formato SVG.
  3. Funciones auxiliares de dibujo (cajas, notas, flechas, decoraciones).
  4. dibujar(): coloca todos los conceptos y sus palabras de enlace.
  5. main(): genera el archivo y lo abre en el navegador.

Cada flecha lleva una palabra de enlace, de modo que se lee como una
proposición: concepto -> palabra de enlace -> concepto.
"""

import math
import random
import sys
import textwrap
import webbrowser
from html import escape
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. Configuración general
# ---------------------------------------------------------------------------
CARPETA_SALIDA = Path(__file__).resolve().parent / "salida"
NOMBRE_ARCHIVO = "mapa_conceptual_e_s.svg"

ANCHO, ALTO = 1600, 1200           # sistema de coordenadas del dibujo (y hacia abajo)

# Fuentes: el navegador usa la primera que tenga instalada.
FUENTE_TEXTO = "Trebuchet MS, Segoe UI, DejaVu Sans, sans-serif"
FUENTE_TITULO = "Arial Black, Impact, DejaVu Sans, sans-serif"

# Paleta pastel de la plantilla
TINTA = "#1E1E1E"
SALMON = "#F9A798"
AZUL = "#A9CCF2"
MENTA = "#A6F4D9"
ROSA = "#F08FE4"
MORADO = "#AC97F3"
AMARILLO_NOTA = "#EDEF8F"
AMARILLO_SOL = "#F5E66B"
PILDORA_AZUL = "#97C9EC"
PILDORA_MENTA = "#8DF0CE"
PILDORA_MORADO = "#8E78F4"
MENTA_TITULO = "#86F2CC"
ROSA_FLOR = "#F06FDA"
AZUL_ARCO = "#9BB9EB"

PT = 100 / 72                      # 1 punto tipográfico = 1.389 unidades del dibujo


# ---------------------------------------------------------------------------
# 2. Lienzo SVG
# ---------------------------------------------------------------------------
class Lienzo:
    """Acumula formas SVG y las escribe en un archivo.
    Cada forma tiene un nivel "z": las de z menor quedan detrás."""

    def __init__(self):
        self._elementos = []

    def _agregar(self, z, svg):
        self._elementos.append((z, len(self._elementos), svg))

    def poligono(self, puntos, relleno, z=2):
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in puntos)
        self._agregar(z, f'<polygon points="{pts}" fill="{relleno}"/>')

    def motas(self, puntos, z=2):
        """Puntitos claros que dan textura de tiza."""
        c = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1"/>' for x, y in puntos)
        self._agregar(z, f'<g fill="#FFFFFF" fill-opacity="0.35">{c}</g>')

    def linea(self, puntos, grosor_pt=5.2, color=TINTA, z=4):
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in puntos)
        self._agregar(z, (f'<polyline points="{pts}" fill="none" stroke="{color}" '
                          f'stroke-width="{grosor_pt * PT:.2f}" stroke-linecap="round" '
                          f'stroke-linejoin="round"/>'))

    def rect_redondeado(self, x, y, ancho, alto, radio, relleno, z=2):
        self._agregar(z, (f'<rect x="{x:.1f}" y="{y:.1f}" width="{ancho:.1f}" '
                          f'height="{alto:.1f}" rx="{radio}" ry="{radio}" fill="{relleno}"/>'))

    def circulo(self, cx, cy, r, relleno="none", borde=None, grosor_pt=0, z=2):
        extra = f' stroke="{borde}" stroke-width="{grosor_pt * PT:.2f}"' if borde else ""
        self._agregar(z, f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{relleno}"{extra}/>')

    def elipse(self, cx, cy, ancho, alto, angulo, relleno, z=2):
        self._agregar(z, (f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{ancho / 2:.1f}" '
                          f'ry="{alto / 2:.1f}" fill="{relleno}" '
                          f'transform="rotate({angulo:.1f} {cx:.1f} {cy:.1f})"/>'))

    def anillo_superior(self, cx, cy, radio, grosor, relleno, z=2):
        """Medio anillo (arco de arcoíris) con el centro en (cx, cy)."""
        ri = radio - grosor
        d = (f"M {cx - radio:.1f} {cy:.1f} A {radio} {radio} 0 0 1 {cx + radio:.1f} {cy:.1f} "
             f"L {cx + ri:.1f} {cy:.1f} A {ri} {ri} 0 0 0 {cx - ri:.1f} {cy:.1f} Z")
        self._agregar(z, f'<path d="{d}" fill="{relleno}"/>')

    def texto(self, x, y, texto, size, negrita=False, cursiva=False, color=TINTA,
              ancla="middle", familia=FUENTE_TEXTO, z=6, contorno=None, grosor_contorno=0):
        """Texto centrado verticalmente en y.  Admite varias líneas con \\n.
        'contorno' dibuja un borde (o halo blanco) alrededor de las letras."""
        fs = size * PT
        lineas = texto.split("\n")
        alto_linea = fs * 1.15
        partes = []
        for i, linea in enumerate(lineas):
            yc = y + (i - (len(lineas) - 1) / 2) * alto_linea
            partes.append(f'<text x="{x:.1f}" y="{yc + 0.35 * fs:.1f}">{escape(linea)}</text>')
        atrib = (f'font-family="{familia}" font-size="{fs:.1f}" text-anchor="{ancla}" '
                 f'fill="{color}"')
        if negrita:
            atrib += ' font-weight="700"'
        if cursiva:
            atrib += ' font-style="italic"'
        if contorno:
            atrib += (f' stroke="{contorno}" stroke-width="{grosor_contorno:.1f}" '
                      f'stroke-linejoin="round" paint-order="stroke"')
        self._agregar(z, f'<g {atrib}>{"".join(partes)}</g>')

    def guardar(self, ruta):
        orden = sorted(self._elementos)
        cuerpo = "\n".join(s for _, _, s in orden)
        svg = (f'<?xml version="1.0" encoding="UTF-8"?>\n'
               f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ANCHO} {ALTO}" '
               f'width="{ANCHO}" height="{ALTO}">\n'
               f'<title>Mapa conceptual: circuitería de entrada/salida (E/S)</title>\n'
               f'<rect width="{ANCHO}" height="{ALTO}" fill="#FFFFFF"/>\n'
               f'{cuerpo}\n</svg>\n')
        Path(ruta).write_text(svg, encoding="utf-8")


# ---------------------------------------------------------------------------
# 3. Funciones auxiliares
# ---------------------------------------------------------------------------
def ancho_caracter(size, negrita=False):
    """Ancho aproximado (en unidades del dibujo) de un carácter."""
    return (0.70 if negrita else 0.62) * size * PT


def envolver(texto, ancho, size, negrita=False):
    """Divide un texto en líneas que quepan en el ancho indicado."""
    n = max(8, int(ancho / ancho_caracter(size, negrita)))
    return textwrap.wrap(texto, n, break_long_words=False) or [""]


def bloque_texto(lz, cx, cy, ancho, titulo, cuerpo, size=12, z=6):
    """Escribe un título en negritas y un cuerpo, centrados en (cx, cy).
    Devuelve la altura total ocupada para poder comprobar que cabe."""
    lineas = []
    if titulo:
        lineas += [(l, True, size + 1) for l in envolver(titulo, ancho, size + 1, True)]
    if cuerpo:
        lineas += [(l, False, size) for l in envolver(cuerpo, ancho, size)]

    def alto_linea(s):
        return s * PT * 1.22

    total = sum(alto_linea(s) for _, _, s in lineas)
    y = cy - total / 2
    for texto, negrita, s in lineas:
        h = alto_linea(s)
        lz.texto(cx, y + h / 2, texto, s, negrita=negrita, z=z)
        y += h
    return total


def rectangulo_rugoso(lz, x0, y0, x1, y1, color, semilla, z=2):
    """Rectángulo de bordes ligeramente irregulares y con textura de tiza."""
    rnd = random.Random(semilla)
    puntos = []

    def borde(ax_, ay, bx, by):
        n = max(2, int(math.hypot(bx - ax_, by - ay) / 45))
        for i in range(n):
            t = i / n
            puntos.append((ax_ + (bx - ax_) * t + rnd.uniform(-1.6, 1.6),
                           ay + (by - ay) * t + rnd.uniform(-1.6, 1.6)))

    borde(x0, y0, x1, y0)
    borde(x1, y0, x1, y1)
    borde(x1, y1, x0, y1)
    borde(x0, y1, x0, y0)
    lz.poligono(puntos, color, z)

    # Motas claras para dar textura
    n = int((x1 - x0) * (y1 - y0) / 350)
    lz.motas([(rnd.uniform(x0 + 3, x1 - 3), rnd.uniform(y0 + 3, y1 - 3)) for _ in range(n)],
             z + 0.1)


def caja(lz, x0, y0, x1, y1, color, titulo, cuerpo, size=12, semilla=1):
    """Caja de color con un concepto (título) y su explicación breve."""
    rectangulo_rugoso(lz, x0, y0, x1, y1, color, semilla)
    alto = bloque_texto(lz, (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0 - 28, titulo, cuerpo, size)
    if alto > (y1 - y0) - 8:
        print(f"AVISO: el texto de «{titulo}» podría no caber en su caja.")


def nota(lz, cx, y0, ancho, alto, titulo, cuerpo, semilla=1, size=10.5):
    """Nota adhesiva amarilla con sombra azul desplazada."""
    x0, x1 = cx - ancho / 2, cx + ancho / 2
    rectangulo_rugoso(lz, x0 + 16, y0 + 16, x1 + 16, y0 + alto + 16, AZUL, semilla + 50, z=2)
    rectangulo_rugoso(lz, x0, y0, x1, y0 + alto, AMARILLO_NOTA, semilla, z=2.3)
    total = bloque_texto(lz, cx, y0 + alto / 2, ancho - 22, titulo, cuerpo, size)
    if total > alto - 8:
        print(f"AVISO: el texto de la nota «{titulo}» podría no caber.")


def pildora(lz, cx, cy, texto, color, size=22):
    """Etiqueta redondeada que titula cada columna."""
    lineas = texto.split("\n")
    w = max(len(l) for l in lineas) * ancho_caracter(size, True) + 56
    h = len(lineas) * size * PT * 1.25 + 26
    lz.rect_redondeado(cx - w / 2, cy - h / 2, w, h, 16, color, z=2)
    lz.texto(cx, cy, texto, size, negrita=True)


def enlace(lz, x, y, texto, ancla="middle", size=10.5):
    """Palabra de enlace (cursiva) con halo blanco para que sea legible."""
    lz.texto(x, y, texto, size, cursiva=True, color="#2B2B2B", ancla=ancla, z=8,
             contorno="#FFFFFF", grosor_contorno=14)


# ----- Flechas dibujadas a mano ---------------------------------------------
def suavizar(puntos, iteraciones=3):
    """Suaviza una poligonal (corte de esquinas de Chaikin)."""
    for _ in range(iteraciones):
        nuevos = [puntos[0]]
        for (x0, y0), (x1, y1) in zip(puntos[:-1], puntos[1:]):
            nuevos.append((0.75 * x0 + 0.25 * x1, 0.75 * y0 + 0.25 * y1))
            nuevos.append((0.25 * x0 + 0.75 * x1, 0.25 * y0 + 0.75 * y1))
        nuevos.append(puntos[-1])
        puntos = nuevos
    return puntos


def trazo(lz, puntos, suave=False, grosor=5.2, z=4):
    if suave:
        puntos = suavizar(puntos)
    lz.linea(puntos, grosor, TINTA, z)
    return puntos


def punta(lz, x, y, ang, largo=26, abertura=0.52, grosor=5.2, z=4):
    """Punta de flecha en forma de V."""
    for s in (-1, 1):
        a = ang + math.pi + s * abertura
        lz.linea([(x, y), (x + largo * math.cos(a), y + largo * math.sin(a))], grosor, TINTA, z)


def flecha(lz, puntos, suave=False):
    """Línea con punta de flecha al final."""
    pts = trazo(lz, puntos, suave)
    (x0, y0), (x1, y1) = pts[-2], pts[-1]
    punta(lz, x1, y1, math.atan2(y1 - y0, x1 - x0))


def recta(lz, p0, p1, semilla=0):
    """Flecha casi recta con un ligero temblor, como hecha a mano."""
    rnd = random.Random(semilla)
    mx = (p0[0] + p1[0]) / 2 + rnd.uniform(-2, 2)
    my = (p0[1] + p1[1]) / 2 + rnd.uniform(-2, 2)
    flecha(lz, [p0, (mx, my), p1], suave=True)


def ondulada(lz, x, y0, y1, desvio=0):
    """Flecha ondulada (en S) que baja de y0 a y1."""
    h = y1 - y0
    pts = [(x, y0), (x - 14, y0 + h * 0.25), (x + 14, y0 + h * 0.5),
           (x - 4 + desvio, y0 + h * 0.78), (x + desvio, y1)]
    flecha(lz, pts, suave=True)


def llave(lz, x_izq, x_der, x_centro, y_barra, y_origen, y_fin):
    """Barra horizontal que reparte tres flechas hacia abajo (como en la plantilla)."""
    trazo(lz, [(x_izq, y_barra), (x_centro, y_barra - 3), (x_der, y_barra)], suave=True)
    trazo(lz, [(x_centro, y_origen), (x_centro, y_barra)])
    for x in (x_izq, x_centro, x_der):
        recta(lz, (x, y_barra), (x, y_fin))


# ----- Decoraciones -----------------------------------------------------------
def estrella(lz, cx, cy, r, semilla=1):
    rnd = random.Random(semilla)
    pts = []
    for k in [0, 2, 4, 1, 3, 0]:
        a = math.radians(-90 + 72 * k)
        rr = r * rnd.uniform(0.92, 1.06)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    trazo(lz, pts, grosor=4.2, z=2)


def destello(lz, cx, cy, r):
    k = 0.22 * r
    pts = [(cx, cy - r), (cx + k, cy - k), (cx + r * 0.62, cy), (cx + k, cy + k),
           (cx, cy + r), (cx - k, cy + k), (cx - r * 0.62, cy), (cx - k, cy - k), (cx, cy - r)]
    trazo(lz, pts, grosor=3.6, z=2)


def flor(lz, cx, cy, r=28):
    for i in range(5):
        a = math.radians(-90 + 72 * i)
        px, py = cx + r * 0.72 * math.cos(a), cy + r * 0.72 * math.sin(a)
        lz.elipse(px, py, r * 1.15, r * 0.95, math.degrees(a), ROSA_FLOR, z=2)
    lz.circulo(cx, cy, r * 0.22, relleno=TINTA, z=3)


def bombilla(lz, cx, cy, lado=1):
    """Foco amarillo con rayos; lado=-1 lo refleja horizontalmente."""
    lz.circulo(cx - 6 * lado, cy + 2, 38, relleno=AMARILLO_SOL, z=2)
    lz.circulo(cx, cy, 42, borde=TINTA, grosor_pt=2.6, z=3)
    for i in range(3):
        y = cy + 52 + i * 9
        trazo(lz, [(cx - 20, y), (cx + 20, y)], grosor=2.6, z=3)
    for (dx0, dy0, dx1, dy1) in [(-64, -26, -86, -36), (-68, 2, -92, 6), (-56, 30, -76, 44)]:
        trazo(lz, [(cx + lado * dx0, cy + dy0), (cx + lado * dx1, cy + dy1)], grosor=2.6, z=2)


def arcoiris(lz, cx, cy):
    lz.anillo_superior(cx, cy, 64, 15, AMARILLO_SOL)
    lz.anillo_superior(cx, cy, 47, 15, AZUL_ARCO)
    lz.anillo_superior(cx, cy, 30, 13, AMARILLO_SOL)


# ---------------------------------------------------------------------------
# 4. Contenido y distribución del mapa
# ---------------------------------------------------------------------------
def dibujar(lz):
    # ---- Título ("MAPA" con contorno menta y "Conceptual" sobre barra rosa) ----
    rectangulo_rugoso(lz, 690, 85, 1130, 192, ROSA, 7)
    lz.texto(570, 140, "MAPA", 72, negrita=True, familia=FUENTE_TITULO,
             contorno=MENTA_TITULO, grosor_contorno=15 * PT)
    lz.texto(910, 140, "Conceptual", 44, negrita=True, familia=FUENTE_TITULO)

    # ---- Concepto principal ----
    bloque_texto(lz, 808, 242, 480,
                 "Sistema de entrada/salida (E/S) de una computadora",
                 "Conjunto de circuitos y mecanismos que comunican a la computadora con el exterior",
                 size=13)

    # Flechas del concepto principal hacia las tres ramas
    flecha(lz, [(548, 258), (330, 258), (330, 384)])
    enlace(lz, 440, 258, "se conecta con los")
    flecha(lz, [(1068, 258), (1285, 258), (1285, 384)])
    enlace(lz, 1175, 258, "realiza la")
    recta(lz, (808, 291), (808, 321))
    enlace(lz, 838, 306, "se apoya en", ancla="start")

    # =====================  COLUMNA IZQUIERDA: DISPOSITIVOS  =====================
    pildora(lz, 330, 430, "Dispositivos", PILDORA_AZUL)
    caja(lz, 100, 480, 560, 570, SALMON, "Dispositivos periféricos",
         "Equipos externos al procesador y a la memoria", semilla=11)

    llave(lz, 118, 542, 330, 606, 570, 652)
    enlace(lz, 224, 606, "se clasifican en")

    nota(lz, 118, 655, 170, 190, "Dispositivos de entrada",
         "Envían datos a la computadora. Ej.: teclado, ratón, escáner", semilla=21)
    nota(lz, 330, 655, 170, 190, "Dispositivos de salida",
         "Presentan datos al usuario. Ej.: monitor, impresora, bocinas", semilla=22)
    nota(lz, 542, 655, 170, 190, "Dispositivos de entrada y salida",
         "Envían y reciben datos. Ej.: disco duro, memoria USB, pantalla táctil", semilla=23)

    ondulada(lz, 118, 866, 918, desvio=14)
    ondulada(lz, 330, 866, 918)
    ondulada(lz, 542, 866, 918, desvio=-14)
    enlace(lz, 224, 892, "se conectan mediante")

    caja(lz, 100, 922, 560, 1007, AZUL, "Controladores o interfaces de E/S",
         "Circuitos que adaptan las señales del dispositivo a las del sistema", semilla=31)
    recta(lz, (330, 1009), (330, 1051))
    enlace(lz, 344, 1030, "avisan a la CPU mediante", ancla="start")
    caja(lz, 100, 1054, 560, 1150, AZUL, "Interrupciones",
         "Señales con las que el controlador avisa a la CPU de que un dispositivo requiere atención",
         semilla=32)

    # Controladores -> Puertos y buses (flecha en codo hacia la columna central)
    flecha(lz, [(562, 965), (668, 965), (668, 745), (694, 745)])
    enlace(lz, 614, 930, "se comunican\nmediante", size=10)

    # ======================  COLUMNA CENTRAL: CPU, BUSES, MEMORIA  ======================
    pildora(lz, 808, 360, "CPU, buses\ny memoria", PILDORA_MENTA, size=20)
    flecha(lz, [(686, 352), (650, 372), (615, 400), (612, 435), (635, 465), (670, 488)], suave=True)
    enlace(lz, 585, 420, "incluye", size=10)
    flecha(lz, [(930, 352), (966, 372), (1001, 400), (1004, 435), (981, 465), (946, 488)], suave=True)
    enlace(lz, 1048, 420, "incluye", size=10)

    caja(lz, 695, 425, 922, 585, AZUL, "Procesador (CPU)",
         "Ejecuta las instrucciones y coordina las operaciones de E/S", size=11, semilla=41)
    recta(lz, (808, 587), (808, 658))
    enlace(lz, 822, 622, "se comunica mediante", ancla="start", size=10)
    caja(lz, 695, 660, 922, 830, ROSA, "Puertos y buses de comunicación",
         "Vías por donde viajan datos, direcciones y señales de control", size=11, semilla=42)
    recta(lz, (808, 832), (808, 903))
    enlace(lz, 822, 868, "enlazan con la", ancla="start", size=10)
    caja(lz, 695, 905, 922, 1075, MENTA, "Memoria principal",
         "Almacena programas y datos en uso; es origen o destino de la transferencia de datos",
         size=11, semilla=43)

    # CPU -> Transferencia de datos
    recta(lz, (924, 538), (1053, 538))
    enlace(lz, 988, 518, "coordina la", size=10)

    # =====================  COLUMNA DERECHA: TRANSFERENCIA  =====================
    pildora(lz, 1285, 435, "Transferencia", PILDORA_MORADO)
    caja(lz, 1055, 485, 1515, 592, MENTA, "Transferencia de datos",
         "Movimiento de datos entre los dispositivos y la memoria o el procesador", semilla=51)

    llave(lz, 1073, 1497, 1285, 610, 592, 652)
    enlace(lz, 1179, 610, "puede realizarse con")

    nota(lz, 1073, 655, 170, 190, "E/S programada",
         "La CPU consulta una y otra vez si el dispositivo está listo", semilla=61)
    nota(lz, 1285, 655, 170, 190, "E/S mediante interrupciones",
         "La CPU trabaja en otra tarea y atiende al dispositivo cuando este avisa", semilla=62)
    nota(lz, 1497, 655, 170, 190, "Acceso directo a memoria (DMA)",
         "Un controlador mueve bloques de datos a la memoria sin pasar por la CPU", semilla=63)

    ondulada(lz, 1073, 866, 918, desvio=14)
    ondulada(lz, 1285, 866, 918)
    ondulada(lz, 1497, 866, 918, desvio=-14)
    enlace(lz, 1179, 892, "se diferencian en la")

    caja(lz, 1055, 922, 1515, 1007, MORADO, "Participación de la CPU",
         "Es máxima en la E/S programada, parcial con interrupciones y mínima con DMA",
         semilla=71)
    caja(lz, 1055, 1054, 1515, 1150, MORADO, "Cómo leer el mapa",
         "Concepto → palabra de enlace → concepto. Cada flecha forma una oración completa.",
         semilla=72)

    # ---- Decoraciones (sin significado conceptual) ----
    estrella(lz, 100, 100, 38, 1)
    estrella(lz, 1478, 98, 40, 2)
    estrella(lz, 1080, 372, 28, 3)
    estrella(lz, 632, 1085, 32, 4)
    destello(lz, 82, 415, 40)
    destello(lz, 1540, 418, 40)
    flor(lz, 293, 92, 30)
    flor(lz, 1270, 100, 28)
    flor(lz, 1558, 1100, 30)
    bombilla(lz, 160, 248, 1)
    bombilla(lz, 1485, 252, -1)
    arcoiris(lz, 880, 1160)


# ---------------------------------------------------------------------------
# 5. Programa principal
# ---------------------------------------------------------------------------
def main():
    lienzo = Lienzo()
    dibujar(lienzo)

    CARPETA_SALIDA.mkdir(exist_ok=True)
    ruta = CARPETA_SALIDA / NOMBRE_ARCHIVO
    lienzo.guardar(ruta)
    print("Mapa conceptual generado correctamente:")
    print("  -", ruta)

    # Abre el resultado en el navegador (omitir con: python main.py --no-abrir)
    if "--no-abrir" not in sys.argv:
        webbrowser.open(ruta.as_uri())


if __name__ == "__main__":
    main()
