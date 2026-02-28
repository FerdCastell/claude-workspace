from .auth import get_service


class Sheets:
    def __init__(self):
        self.service = get_service("sheets", "v4")

    def create(self, title):
        spreadsheet = (
            self.service.spreadsheets()
            .create(body={"properties": {"title": title}}, fields="spreadsheetId,spreadsheetUrl")
            .execute()
        )
        return spreadsheet

    def read(self, spreadsheet_id, range_):
        result = (
            self.service.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=range_)
            .execute()
        )
        return result.get("values", [])

    def write(self, spreadsheet_id, range_, values):
        body = {"values": values}
        result = (
            self.service.spreadsheets()
            .values()
            .update(
                spreadsheetId=spreadsheet_id,
                range=range_,
                valueInputOption="USER_ENTERED",
                body=body,
            )
            .execute()
        )
        return result

    def append(self, spreadsheet_id, range_, values):
        body = {"values": values}
        result = (
            self.service.spreadsheets()
            .values()
            .append(
                spreadsheetId=spreadsheet_id,
                range=range_,
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body=body,
            )
            .execute()
        )
        return result

    def clear(self, spreadsheet_id, range_):
        result = (
            self.service.spreadsheets()
            .values()
            .clear(spreadsheetId=spreadsheet_id, range=range_, body={})
            .execute()
        )
        return result

    def get_info(self, spreadsheet_id):
        result = (
            self.service.spreadsheets()
            .get(spreadsheetId=spreadsheet_id, fields="spreadsheetId,spreadsheetUrl,properties,sheets.properties")
            .execute()
        )
        return result
