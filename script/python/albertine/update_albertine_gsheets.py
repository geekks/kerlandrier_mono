import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_FILE = "association-concarneau-699ee78dcdfa.json"
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)
print(client)
# SPREADSHEET_ID = "1zIf5KOHUAd2ZereswDAfeRbCPNx3EZO4"  # Albertine original
SPREADSHEET_ID = "1JX5V88_jNbe3gjJ3pm1PWHycT8JAscaYdVQs4s1UL6I"  # Cousin copy

# List client authorizations
authorized_user = creds.service_account_email
print(f"Authorized user: {authorized_user}")


sheet = client.open_by_key(SPREADSHEET_ID)
# Get the first worksheet
worksheet = sheet.get_worksheet(0)

# Fetch all data from the worksheet
data = worksheet.get_all_records()

# Print the data
print(data)