"""
EVRYWR.MEDIA — Setup Drive + Sheet
Crea la estructura de carpetas en Drive y el calendario editorial en Google Sheets.
"""

import httplib2
_orig_http_init = httplib2.Http.__init__
def _http_no_ssl(self, *a, **kw):
    kw.setdefault("disable_ssl_certificate_validation", True)
    _orig_http_init(self, *a, **kw)
httplib2.Http.__init__ = _http_no_ssl  # noqa: proxy self-signed cert

from google_workspace import Drive, Sheets
from google_workspace.auth import get_service

# ─── DRIVE ──────────────────────────────────────────────────────────────────

drive = Drive()
sheets_client = Sheets()
drive_service = get_service("drive", "v3")
sheets_service = get_service("sheets", "v4")


def create_folder(name, parent_id=None):
    f = drive.create_folder(name, parent_id)
    print(f"  📁 {name}")
    return f["id"], f["webViewLink"]


print("\n=== Creando estructura de carpetas en Drive ===\n")

# Root
evrywr_id, evrywr_link = create_folder("EVRYWR")

# MARZO 2026
marzo_id, _ = create_folder("MARZO 2026", evrywr_id)

# Semanas
w1_id, _ = create_folder("W1 - POSITIONING", marzo_id)
w2_id, _ = create_folder("W2 - AUTHORITY", marzo_id)
w3_id, _ = create_folder("W3 - HUMANIZATION", marzo_id)
w4_id, _ = create_folder("W4 - CONVERSION", marzo_id)

# Carpetas por post — (id, link) guardados para el sheet
post_folders = {}

posts_w1 = [
    ("MAR03 - EDU - 5 Errores Algoritmo", w1_id),
    ("MAR05 - CASE - Cliente Placeholder 1", w1_id),
    ("MAR07 - BTS - Reel con IA Higgsfield", w1_id),
]
posts_w2 = [
    ("MAR10 - EDU - Hashtags 2026", w2_id),
    ("MAR12 - TREND - Instagram SEO", w2_id),
    ("MAR14 - COMM - Encuesta Redes", w2_id),
]
posts_w3 = [
    ("MAR17 - EDU - Carousels vs Reels", w3_id),
    ("MAR19 - CASE - Cliente Placeholder 2", w3_id),
    ("MAR21 - BTS - Un Dia en EVRYWR", w3_id),
]
posts_w4 = [
    ("MAR24 - EDU - Hooks 10 Templates", w4_id),
    ("MAR26 - CASE - Cliente Placeholder 3", w4_id),
    ("MAR28 - TREND - Agencias IA", w4_id),
    ("MAR31 - COMM - Recap Marzo", w4_id),
]

for name, parent in posts_w1 + posts_w2 + posts_w3 + posts_w4:
    pid, link = create_folder(name, parent)
    # Key: fecha corta, e.g. "MAR03"
    key = name.split(" - ")[0]
    post_folders[key] = link

# ASSETS
assets_id, _ = create_folder("ASSETS", evrywr_id)
for sub in ["B-Roll", "Templates Graficos", "Brand Guidelines", "Musica y Audio", "Fotos Equipo"]:
    create_folder(sub, assets_id)

# CLIENTES
clientes_id, _ = create_folder("CLIENTES", evrywr_id)
for sub in ["Cliente 1 - Placeholder", "Cliente 2 - Placeholder", "Cliente 3 - Placeholder"]:
    create_folder(sub, clientes_id)

# REFERENCIAS
refs_id, _ = create_folder("REFERENCIAS", evrywr_id)
for sub in ["Inspiracion Visual", "Competencia", "Benchmarks y Data", "Guiones de Referencia"]:
    create_folder(sub, refs_id)

print(f"\n✅ Estructura creada. Carpeta raíz EVRYWR: {evrywr_link}\n")

# ─── SHEET ──────────────────────────────────────────────────────────────────

print("=== Creando Google Sheet ===\n")

sp = sheets_service.spreadsheets().create(
    body={"properties": {"title": "EVRYWR.MEDIA — Calendario Editorial Marzo 2026"}},
    fields="spreadsheetId,spreadsheetUrl",
).execute()

sheet_id = sp["spreadsheetId"]
sheet_url = sp["spreadsheetUrl"]
print(f"  📊 Sheet creado: {sheet_url}")

# ── Obtener sheetId de la primera hoja ──────────────────────────────────────
info = sheets_service.spreadsheets().get(spreadsheetId=sheet_id).execute()
tab_id = info["sheets"][0]["properties"]["sheetId"]

# ── ENCABEZADOS ─────────────────────────────────────────────────────────────
headers = [
    "FECHA",
    "DÍA",
    "SEMANA | TEMA",
    "TIPO",
    "FORMATO",
    "TÍTULO / TOPIC",
    "HOOK (Primeras líneas)",
    "SCRIPT / CAPTION",
    "NOTAS DE PRODUCCIÓN",
    "ESTADO",
    "RESPONSABLE",
    "📁 CARPETA DRIVE",
    "🖼 ASSETS / REFERENCIAS",
    "👁 BORRADOR / PREVIEW",
    "🔗 POST PUBLICADO",
    "📈 ALCANCE",
    "❤️ ENGAGEMENT",
    "# HASHTAGS / KEYWORDS",
    "🤖 CTA / KEYWORD MANYCHAT",
]

# ── DATOS DEL CALENDARIO ────────────────────────────────────────────────────
assets_link = f"https://drive.google.com/drive/folders/{assets_id}"
refs_link   = f"https://drive.google.com/drive/folders/{refs_id}"

rows = [
    # W1
    ["MAR 3",  "Lunes",    "W1 · POSITIONING", "EDU",  "Carousel",
     "5 errores que matan el alcance en Instagram 2026",
     "Tu contenido es bueno pero nadie lo ve. El problema no eres tú, es tu estrategia de 2024...",
     "", "Hooks + screenshots de métricas. ManyChat keyword: AUDIT",
     "Pendiente", "", post_folders.get("MAR03",""), assets_link, "", "", "", "", "#instagram #estrategia #socialmedia", "AUDIT"],

    ["MAR 5",  "Miércoles","W1 · POSITIONING", "CASE", "Reel",
     "[PLACEHOLDER] Trabajo/Testimonio Cliente — De 200 views a 15K en 30 días",
     "De 200 views a 15K en 30 días — cómo lo hicimos para [Cliente]",
     "", "⚠ REQUIERE CLIENTE REAL. Usar métrica real + antes/después",
     "Pendiente", "", post_folders.get("MAR05",""), assets_link, "", "", "", "", "#casodeexito #resultados", "CASO"],

    ["MAR 7",  "Viernes",  "W1 · POSITIONING", "BTS",  "Story→Reel",
     "Así creamos un Reel con IA en 15 minutos (Higgsfield)",
     "La gente piensa que la IA reemplaza creativos. Falso. La IA potencia a los que tienen ideas...",
     "", "Pantalla compartida, proceso real sin filtros",
     "Pendiente", "", post_folders.get("MAR07",""), assets_link, "", "", "", "#ia #reels #bts", ""],

    # W2
    ["MAR 10", "Lunes",    "W2 · AUTHORITY",   "EDU",  "Carousel",
     "Hashtags en 2026: por qué ya NO funcionan (y qué hacer)",
     "Llevás usando 30 hashtags y tu alcance sigue igual. Es hora de hablar de SEO...",
     "", "Data de investigación 2026",
     "Pendiente", "", post_folders.get("MAR10",""), refs_link, "", "", "", "#hashtags #seo #instagram2026", ""],

    ["MAR 12", "Miércoles","W2 · AUTHORITY",   "TREND","Reel",
     "Instagram ahora es un buscador — y nadie lo está usando bien",
     "Google indexa tus posts. Si no optimizás para SEO, eres invisible...",
     "", "Screen recording de búsqueda Google mostrando posts",
     "Pendiente", "", post_folders.get("MAR12",""), refs_link, "", "", "", "#instagramseo #marketing", ""],

    ["MAR 14", "Viernes",  "W2 · AUTHORITY",   "COMM", "Post+Stories",
     "Pregunta: ¿Qué les cuesta MÁS de manejar sus redes?",
     "¿Qué los está frenando? ¿Tiempo? ¿Ideas? ¿Edición?",
     "", "Encuesta interactiva — guardar respuestas para contenido futuro",
     "Pendiente", "", post_folders.get("MAR14",""), assets_link, "", "", "", "#comunidad #engagement", ""],

    # W3
    ["MAR 17", "Lunes",    "W3 · HUMANIZATION","EDU",  "Reel",
     "Carousels vs Reels: cuál usar según tu número de seguidores",
     "Si tenés menos de 50K, hacé Reels. Si tenés más, carousels. Aquí la data...",
     "", "Gráfica animada con data real",
     "Pendiente", "", post_folders.get("MAR17",""), refs_link, "", "", "", "#reels #carousel #estrategia", ""],

    ["MAR 19", "Miércoles","W3 · HUMANIZATION","CASE", "Carousel",
     "[PLACEHOLDER] Proyecto: [Nombre Cliente] — Objetivo / Proceso / Resultados",
     "Proyecto: [Nombre Cliente] — Objetivo / Proceso / Resultados",
     "", "⚠ REQUIERE CLIENTE REAL. Mostrar entregables reales",
     "Pendiente", "", post_folders.get("MAR19",""), assets_link, "", "", "", "#proyecto #agencia", "CASO"],

    ["MAR 21", "Viernes",  "W3 · HUMANIZATION","BTS",  "Reel",
     "Un día en EVRYWR: de brief a post publicado",
     "7 AM: llega el brief. 6 PM: está en el feed del cliente. Así pasa la magia...",
     "", "Time-lapse del equipo trabajando",
     "Pendiente", "", post_folders.get("MAR21",""), assets_link, "", "", "", "#bts #agencia #equipo", ""],

    # W4
    ["MAR 24", "Lunes",    "W4 · CONVERSION",  "EDU",  "Carousel",
     "Cómo escribir hooks que paran el scroll (10 templates)",
     "El 80% del alcance se decide en los primeros 3 segundos. Roba estos 10 hooks...",
     "", "Templates copiables en slides",
     "Pendiente", "", post_folders.get("MAR24",""), refs_link, "", "", "", "#copywriting #hooks #contenido", "HOOKS"],

    ["MAR 26", "Miércoles","W4 · CONVERSION",  "CASE", "Reel",
     "[PLACEHOLDER] Cliente: [Nombre] — Desafío / Estrategia / ROI",
     "Cliente: [Nombre] — Desafío / Estrategia / ROI",
     "", "⚠ REQUIERE CLIENTE REAL. Testimonial en video o quote gráfico",
     "Pendiente", "", post_folders.get("MAR26",""), assets_link, "", "", "", "#roi #resultados #casodeexito", "CASO"],

    ["MAR 28", "Viernes",  "W4 · CONVERSION",  "TREND","Post+Carousel",
     "Por qué las agencias que usan IA sin estrategia están quebrando",
     "La IA no es una varita mágica. Es una herramienta. Sin cerebro humano, es basura...",
     "", "Opinión bold — posicionamiento de expertise",
     "Pendiente", "", post_folders.get("MAR28",""), refs_link, "", "", "", "#ia #agencias #estrategia", ""],

    ["MAR 31", "Lunes",    "W4 · CONVERSION",  "COMM", "Reel+Stories",
     "Recap Marzo: lo que funcionó, lo que aprendimos, lo que viene",
     "Cerramos el mes con [X] posts, [X] alcance. Esto aprendimos...",
     "", "Transparencia total — Build in Public",
     "Pendiente", "", post_folders.get("MAR31",""), assets_link, "", "", "", "#recap #buildinpublic #marzo", ""],
]

# ── Escribir datos ───────────────────────────────────────────────────────────
all_data = [headers] + rows

sheets_service.spreadsheets().values().update(
    spreadsheetId=sheet_id,
    range="A1",
    valueInputOption="USER_ENTERED",
    body={"values": all_data},
).execute()

print("  ✏️  Datos escritos")

# ── FORMATO ─────────────────────────────────────────────────────────────────
# Colores del sistema EVRYWR
BLACK  = {"red": 0.051, "green": 0.051, "blue": 0.051}   # #0D0D0D
AMBER  = {"red": 1.0,   "green": 0.722, "blue": 0.0}      # #FFB800
LIME   = {"red": 0.784, "green": 1.0,   "blue": 0.0}      # #C8FF00
BONE   = {"red": 0.961, "green": 0.941, "blue": 0.91}     # #F5F0E8
WHITE  = {"red": 1.0,   "green": 1.0,   "blue": 1.0}
CORAL  = {"red": 1.0,   "green": 0.302, "blue": 0.302}    # #FF4D4D
LGRAY  = {"red": 0.95,  "green": 0.95,  "blue": 0.95}
MGRAY  = {"red": 0.85,  "green": 0.85,  "blue": 0.85}

n_rows = len(rows)  # 13
n_cols = len(headers)  # 19

def col_range(c): return {"startColumnIndex": c, "endColumnIndex": c + 1}

requests = []

# 1. Freeze fila 1 y columnas A-B
requests.append({"updateSheetProperties": {
    "properties": {"sheetId": tab_id, "gridProperties": {"frozenRowCount": 1, "frozenColumnCount": 2}},
    "fields": "gridProperties.frozenRowCount,gridProperties.frozenColumnCount",
}})

# 2. Fila header: fondo negro, texto amber, negrita, 11px
requests.append({"repeatCell": {
    "range": {"sheetId": tab_id, "startRowIndex": 0, "endRowIndex": 1,
              "startColumnIndex": 0, "endColumnIndex": n_cols},
    "cell": {"userEnteredFormat": {
        "backgroundColor": BLACK,
        "textFormat": {"foregroundColor": AMBER, "bold": True, "fontSize": 10,
                       "fontFamily": "Arial"},
        "horizontalAlignment": "CENTER",
        "verticalAlignment": "MIDDLE",
        "wrapStrategy": "WRAP",
    }},
    "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment,wrapStrategy)",
}})

# 3. Todas las filas de datos: fondo hueso, texto negro, font 10
requests.append({"repeatCell": {
    "range": {"sheetId": tab_id, "startRowIndex": 1, "endRowIndex": 1 + n_rows,
              "startColumnIndex": 0, "endColumnIndex": n_cols},
    "cell": {"userEnteredFormat": {
        "backgroundColor": BONE,
        "textFormat": {"foregroundColor": BLACK, "fontSize": 10, "fontFamily": "Arial"},
        "verticalAlignment": "TOP",
        "wrapStrategy": "WRAP",
    }},
    "fields": "userEnteredFormat(backgroundColor,textFormat,verticalAlignment,wrapStrategy)",
}})

# 4. Columna TIPO (col 3) — color según tipo
tipo_colors = {
    "EDU":   {"bg": LIME,  "fg": BLACK},
    "CASE":  {"bg": CORAL, "fg": WHITE},
    "BTS":   {"bg": AMBER, "fg": BLACK},
    "TREND": {"bg": BLACK, "fg": AMBER},
    "COMM":  {"bg": MGRAY, "fg": BLACK},
}
for i, row in enumerate(rows):
    tipo = row[3]
    c = tipo_colors.get(tipo, {"bg": LGRAY, "fg": BLACK})
    requests.append({"repeatCell": {
        "range": {"sheetId": tab_id,
                  "startRowIndex": i + 1, "endRowIndex": i + 2,
                  "startColumnIndex": 3, "endColumnIndex": 4},
        "cell": {"userEnteredFormat": {
            "backgroundColor": c["bg"],
            "textFormat": {"foregroundColor": c["fg"], "bold": True, "fontSize": 10},
            "horizontalAlignment": "CENTER",
        }},
        "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)",
    }})

# 5. Columna FECHA (col 0) — negrita, centrada
requests.append({"repeatCell": {
    "range": {"sheetId": tab_id, "startRowIndex": 1, "endRowIndex": 1 + n_rows,
              "startColumnIndex": 0, "endColumnIndex": 1},
    "cell": {"userEnteredFormat": {
        "textFormat": {"bold": True, "fontSize": 11},
        "horizontalAlignment": "CENTER",
    }},
    "fields": "userEnteredFormat(textFormat,horizontalAlignment)",
}})

# 6. Columna ESTADO (col 9) — dropdown de validación
requests.append({"setDataValidation": {
    "range": {"sheetId": tab_id, "startRowIndex": 1, "endRowIndex": 1 + n_rows,
              "startColumnIndex": 9, "endColumnIndex": 10},
    "rule": {
        "condition": {
            "type": "ONE_OF_LIST",
            "values": [
                {"userEnteredValue": "Pendiente"},
                {"userEnteredValue": "En Producción"},
                {"userEnteredValue": "En Revisión"},
                {"userEnteredValue": "Listo"},
                {"userEnteredValue": "Publicado"},
            ],
        },
        "showCustomUi": True,
        "strict": True,
    },
}})

# 7. Colorear ESTADO según valor — condicional
estado_colors = {
    "Pendiente":     {"red": 1.0,  "green": 0.95, "blue": 0.8},
    "En Producción": {"red": 0.8,  "green": 0.9,  "blue": 1.0},
    "En Revisión":   {"red": 1.0,  "green": 0.9,  "blue": 0.6},
    "Listo":         {"red": 0.8,  "green": 1.0,  "blue": 0.8},
    "Publicado":     {"red": 0.78, "green": 1.0,  "blue": 0.0},
}
for estado, color in estado_colors.items():
    requests.append({"addConditionalFormatRule": {
        "rule": {
            "ranges": [{"sheetId": tab_id, "startRowIndex": 1, "endRowIndex": 1 + n_rows,
                        "startColumnIndex": 9, "endColumnIndex": 10}],
            "booleanRule": {
                "condition": {"type": "TEXT_EQ", "values": [{"userEnteredValue": estado}]},
                "format": {"backgroundColor": color},
            },
        },
        "index": 0,
    }})

# 8. Anchos de columna (en pixels)
col_widths = [
    70,   # FECHA
    80,   # DÍA
    140,  # SEMANA
    70,   # TIPO
    90,   # FORMATO
    260,  # TÍTULO
    260,  # HOOK
    280,  # SCRIPT
    220,  # NOTAS
    110,  # ESTADO
    120,  # RESPONSABLE
    90,   # CARPETA DRIVE
    90,   # ASSETS
    90,   # BORRADOR
    90,   # POST
    80,   # ALCANCE
    90,   # ENGAGEMENT
    200,  # HASHTAGS
    160,  # CTA
]
for i, w in enumerate(col_widths):
    requests.append({"updateDimensionProperties": {
        "range": {"sheetId": tab_id, "dimension": "COLUMNS",
                  "startIndex": i, "endIndex": i + 1},
        "properties": {"pixelSize": w},
        "fields": "pixelSize",
    }})

# 9. Altura de filas de datos
requests.append({"updateDimensionProperties": {
    "range": {"sheetId": tab_id, "dimension": "ROWS",
              "startIndex": 1, "endIndex": 1 + n_rows},
    "properties": {"pixelSize": 80},
    "fields": "pixelSize",
}})

# 10. Borde exterior de toda la tabla
requests.append({"updateBorders": {
    "range": {"sheetId": tab_id, "startRowIndex": 0, "endRowIndex": 1 + n_rows,
              "startColumnIndex": 0, "endColumnIndex": n_cols},
    "top":    {"style": "SOLID_THICK", "color": BLACK},
    "bottom": {"style": "SOLID_THICK", "color": BLACK},
    "left":   {"style": "SOLID_THICK", "color": BLACK},
    "right":  {"style": "SOLID_THICK", "color": BLACK},
    "innerHorizontal": {"style": "SOLID", "color": MGRAY},
    "innerVertical":   {"style": "SOLID", "color": MGRAY},
}})

# 11. Columnas de métricas (ALCANCE, ENGAGEMENT) — centradas y color diferenciado
requests.append({"repeatCell": {
    "range": {"sheetId": tab_id, "startRowIndex": 1, "endRowIndex": 1 + n_rows,
              "startColumnIndex": 15, "endColumnIndex": 17},
    "cell": {"userEnteredFormat": {
        "backgroundColor": {"red": 0.93, "green": 0.97, "blue": 0.93},
        "horizontalAlignment": "CENTER",
        "textFormat": {"bold": True},
    }},
    "fields": "userEnteredFormat(backgroundColor,horizontalAlignment,textFormat)",
}})

# 12. Links de Drive como hyperlink (columnas 11, 12, 13, 14)
# Ya están como texto plano — convertir las carpetas a fórmula HYPERLINK
for i, row in enumerate(rows):
    folder_url = row[11]  # 📁 CARPETA DRIVE
    if folder_url:
        sheets_service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range=f"L{i+2}",
            valueInputOption="USER_ENTERED",
            body={"values": [[f'=HYPERLINK("{folder_url}","📁 Abrir Carpeta")']]}
        ).execute()

    assets_url = row[12]  # ASSETS
    if assets_url:
        sheets_service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range=f"M{i+2}",
            valueInputOption="USER_ENTERED",
            body={"values": [[f'=HYPERLINK("{assets_url}","🖼 Assets")']]}
        ).execute()

# 13. Aplicar todos los requests de formato
sheets_service.spreadsheets().batchUpdate(
    spreadsheetId=sheet_id,
    body={"requests": requests},
).execute()

print("  🎨 Formato aplicado")

# ── Mover sheet a carpeta EVRYWR ─────────────────────────────────────────────
drive_service.files().update(
    fileId=sheet_id,
    addParents=evrywr_id,
    fields="id, parents",
).execute()
print("  📂 Sheet movido a carpeta EVRYWR")

# ── RESUMEN FINAL ────────────────────────────────────────────────────────────
print(f"""
╔══════════════════════════════════════════════════════╗
║  ✅  SETUP COMPLETO                                  ║
╠══════════════════════════════════════════════════════╣
║  📁 Carpeta EVRYWR:                                  ║
║     {evrywr_link:<50} ║
║                                                      ║
║  📊 Google Sheet:                                    ║
║     {sheet_url:<50} ║
╚══════════════════════════════════════════════════════╝
""")
