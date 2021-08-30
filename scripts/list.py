import io
import sys
import errno
from os import system
import os.path
import argparse

# pip install google-api-python-client google_auth_oauthlib

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive.readonly']

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--verbose", help="Increase output verbosity", action="store_true")
    parser.add_argument("--hide-pg", help="Hide progress bar", action="store_true")

    # Drive ID and dist folder
    parser.add_argument('--drive', required=True, help="Drive ID (token at the end of the URL at root level in the drive)")
    parser.add_argument('--dist', required=True, help="Dist folder")

    # Need folder name OR id to find
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--folder-name', help="Folder name. If multiple folder matches, download will not start.")
    group.add_argument('--folder-id', help="Folder ID (token at the end of the URL")

    args = parser.parse_args()

    verbose = args.verbose
    hide_progress = args.hide_pg

    drive_id = args.drive
    dist_folder_name = args.dist

    target_folder_id = args.folder_id
    target_folder_name = args.folder_name
    
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
            if not os.path.exists('credentials.json'):
                print('"credentials.json" missing')
                return
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    file_service = build('drive', 'v3', credentials=creds).files()

    # Fetch all the folders in the drive
    res = file_service.list(
        corpora="drive", 
        driveId=drive_id,
        includeItemsFromAllDrives=False,
        includeTeamDriveItems=True,
        supportsAllDrives=True,
        supportsTeamDrives=True,
        fields="files(id, name, parents)",
        q="mimeType = 'application/vnd.google-apps.folder' and trashed = false").execute()
    
    targets = {}
    dup = set()
    target_key = "id" if target_folder_id else "name"
    target_folder = target_folder_id if target_folder_id else target_folder_name

    print(f"{colors.OKCYAN}Searching for folder.{target_key} = \"{target_folder}\" in {str(len(res['files']))} folders {colors.ENDC}")

    # Find the folder
    for folder in res['files']:
        if verbose:
            print(f"  {colors.WARNING}{folder['id']}{colors.ENDC} {colors.UNDERLINE}{folder['name']}{colors.ENDC}")
        if (target_folder in folder[target_key]):
            targets[folder['id']] = None
            dup.add(folder[target_key])

    # Duplicates
    if len(targets) > 1:
        print(f"{colors.FAIL}Found multiple folder with {target_key} \"{target_folder}\":\
            {colors.ENDC} \n  {colors.WARNING}" + '\n  '.join(dup) + colors.ENDC)
        return

    # Not found
    if not len(targets):
        print(f"{colors.FAIL}Can not find folder with {target_key} \"{target_folder}\"{colors.ENDC}")
        return

    # Build folder tree since google doesn't include path
    for _ in range(10):
        for folder in res['files']:
            for parent in folder["parents"]:
                if parent in targets and folder["id"] not in targets:
                    print(f"{colors.OKGREEN} Added subfolder{colors.ENDC} {colors.UNDERLINE}{folder['name']}{colors.ENDC}")
                    targets[folder["id"]] = { "parent": parent, "name": folder["name"] }

    # Helper function to build the path to a file
    def build_path(f, name):
        if f in targets:
            if targets[f] is None:
                return name
            else:
                return build_path(targets[f]["parent"], f"{targets[f]['name']}/{name}")
        else:
            return name

    # Fetch all the files in the drive
    res = file_service.list(
        corpora="drive",
        driveId=drive_id,
        includeItemsFromAllDrives=False,
        includeTeamDriveItems=True,
        supportsAllDrives=True,
        supportsTeamDrives=True,
        fields="files(id, name, parents)",
        q="mimeType != 'application/vnd.google-apps.folder' and trashed = false").execute()

    # Build download path
    download = {}
    for file in res['files']:
        if sum([p in targets for p in file['parents']]):

            if file["name"] in download:
                print(f"Duplicate file: {file['name']}")
                continue
            download[file["name"]] = file

            file['path'] = build_path(file["parents"][0], file["name"])
            if verbose:
                print(f"Download queued: {file['path']}")

    print(f"{colors.OKCYAN}Queued {len(download)} files to download{colors.ENDC}")

    # Download files
    for file in download.values():

        filename = dist_folder_name + "/" + file['path']

        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        fh = io.FileIO(filename, mode="wb")
        req = file_service.get_media(fileId = file["id"])
        req.uri = req.uri.replace('alt=json', 'alt=media')

        # 16 MB chunk size
        downloader = MediaIoBaseDownload(fh, req, chunksize = 16 * 1024 * 1024)

        pg_bar_width = 25
        pg = 0

        def print_progress(name, done = False):
            if hide_progress:
                if done:
                    sys.stderr.write(f'\r{colors.OKGREEN}Downloaded{colors.ENDC} {colors.UNDERLINE}{name}{colors.ENDC}')
                return

            p1 = '=' * pg
            p2 = ' ' * max((pg_bar_width - pg - 1), 0)
            perc = str(round(status.progress() * 100)).rjust(3)
            if not done:
                sys.stderr.write(f'\r{colors.OKCYAN}[{p1}>{p2}] {perc}% Downloaded{colors.ENDC} {colors.UNDERLINE}{name}{colors.ENDC}')
            else:
                sys.stderr.write(f'\r{colors.OKGREEN}[{"=" * pg_bar_width}] {perc}% Downloaded{colors.ENDC} {colors.UNDERLINE}{name}{colors.ENDC}')

        # Download this file
        done = False
        while done is False:
            status, done = downloader.next_chunk()

            if status:
                if status.progress() > pg / pg_bar_width:
                    pg = round(status.progress() * pg_bar_width)
                    print_progress(file['path'])
            if done:
                pg = pg_bar_width
                print_progress(file['path'], True)
                sys.stderr.write("\n")

class colors:
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    UNDERLINE = '\033[4m'

if __name__ == '__main__':

    if not sys.stdout.isatty() or not sys.stderr.isatty():
        colors.OKCYAN = ''
        colors.OKGREEN = ''
        colors.WARNING = ''
        colors.FAIL = ''
        colors.ENDC = ''
        colors.UNDERLINE = ''
    else:
        system("color")

    main()