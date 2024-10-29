from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Path to your service account key file (downloaded from Google Cloud Console)
SERVICE_ACCOUNT_FILE = 'publicmartdrive-31029d6358cd.json'

# Scopes needed for Google Drive API operations
SCOPES = ['https://www.googleapis.com/auth/drive']

def share_file_with_user(file_id, email):
    """Shares a Google Drive file or folder with a user, granting read-only access."""
    try:
        # Authenticate using service account credentials
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        
        # Build the Google Drive service
        service = build('drive', 'v3', credentials=credentials)

        # Define the permission
        permission = {
            'type': 'user',  # Sharing with a specific user
            'role': 'reader',  # Read-only access
            'emailAddress': email  # Email of the user you are sharing with
        }

        # Call the Drive API to share the file
        service.permissions().create(
            fileId=file_id,
            body=permission,
            fields='id'
        ).execute()

        print(f"File {file_id} shared with {email} successfully.")

    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

if __name__ == '__main__':
    # Google Drive file or folder ID
    file_id = '1CG7PHFeB6'

    # Email of the user you want to share the file with
    user_email = 's.r.vitkar55@gmail.com'

    # Call the function to share the file
    share_file_with_user(file_id, user_email)