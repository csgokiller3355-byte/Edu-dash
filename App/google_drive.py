import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from django.conf import settings
SERVICE_ACCOUNT_FILE = settings.BASE_DIR / 'edudash-512314-7fa862deef3b.json'
# Настройки (их можно вынести в settings.py)
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = settings.BASE_DIR / 'credentials.json'  # Путь к вашему скачанному JSON-файлу
PARENT_FOLDER_ID = '1Rk_nPmaUz-VtEB1cbDnZ0-d4KCDEZz-u'  # ID вашей папки


def get_drive_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build('drive', 'v3', credentials=creds)


def upload_file_to_drive(file_obj, filename, mime_type=None):
    """
    Загружает файл на Google Диск.
    file_obj: файл из запроса (например, request.FILES['pdf'])
    Возвращает словарь с id и веб-ссылкой на файл.
    """
    service = get_drive_service()

    file_metadata = {
        'name': filename,
        'parents': [PARENT_FOLDER_ID]
    }

    # Читаем байты из django UploadedFile
    media = MediaIoBaseUpload(
        io.BytesIO(file_obj.read()),
        mimetype=mime_type or 'application/octet-stream',
        resumable=True
    )

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink, webContentLink'
    ).execute()

    return file