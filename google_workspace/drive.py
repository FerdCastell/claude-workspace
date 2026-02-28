import io
import os
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from .auth import get_service


class Drive:
    def __init__(self):
        self.service = get_service("drive", "v3")

    def list_files(self, folder_id=None, max_results=20):
        query = f"'{folder_id}' in parents" if folder_id else None
        params = {
            "pageSize": max_results,
            "fields": "files(id, name, mimeType, size, modifiedTime, webViewLink)",
        }
        if query:
            params["q"] = query
        result = self.service.files().list(**params).execute()
        return result.get("files", [])

    def upload_file(self, local_path, folder_id=None, mime_type=None):
        name = os.path.basename(local_path)
        metadata = {"name": name}
        if folder_id:
            metadata["parents"] = [folder_id]
        media = MediaFileUpload(local_path, mimetype=mime_type, resumable=True)
        file = (
            self.service.files()
            .create(body=metadata, media_body=media, fields="id, name, webViewLink")
            .execute()
        )
        return file

    def download_file(self, file_id, dest_path):
        request = self.service.files().get_media(fileId=file_id)
        os.makedirs(os.path.dirname(dest_path) or ".", exist_ok=True)
        with open(dest_path, "wb") as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()
        return dest_path

    def create_folder(self, name, parent_id=None):
        metadata = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
        }
        if parent_id:
            metadata["parents"] = [parent_id]
        folder = (
            self.service.files()
            .create(body=metadata, fields="id, name, webViewLink")
            .execute()
        )
        return folder

    def delete_file(self, file_id):
        self.service.files().delete(fileId=file_id).execute()

    def search(self, query, max_results=20):
        result = (
            self.service.files()
            .list(
                q=query,
                pageSize=max_results,
                fields="files(id, name, mimeType, modifiedTime, webViewLink)",
            )
            .execute()
        )
        return result.get("files", [])
