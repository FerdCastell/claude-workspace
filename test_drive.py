from google_workspace import Drive, Docs
from google_workspace.auth import get_service

drive = Drive()
docs = Docs()

folder = drive.create_folder("claude")
print("Carpeta creada:", folder["name"], "-", folder["webViewLink"])

doc = docs.create("Hola")
doc_id = doc["documentId"]

service = get_service("drive", "v3")
service.files().update(fileId=doc_id, addParents=folder["id"], fields="id").execute()

docs.append_text(doc_id, "hola")
print("Documento:", "https://docs.google.com/document/d/" + doc_id)
