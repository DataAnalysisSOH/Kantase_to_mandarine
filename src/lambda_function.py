import base64
import boto3
import json
import gspread
import re
import urllib.parse

from oauth2client.service_account import ServiceAccountCredentials


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
                <textarea name="input_text" rows="10" cols="30"></textarea><br><br>
                <input type="submit" value="Submit">
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
            body = base64.b64decode(event_body).decode('utf-8')
        else:
            body = event['body']
        
        if IS_DEBUGGING:
            print(f"Decoded request body: {body}")
        
        parsed_body = urllib.parse.parse_qs(body)
        
        if IS_DEBUGGING:
            print(f"Parsed request body: {parsed_body}")
        
        # Get input text. If no 'input_text' found use default value ['']
        input_text = parsed_body.get('input_text', [''])[0]
        
        # Count the number of characters in the text
        char_count = len(input_text)
        
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
            replaced_text = replaced_text.replace(mandarin, cantonese)
        
        replaced_text.replace('\n', '<br/>')

        # Return the result
        result_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{APP_NAME}</title>
        </head>
        <body>
            <h1>{APP_NAME}</h1>
            <p>The text you entered has {char_count} characters.</p>
            <h2>Replaced text</h2>
            <p>{replaced_text}</p>
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