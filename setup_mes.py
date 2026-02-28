"""
EVRYWR.MEDIA — Setup Mensual
Crea o actualiza estructura Drive + Google Sheet para un mes del calendario editorial.

Uso:
    python3 setup_mes.py --mes marzo_2026

Si las carpetas ya existen en Drive, las reutiliza (no duplica).
Cada mes tiene su configuración en calendar_config/<mes>.py
"""

import argparse
import importlib

import httplib2

_orig_http_init = httplib2.Http.__init__


def _http_no_ssl(self, *a, **kw):
    kw.setdefault("disable_ssl_certificate_validation", True)
    _orig_http_init(self, *a, **kw)


httplib2.Http.__init__ = _http_no_ssl  # noqa: proxy self-signed cert

from google_workspace.auth import get_service  # noqa: E402

drive_svc = get_service("drive", "v3")
sheets_svc = get_service("sheets", "v4")

# ─── COLORES EVRYWR ──────────────────────────────────────────────────────────

BLACK = {"red": 0.051, "green": 0.051, "blue": 0.051}
AMBER = {"red": 1.0,   "green": 0.722, "blue": 0.0}
LIME  = {"red": 0.784, "green": 1.0,   "blue": 0.0}
BONE  = {"red": 0.961, "green": 0.941, "blue": 0.91}
WHITE = {"red": 1.0,   "green": 1.0,   "blue": 1.0}
CORAL = {"red": 1.0,   "green": 0.302, "blue": 0.302}
LGRAY = {"red": 0.95,  "green": 0.95,  "blue": 0.95}
MGRAY = {"red": 0.85,  "green": 0.85,  "blue": 0.85}

TIPO_COLORS = {
    "EDU":   {"bg": LIME,  "fg": BLACK},
    "CASE":  {"bg": CORAL, "fg": WHITE},
    "BTS":   {"bg": AMBER, "fg": BLACK},
    "TREND": {"bg": BLACK, "fg": AMBER},
    "COMM":  {"bg": MGRAY, "fg": BLACK},
}

ESTADO_OPTS = ["Pendiente", "En Producción", "En Revisión", "Listo", "Publicado"]
ESTADO_COLORS = {
    "Pendiente":     {"red": 1.0,  "green": 0.95, "blue": 0.8},
    "En Producción": {"red": 0.8,  "green": 0.9,  "blue": 1.0},
    "En Revisión":   {"red": 1.0,  "green": 0.9,  "blue": 0.6},
    "Listo":         {"red": 0.8,  "green": 1.0,  "blue": 0.8},
    "Publicado":     {"red": 0.78, "green": 1.0,  "blue": 0.0},
}

PLATAFORMA_OPTS = ["Instagram", "TikTok", "LinkedIn", "YouTube Shorts", "Multi-plataforma"]

# ─── COLUMNAS CALENDARIO ─────────────────────────────────────────────────────
#  A   B    C               D     E           F        G               H
# FECHA DÍA  SEMANA|TEMA    TIPO  PLATAFORMA  FORMATO  TÍTULO/TOPIC    HOOK
#  I              J                   K       L           M            N
# SCRIPT/CAPTION  NOTAS PRODUCCIÓN   ESTADO  RESPONSABLE  %COMPLETADO  CARPETA DRIVE
#  O       P                Q                 R                S          T            U
# ASSETS   BORRADOR/PREVIEW  POST PUBLICADO   FECHA REAL PUB.  ALCANCE    ENGAGEMENT   HASHTAGS

HEADERS = [
    "FECHA",                    # A  0
    "DÍA",                      # B  1
    "SEMANA | TEMA",            # C  2
    "TIPO",                     # D  3
    "PLATAFORMA",               # E  4
    "FORMATO",                  # F  5
    "TÍTULO / TOPIC",           # G  6
    "HOOK (Primeras líneas)",   # H  7
    "SCRIPT / CAPTION",         # I  8
    "NOTAS DE PRODUCCIÓN",      # J  9
    "ESTADO",                   # K  10
    "RESPONSABLE",              # L  11
    "% COMPLETADO",             # M  12
    "📁 CARPETA DRIVE",         # N  13
    "🖼 ASSETS",                # O  14
    "👁 BORRADOR / PREVIEW",    # P  15
    "🔗 POST PUBLICADO",        # Q  16
    "FECHA REAL PUBLICACIÓN",   # R  17
    "📈 ALCANCE",               # S  18
    "❤️ ENGAGEMENT",            # T  19
    "# HASHTAGS / KEYWORDS",    # U  20
]

N_COLS     = len(HEADERS)   # 21
COL_TIPO   = 3
COL_PLAT   = 4
COL_ESTADO = 10
COL_PCT    = 12
COL_DRIVE  = 13
COL_ASSETS = 14
COL_ALC    = 18
COL_ENG    = 19

HOOKS_BANK = [
    ["Tu contenido es bueno pero nadie lo ve. El problema no eres tú, es tu estrategia de 2024...",
     "EDU", "Carousel", "Marketing / Agencias", "Alto", "Énfasis en contraste: tú ≠ el problema"],
    ["De 200 views a 15K en 30 días — cómo lo hicimos para [Cliente]",
     "CASE", "Reel", "Cualquier industria", "Muy alto", "Requiere métrica real"],
    ["La gente piensa que la IA reemplaza creativos. Falso.",
     "BTS", "Reel", "Marketing / Creatividad", "Alto", "Hook de opinión contraria"],
    ["Llevás usando 30 hashtags y tu alcance sigue igual.",
     "EDU", "Carousel", "Social Media", "Alto", "Espejo del dolor del usuario"],
    ["Google indexa tus posts. Si no optimizás para SEO, eres invisible.",
     "TREND", "Reel", "Marketing", "Muy alto", "Dato sorpresivo"],
    ["Si tenés menos de 50K, hacé Reels. Si tenés más, carousels.",
     "EDU", "Reel", "Creadores / Agencias", "Alto", "Regla simple y accionable"],
    ["El 80% del alcance se decide en los primeros 3 segundos.",
     "EDU", "Carousel", "Marketing", "Alto", "Estadística + urgencia"],
    ["7 AM: llega el brief. 6 PM: está en el feed del cliente.",
     "BTS", "Reel", "Agencias", "Medio-alto", "Estructura de día en la vida"],
    ["La IA no es una varita mágica. Es una herramienta.",
     "TREND", "Post", "Marketing / IA", "Alto", "Hook de desmitificación"],
    ["¿Qué los está frenando? ¿Tiempo? ¿Ideas? ¿Edición?",
     "COMM", "Stories", "Cualquier industria", "Alto", "Pregunta directa de comunidad"],
    # Templates reutilizables
    ["[Número] errores que [audiencia] comete con [tema]",
     "EDU", "Carousel", "Universal", "Alto", "Template numérico"],
    ["Nadie habla de esto pero [insight sorpresivo]",
     "TREND", "Reel", "Universal", "Muy alto", "Hook de exclusividad"],
    ["Antes: [estado malo]. Después: [estado bueno]. Lo que cambió:",
     "CASE", "Carousel/Reel", "Universal", "Muy alto", "Antes/después"],
    ["[Pregunta que el lector ya se hizo]",
     "COMM", "Post/Stories", "Universal", "Medio", "Mirror hook"],
    ["La mayoría hace [X]. Los que tienen resultados hacen [Y].",
     "EDU", "Carousel", "Universal", "Alto", "Contraste de comportamiento"],
]


# ─── DRIVE HELPERS ───────────────────────────────────────────────────────────

def find_folder(name, parent_id=None):
    q = f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if parent_id:
        q += f" and '{parent_id}' in parents"
    result = drive_svc.files().list(q=q, fields="files(id,webViewLink)", pageSize=1).execute()
    files = result.get("files", [])
    if files:
        return files[0]["id"], files[0]["webViewLink"]
    return None, None


def get_or_create_folder(name, parent_id=None):
    fid, link = find_folder(name, parent_id)
    if fid:
        print(f"  ♻  {name}")
        return fid, link
    metadata = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
    if parent_id:
        metadata["parents"] = [parent_id]
    folder = drive_svc.files().create(body=metadata, fields="id,webViewLink").execute()
    print(f"  📁 {name}")
    return folder["id"], folder["webViewLink"]


# ─── SHEET HELPERS ───────────────────────────────────────────────────────────

def _col(n):
    """0-indexed column number to letter: 0→A, 25→Z, 26→AA, ..."""
    result = ""
    while True:
        result = chr(65 + n % 26) + result
        n = n // 26 - 1
        if n < 0:
            break
    return result


def _build_calendar_rows(posts, semana_labels, post_folders, assets_link):
    rows = []
    for i, post in enumerate(posts):
        r = i + 2  # 1-indexed, row 1 is header
        semana_label = semana_labels[post["semana"]]
        folder_url   = post_folders.get(post["fecha_key"], "")
        pct_formula  = (
            f'=(IF({_col(7)}{r}<>"",1,0)'
            f'+IF({_col(8)}{r}<>"",1,0)'
            f'+IF({_col(9)}{r}<>"",1,0))/3'
        )
        drive_formula  = f'=HYPERLINK("{folder_url}","📁 Abrir")' if folder_url else ""
        assets_formula = f'=HYPERLINK("{assets_link}","🖼 Assets")'
        rows.append([
            post["fecha"],
            post["dia"],
            semana_label,
            post["tipo"],
            post.get("plataforma", "Instagram"),
            post["formato"],
            post["titulo"],
            post["hook"],
            post["script"],
            post["notas"],
            "Pendiente",
            "",             # RESPONSABLE
            pct_formula,    # % COMPLETADO
            drive_formula,  # CARPETA DRIVE
            assets_formula, # ASSETS
            "",             # BORRADOR
            "",             # POST PUBLICADO
            "",             # FECHA REAL
            "",             # ALCANCE
            "",             # ENGAGEMENT
            post["hashtags"],
        ])
    return rows


def _build_metricas_rows(semanas, posts):
    posts_per_week = {}
    for p in posts:
        posts_per_week[p["semana"]] = posts_per_week.get(p["semana"], 0) + 1

    sc = _col(2)   # C — SEMANA|TEMA
    kc = _col(10)  # K — ESTADO
    sc_alc = _col(18)  # S — ALCANCE
    sc_eng = _col(19)  # T — ENGAGEMENT

    rows = []
    for j, (code, tema) in enumerate(semanas.items()):
        r = j + 2
        prefix = f"{code} ·"
        n = posts_per_week.get(code, 0)
        rows.append([
            code, tema, n,
            f'=COUNTIFS(CALENDARIO!{sc}:{sc},"{prefix}*",CALENDARIO!{kc}:{kc},"Publicado")',
            f"=IF(C{r}=0,0,D{r}/C{r})",
            f'=SUMIFS(CALENDARIO!{sc_alc}:{sc_alc},CALENDARIO!{sc}:{sc},"{prefix}*")',
            f'=SUMIFS(CALENDARIO!{sc_eng}:{sc_eng},CALENDARIO!{sc}:{sc},"{prefix}*")',
        ])

    nd = len(rows)
    tr = nd + 2
    rows.append([
        "TOTAL", "",
        f"=SUM(C2:C{nd+1})",
        f"=SUM(D2:D{nd+1})",
        f"=IF(C{tr}=0,0,D{tr}/C{tr})",
        f"=SUM(F2:F{nd+1})",
        f"=SUM(G2:G{nd+1})",
    ])
    return rows


def _format_requests(tab_cal, tab_met, tab_hooks, n_rows, posts):
    reqs = []

    # ── CALENDARIO ────────────────────────────────────────────────────────────

    # Freeze header row + cols A-B
    reqs.append({"updateSheetProperties": {
        "properties": {
            "sheetId": tab_cal,
            "gridProperties": {"frozenRowCount": 1, "frozenColumnCount": 2},
        },
        "fields": "gridProperties.frozenRowCount,gridProperties.frozenColumnCount",
    }})

    # Header: black bg, amber text
    reqs.append({"repeatCell": {
        "range": {"sheetId": tab_cal, "startRowIndex": 0, "endRowIndex": 1,
                  "startColumnIndex": 0, "endColumnIndex": N_COLS},
        "cell": {"userEnteredFormat": {
            "backgroundColor": BLACK,
            "textFormat": {"foregroundColor": AMBER, "bold": True,
                           "fontSize": 10, "fontFamily": "Arial"},
            "horizontalAlignment": "CENTER",
            "verticalAlignment": "MIDDLE",
            "wrapStrategy": "WRAP",
        }},
        "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment,wrapStrategy)",
    }})

    # Data rows: bone bg, black text
    reqs.append({"repeatCell": {
        "range": {"sheetId": tab_cal, "startRowIndex": 1, "endRowIndex": 1 + n_rows,
                  "startColumnIndex": 0, "endColumnIndex": N_COLS},
        "cell": {"userEnteredFormat": {
            "backgroundColor": BONE,
            "textFormat": {"foregroundColor": BLACK, "fontSize": 10, "fontFamily": "Arial"},
            "verticalAlignment": "TOP",
            "wrapStrategy": "WRAP",
        }},
        "fields": "userEnteredFormat(backgroundColor,textFormat,verticalAlignment,wrapStrategy)",
    }})

    # FECHA column: bold, centered
    reqs.append({"repeatCell": {
        "range": {"sheetId": tab_cal, "startRowIndex": 1, "endRowIndex": 1 + n_rows,
                  "startColumnIndex": 0, "endColumnIndex": 1},
        "cell": {"userEnteredFormat": {
            "textFormat": {"bold": True, "fontSize": 11},
            "horizontalAlignment": "CENTER",
        }},
        "fields": "userEnteredFormat(textFormat,horizontalAlignment)",
    }})

    # TIPO: color per row
    for i, post in enumerate(posts):
        c = TIPO_COLORS.get(post["tipo"], {"bg": LGRAY, "fg": BLACK})
        reqs.append({"repeatCell": {
            "range": {"sheetId": tab_cal,
                      "startRowIndex": i + 1, "endRowIndex": i + 2,
                      "startColumnIndex": COL_TIPO, "endColumnIndex": COL_TIPO + 1},
            "cell": {"userEnteredFormat": {
                "backgroundColor": c["bg"],
                "textFormat": {"foregroundColor": c["fg"], "bold": True, "fontSize": 10},
                "horizontalAlignment": "CENTER",
            }},
            "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)",
        }})

    # ESTADO dropdown
    reqs.append({"setDataValidation": {
        "range": {"sheetId": tab_cal, "startRowIndex": 1, "endRowIndex": 1 + n_rows,
                  "startColumnIndex": COL_ESTADO, "endColumnIndex": COL_ESTADO + 1},
        "rule": {
            "condition": {
                "type": "ONE_OF_LIST",
                "values": [{"userEnteredValue": s} for s in ESTADO_OPTS],
            },
            "showCustomUi": True,
            "strict": True,
        },
    }})

    # PLATAFORMA dropdown
    reqs.append({"setDataValidation": {
        "range": {"sheetId": tab_cal, "startRowIndex": 1, "endRowIndex": 1 + n_rows,
                  "startColumnIndex": COL_PLAT, "endColumnIndex": COL_PLAT + 1},
        "rule": {
            "condition": {
                "type": "ONE_OF_LIST",
                "values": [{"userEnteredValue": p} for p in PLATAFORMA_OPTS],
            },
            "showCustomUi": True,
            "strict": False,
        },
    }})

    # ESTADO conditional colors
    for estado, color in ESTADO_COLORS.items():
        reqs.append({"addConditionalFormatRule": {
            "rule": {
                "ranges": [{"sheetId": tab_cal, "startRowIndex": 1, "endRowIndex": 1 + n_rows,
                            "startColumnIndex": COL_ESTADO, "endColumnIndex": COL_ESTADO + 1}],
                "booleanRule": {
                    "condition": {"type": "TEXT_EQ", "values": [{"userEnteredValue": estado}]},
                    "format": {"backgroundColor": color},
                },
            },
            "index": 0,
        }})

    # % COMPLETADO: percentage format + gradient color
    reqs.append({"repeatCell": {
        "range": {"sheetId": tab_cal, "startRowIndex": 1, "endRowIndex": 1 + n_rows,
                  "startColumnIndex": COL_PCT, "endColumnIndex": COL_PCT + 1},
        "cell": {"userEnteredFormat": {
            "numberFormat": {"type": "PERCENT", "pattern": "0%"},
            "horizontalAlignment": "CENTER",
            "textFormat": {"bold": True},
        }},
        "fields": "userEnteredFormat(numberFormat,horizontalAlignment,textFormat)",
    }})
    reqs.append({"addConditionalFormatRule": {
        "rule": {
            "ranges": [{"sheetId": tab_cal, "startRowIndex": 1, "endRowIndex": 1 + n_rows,
                        "startColumnIndex": COL_PCT, "endColumnIndex": COL_PCT + 1}],
            "gradientRule": {
                "minpoint": {"color": {"red": 1.0, "green": 0.8, "blue": 0.8},
                             "type": "MIN"},
                "midpoint": {"color": {"red": 1.0, "green": 1.0, "blue": 0.6},
                             "type": "PERCENTILE", "value": "50"},
                "maxpoint": {"color": {"red": 0.6, "green": 0.9, "blue": 0.6},
                             "type": "MAX"},
            },
        },
        "index": 0,
    }})

    # ALCANCE + ENGAGEMENT: green tint, centered, bold
    reqs.append({"repeatCell": {
        "range": {"sheetId": tab_cal, "startRowIndex": 1, "endRowIndex": 1 + n_rows,
                  "startColumnIndex": COL_ALC, "endColumnIndex": COL_ENG + 1},
        "cell": {"userEnteredFormat": {
            "backgroundColor": {"red": 0.93, "green": 0.97, "blue": 0.93},
            "horizontalAlignment": "CENTER",
            "textFormat": {"bold": True},
        }},
        "fields": "userEnteredFormat(backgroundColor,horizontalAlignment,textFormat)",
    }})

    # Column widths
    for i, w in enumerate([
        70,   # FECHA
        80,   # DÍA
        150,  # SEMANA
        70,   # TIPO
        110,  # PLATAFORMA
        90,   # FORMATO
        260,  # TÍTULO
        260,  # HOOK
        280,  # SCRIPT
        220,  # NOTAS
        110,  # ESTADO
        120,  # RESPONSABLE
        95,   # % COMPLETADO
        90,   # CARPETA DRIVE
        80,   # ASSETS
        90,   # BORRADOR
        90,   # POST PUBLICADO
        130,  # FECHA REAL
        80,   # ALCANCE
        90,   # ENGAGEMENT
        200,  # HASHTAGS
    ]):
        reqs.append({"updateDimensionProperties": {
            "range": {"sheetId": tab_cal, "dimension": "COLUMNS",
                      "startIndex": i, "endIndex": i + 1},
            "properties": {"pixelSize": w},
            "fields": "pixelSize",
        }})

    # Row heights
    reqs.append({"updateDimensionProperties": {
        "range": {"sheetId": tab_cal, "dimension": "ROWS",
                  "startIndex": 1, "endIndex": 1 + n_rows},
        "properties": {"pixelSize": 80},
        "fields": "pixelSize",
    }})

    # Borders
    reqs.append({"updateBorders": {
        "range": {"sheetId": tab_cal, "startRowIndex": 0, "endRowIndex": 1 + n_rows,
                  "startColumnIndex": 0, "endColumnIndex": N_COLS},
        "top":             {"style": "SOLID_THICK", "color": BLACK},
        "bottom":          {"style": "SOLID_THICK", "color": BLACK},
        "left":            {"style": "SOLID_THICK", "color": BLACK},
        "right":           {"style": "SOLID_THICK", "color": BLACK},
        "innerHorizontal": {"style": "SOLID",       "color": MGRAY},
        "innerVertical":   {"style": "SOLID",       "color": MGRAY},
    }})

    # ── MÉTRICAS ──────────────────────────────────────────────────────────────
    reqs.append({"repeatCell": {
        "range": {"sheetId": tab_met, "startRowIndex": 0, "endRowIndex": 1,
                  "startColumnIndex": 0, "endColumnIndex": 7},
        "cell": {"userEnteredFormat": {
            "backgroundColor": BLACK,
            "textFormat": {"foregroundColor": LIME, "bold": True, "fontSize": 10},
            "horizontalAlignment": "CENTER",
            "wrapStrategy": "WRAP",
        }},
        "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,wrapStrategy)",
    }})
    # % CUMPLIMIENTO column (E, index 4) as percentage
    reqs.append({"repeatCell": {
        "range": {"sheetId": tab_met, "startRowIndex": 1, "endRowIndex": 7,
                  "startColumnIndex": 4, "endColumnIndex": 5},
        "cell": {"userEnteredFormat": {
            "numberFormat": {"type": "PERCENT", "pattern": "0%"},
            "horizontalAlignment": "CENTER",
        }},
        "fields": "userEnteredFormat(numberFormat,horizontalAlignment)",
    }})
    # TOTAL row: black bg, white text
    reqs.append({"repeatCell": {
        "range": {"sheetId": tab_met, "startRowIndex": 6, "endRowIndex": 7,
                  "startColumnIndex": 0, "endColumnIndex": 7},
        "cell": {"userEnteredFormat": {
            "backgroundColor": BLACK,
            "textFormat": {"foregroundColor": WHITE, "bold": True},
        }},
        "fields": "userEnteredFormat(backgroundColor,textFormat)",
    }})

    # ── BANCO DE HOOKS ────────────────────────────────────────────────────────
    reqs.append({"repeatCell": {
        "range": {"sheetId": tab_hooks, "startRowIndex": 0, "endRowIndex": 1,
                  "startColumnIndex": 0, "endColumnIndex": 6},
        "cell": {"userEnteredFormat": {
            "backgroundColor": BLACK,
            "textFormat": {"foregroundColor": AMBER, "bold": True, "fontSize": 10},
            "horizontalAlignment": "CENTER",
        }},
        "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)",
    }})
    # Hook column wide
    reqs.append({"updateDimensionProperties": {
        "range": {"sheetId": tab_hooks, "dimension": "COLUMNS",
                  "startIndex": 0, "endIndex": 1},
        "properties": {"pixelSize": 380},
        "fields": "pixelSize",
    }})
    # TIPO color per row in hooks
    for i, hook_row in enumerate(HOOKS_BANK):
        c = TIPO_COLORS.get(hook_row[1], {"bg": LGRAY, "fg": BLACK})
        reqs.append({"repeatCell": {
            "range": {"sheetId": tab_hooks,
                      "startRowIndex": i + 1, "endRowIndex": i + 2,
                      "startColumnIndex": 1, "endColumnIndex": 2},
            "cell": {"userEnteredFormat": {
                "backgroundColor": c["bg"],
                "textFormat": {"foregroundColor": c["fg"], "bold": True},
                "horizontalAlignment": "CENTER",
            }},
            "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)",
        }})

    return reqs


# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Setup mensual EVRYWR.MEDIA")
    parser.add_argument("--mes", required=True,
                        help="Nombre del módulo en calendar_config/ (ej: marzo_2026)")
    args = parser.parse_args()

    try:
        cfg = importlib.import_module(f"calendar_config.{args.mes}")
    except ModuleNotFoundError:
        print(f"\nERROR: calendar_config/{args.mes}.py no encontrado.")
        print("Crea el archivo con MES, SEMANAS y POSTS definidos.\n")
        return

    mes_name = cfg.MES
    semanas  = cfg.SEMANAS
    posts    = cfg.POSTS
    clientes = getattr(cfg, "CLIENTES", [])

    print(f"\n=== EVRYWR.MEDIA — Setup {mes_name} ===\n")

    # ── Drive: estructura raíz ────────────────────────────────────────────────
    print("Drive — carpetas raíz:")
    evrywr_id,   evrywr_link  = get_or_create_folder("EVRYWR")
    archivo_id,  _            = get_or_create_folder("ARCHIVO",   evrywr_id)
    assets_id,   assets_link  = get_or_create_folder("ASSETS",    evrywr_id)
    for sub in ["B-Roll", "Templates Graficos", "Brand Guidelines", "Musica y Audio", "Fotos Equipo"]:
        get_or_create_folder(sub, assets_id)
    clientes_id, _ = get_or_create_folder("CLIENTES",   evrywr_id)
    for c in clientes:
        get_or_create_folder(c, clientes_id)
    refs_id,     _ = get_or_create_folder("REFERENCIAS", evrywr_id)
    for sub in ["Inspiracion Visual", "Competencia", "Benchmarks y Data", "Guiones de Referencia"]:
        get_or_create_folder(sub, refs_id)

    # ── Drive: mes y posts ────────────────────────────────────────────────────
    print(f"\nDrive — {mes_name}:")
    mes_id, _ = get_or_create_folder(mes_name, evrywr_id)
    week_ids = {}
    for code, tema in semanas.items():
        wid, _ = get_or_create_folder(f"{code} - {tema}", mes_id)
        week_ids[code] = wid
    post_folders = {}
    for post in posts:
        folder_name = f"{post['fecha_key']} - {post['tipo']} - {post['titulo_corto']}"
        _, link = get_or_create_folder(folder_name, week_ids[post["semana"]])
        post_folders[post["fecha_key"]] = link

    # ── Sheet ─────────────────────────────────────────────────────────────────
    print(f"\nSheet — creando...")
    semana_labels = {code: f"{code} · {tema}" for code, tema in semanas.items()}

    sp = sheets_svc.spreadsheets().create(
        body={
            "properties": {"title": f"EVRYWR.MEDIA — Calendario Editorial {mes_name}"},
            "sheets": [
                {"properties": {"title": "CALENDARIO",    "index": 0}},
                {"properties": {"title": "MÉTRICAS",      "index": 1}},
                {"properties": {"title": "BANCO DE HOOKS","index": 2}},
            ],
        },
        fields="spreadsheetId,spreadsheetUrl,sheets.properties",
    ).execute()

    sheet_id  = sp["spreadsheetId"]
    sheet_url = sp["spreadsheetUrl"]
    tab_cal   = sp["sheets"][0]["properties"]["sheetId"]
    tab_met   = sp["sheets"][1]["properties"]["sheetId"]
    tab_hooks = sp["sheets"][2]["properties"]["sheetId"]

    # Write CALENDARIO
    cal_rows = _build_calendar_rows(posts, semana_labels, post_folders, assets_link)
    sheets_svc.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range="CALENDARIO!A1",
        valueInputOption="USER_ENTERED",
        body={"values": [HEADERS] + cal_rows},
    ).execute()
    print(f"  ✏  CALENDARIO — {len(cal_rows)} posts")

    # Write MÉTRICAS
    met_headers = ["SEMANA", "TEMA", "PLANIFICADOS", "PUBLICADOS",
                   "% CUMPLIMIENTO", "ALCANCE TOTAL", "ENGAGEMENT TOTAL"]
    met_rows = _build_metricas_rows(semanas, posts)
    sheets_svc.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range="MÉTRICAS!A1",
        valueInputOption="USER_ENTERED",
        body={"values": [met_headers] + met_rows},
    ).execute()
    print(f"  ✏  MÉTRICAS — {len(met_rows)-1} semanas + total")

    # Write BANCO DE HOOKS
    hook_headers = ["HOOK", "TIPO", "FORMATO RECOMENDADO",
                    "INDUSTRIA", "RESULTADO ESTIMADO", "NOTAS / VARIACIONES"]
    sheets_svc.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range="BANCO DE HOOKS!A1",
        valueInputOption="USER_ENTERED",
        body={"values": [hook_headers] + HOOKS_BANK},
    ).execute()
    print(f"  ✏  BANCO DE HOOKS — {len(HOOKS_BANK)} hooks")

    # Apply all formatting
    reqs = _format_requests(tab_cal, tab_met, tab_hooks, len(cal_rows), posts)
    sheets_svc.spreadsheets().batchUpdate(
        spreadsheetId=sheet_id,
        body={"requests": reqs},
    ).execute()
    print("  🎨 Formato aplicado")

    # Move sheet into EVRYWR folder
    drive_svc.files().update(
        fileId=sheet_id,
        addParents=evrywr_id,
        fields="id,parents",
    ).execute()
    print("  📂 Sheet movido a carpeta EVRYWR")

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║  SETUP COMPLETO — {mes_name:<42}║
╠══════════════════════════════════════════════════════════════╣
║  Carpeta EVRYWR:                                             ║
║  {evrywr_link:<60}║
║                                                              ║
║  Google Sheet:                                               ║
║  {sheet_url:<60}║
╚══════════════════════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    main()
