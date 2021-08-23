import os.path
import sys
import errno
import io

# pip install google-api-python-client
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from google_auth_oauthlib.flow import InstalledAppFlow

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive.readonly']

def main():

    if len(sys.argv) <= 3:
        print("Usage: python list.py [driveId] [folder name] [dist folder]")
        return

    drive_id = sys.argv[1]
    target_folder_name = sys.argv[2]
    download_folder_name = sys.argv[3]
    
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
        # # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('drive', 'v3', credentials=creds)

    res = service.files().list(
        corpora="drive", 
        driveId=drive_id,
        includeItemsFromAllDrives=False,
        includeTeamDriveItems=True,
        supportsAllDrives=True,
        supportsTeamDrives=True,
        fields="files(id, name, parents)",
        q="mimeType = 'application/vnd.google-apps.folder' and trashed = false").execute()
    
    targets = {}

    print("All Folders:")

    for folder in res['files']:
        print(f"  {folder['name']}")
        if (target_folder_name in folder['name']):
            targets[folder['id']] = None

    if len(targets) > 1:
        print(f"Found multiple folder with name {target_folder_name}: {[t for t in targets]}")
        return
    if not len(targets):
        print(f"Can not find folder with name \"{target_folder_name or 'none'}\"")
        return

    for _ in range(10):
        for folder in res['files']:
            for parent in folder["parents"]:
                if parent in targets and folder["id"] not in targets:
                    print(f"Added subfolder '{folder['name']}'")
                    targets[folder["id"]] = { "parent": parent, "name": folder["name"] }

    def get_path(f, name):
        if f in targets:
            if targets[f] is None:
                return name
            else:
                return get_path(targets[f]["parent"], f"{targets[f]['name']}/{name}")
        else:
            return name

    res = service.files().list(
        corpora="drive",
        driveId=drive_id,
        includeItemsFromAllDrives=False,
        includeTeamDriveItems=True,
        supportsAllDrives=True,
        supportsTeamDrives=True,
        fields="files(id, name, parents)",
        q="mimeType != 'application/vnd.google-apps.folder' and trashed = false").execute()

    print("Files")
    download = {}

    for file in res['files']:
        if sum([p in targets for p in file['parents']]):

            if file["name"] in download:
                print(f"Duplicate file: {file['name']}")
                continue
            download[file["name"]] = file

            file['path'] = get_path(file["parents"][0], file["name"])
            print(f"File: {file['path']}")

    files_service = service.files()

    for file in download.values():

        filename = download_folder_name + "/" + file['path']

        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        fh = io.FileIO(filename, mode="wb")
        req = files_service.get_media(fileId = file["id"])
        req.uri = req.uri.replace('alt=json', 'alt=media')
        downloader = MediaIoBaseDownload(fh, req, chunksize = 16 * 1024 * 1024)

        done = False
        while done is False:
            status, done = downloader.next_chunk()
            if status:
                print(f"Downloading {file['name']} {int(status.progress() * 100)}%")

if __name__ == '__main__':
    main()