import sys
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
]

flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
flow.redirect_uri = "http://localhost"

auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")
print("\n=== PASO 1: Abre este link en tu navegador ===")
print(auth_url)
print("\n=== PASO 2: Autoriza y copia la URL completa a la que te redirige ===")
print("(La URL empieza con http://localhost/?code=...)\n")

if len(sys.argv) > 1:
    redirect_url = sys.argv[1]
    from urllib.parse import urlparse, parse_qs
    params = parse_qs(urlparse(redirect_url).query)
    code = params.get("code", [None])[0]
    if not code:
        print("No se encontro el codigo en la URL.")
        sys.exit(1)
    flow.fetch_token(code=code)
    creds = flow.credentials
    with open("token.json", "w") as f:
        f.write(creds.to_json())
    print("token.json creado. Autenticacion completa.")
