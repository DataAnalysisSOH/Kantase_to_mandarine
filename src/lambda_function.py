import base64
import boto3
import cgi
import json
import gspread
import re

from bs4 import BeautifulSoup
from oauth2client.service_account import ServiceAccountCredentials
from urllib.parse import unquote


APP_NAME = 'Mandarin Cantonese Translator'
GOOGLE_SERVICE_ACCOUNT_SECRET_NAME = 'dev/ygtq/mandarin_cantonese_translator'
GOOGLE_SPREAD_SHEET_URL = 'https://docs.google.com/spreadsheets/d/1CxDhoWYiTjSeOXMotycxmltDYxbafflghAEM6En0K9g/edit?gid=0#gid=0'
GOOGLE_SHEET_NAME = 'Mappings'
IS_DEBUGGING = True


def extract_spreadsheet_id(url):
    """
    Extracts the Google Spreadsheet ID from a given URL.

    :param url: The full Google Sheets URL.
    :return: The Spreadsheet ID as a string, or None if not found.
    """
    # Regular expression to match the Spreadsheet ID in the URL
    match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
    
    if match:
        return match.group(1)
    else:
        return None
    

def HTMLEntitiesToUnicode(html_string):
    """Converts HTML entities to unicode.  For example '&amp;' becomes '&'."""
    # Parse the HTML string with BeautifulSoup
    soup = BeautifulSoup(html_string, "html.parser")
    # Convert to a Unicode string
    unicode_string = soup.get_text()
    return unicode_string


def lambda_handler(event, context):
    print (f"{APP_NAME} starts ...")

    if IS_DEBUGGING:
        print(f"Event: {event}")
        
    # Create a Secrets Manager client
    secrets_client = boto3.client('secretsmanager')
    # Retrieve the secret
    response = secrets_client.get_secret_value(SecretId=GOOGLE_SERVICE_ACCOUNT_SECRET_NAME)
    # Parse the secret's value as JSON
    service_account_secret = json.loads(response['SecretString'])
    
    # Use the credentials to access the Google Sheets API
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_secret, scope)
    gspread_client = gspread.authorize(creds)

    http_method = event['requestContext']['http']['method']
    
    # 1. Make sure we get the HTTP method used by the requester
    print(f"HTTP method: {http_method}")
    
    if http_method == 'GET':
        # Return the HTML form
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{APP_NAME}</title>
        </head>
        <body>
            <h1>{APP_NAME}</h1>
            <form action="/mandarin-cantonese-translator" method="post">
                <textarea name="input_text" rows="20" cols="60"></textarea><br><br>
                <input type="submit" value="Convert">
            </form>
        </body>
        </html>
        """
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html'
            },
            'body': html_content
        }
        
    elif http_method == 'POST':
        event_body = event['body']
        
        if IS_DEBUGGING:
            print(f"Original event body: {event_body}")
        
        # Check if the body is base64 encoded
        if event.get('isBase64Encoded', False):
            # Decode the base64-encoded body
            decoded_body = base64.b64decode(event_body).decode('utf-8')
        else:
            decoded_body = event['body']
        
        if IS_DEBUGGING:
            print(f"Decoded request body: {decoded_body}")
        
        parsed_body = unquote(decoded_body)
        if IS_DEBUGGING:
            print(f"Parsed request body: {parsed_body}")
        
        unicode_body = HTMLEntitiesToUnicode(parsed_body)
        if IS_DEBUGGING:
            print(f"Unicoded request body: {unicode_body}")

        # Split request payload body using '=' because form values 
        # comes in as pairs and each pair is connected by '='
        input_text = unicode_body.split('=')[1] if unicode_body else ''
        
        original_lines = input_text.splitlines()
        original_html_lines = []
        for text_line in original_lines:
            if len(text_line) == 0:
                continue
            html_line = f"<p>{text_line}</p>"
            original_html_lines.append(html_line)

        # Replace text using mappings specified in the Google Sheet
        spreadsheet_id = extract_spreadsheet_id(GOOGLE_SPREAD_SHEET_URL)
        # Access the Google Sheet by Spreadsheet ID
        spreadsheet = gspread_client.open_by_key(spreadsheet_id)
        # Open the worksheet by name
        worksheet = spreadsheet.worksheet(GOOGLE_SHEET_NAME)
        # Get all records from the worksheet
        records = worksheet.get_all_records()

        if IS_DEBUGGING:
            print("Madarin Cantonese Mappings")
            print(records)
            # Example:
            # [
            #     {'Mandarin': '早上好', 'Cantonese': '早晨'},
            #     {'Mandarin': '现在', 'Cantonese': '依家'},
            #     {'Mandarin': '这里', 'Cantonese': '呢度'},
            #     {'Mandarin': '为什么', 'Cantonese': '点解'}
            # ]

        replaced_text = input_text
        for mapping in records:
            mandarin = mapping['Mandarin']
            cantonese = mapping['Cantonese']
            if IS_DEBUGGING:
                print(f"replacing {mandarin} with {cantonese}")
            replaced_text = replaced_text.replace(mandarin, cantonese)

        if IS_DEBUGGING:
            print(f"Replaced outcome: {replaced_text}")

        replaced_text_lines = replaced_text.splitlines()
        replaced_text_html_lines = []
        for text_line in replaced_text_lines:
            if len(text_line) == 0:
                continue
            html_line = f"<p>{text_line}</p>"
            replaced_text_html_lines.append(html_line)
        
        # Return the result
        result_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{APP_NAME}</title>
            <meta content="text/html; charset=utf-8" http-equiv="content-type"/>
        </head>
        <body>
            <h1>{APP_NAME}</h1>
            <div style="display: flex">
                <div style="width: 50%">
                    <h2>Original input</h2>
                    {''.join(original_html_lines)}
                </div>
                <div style="width: 50%">
                    <h2>Convert outcome</h2>
                    {''.join(replaced_text_html_lines)}
                </div>
            </div>
            <a href="/mandarin-cantonese-translator">Back</a>
        </body>
        </html>
        """
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html'
            },
            'body': result_content
        }
    
    else:
        return {
            'statusCode': 405,
            'body': 'Method Not Allowed'
        }