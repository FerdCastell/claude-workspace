from .auth import get_service


class Docs:
    def __init__(self):
        self.service = get_service("docs", "v1")

    def create(self, title):
        doc = self.service.documents().create(body={"title": title}).execute()
        return doc

    def get(self, document_id):
        return self.service.documents().get(documentId=document_id).execute()

    def read_text(self, document_id):
        doc = self.get(document_id)
        text = []
        for element in doc.get("body", {}).get("content", []):
            paragraph = element.get("paragraph")
            if paragraph:
                for run in paragraph.get("elements", []):
                    text_run = run.get("textRun")
                    if text_run:
                        text.append(text_run.get("content", ""))
        return "".join(text)

    def append_text(self, document_id, text):
        doc = self.get(document_id)
        end_index = doc["body"]["content"][-1]["endIndex"] - 1
        requests = [
            {
                "insertText": {
                    "location": {"index": end_index},
                    "text": text,
                }
            }
        ]
        result = (
            self.service.documents()
            .batchUpdate(documentId=document_id, body={"requests": requests})
            .execute()
        )
        return result

    def replace_text(self, document_id, find, replace):
        requests = [
            {
                "replaceAllText": {
                    "containsText": {"text": find, "matchCase": True},
                    "replaceText": replace,
                }
            }
        ]
        result = (
            self.service.documents()
            .batchUpdate(documentId=document_id, body={"requests": requests})
            .execute()
        )
        return result
