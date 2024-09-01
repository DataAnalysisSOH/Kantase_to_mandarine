import base64
import boto3
import json
import gspread
import re

from oauth2client.service_account import ServiceAccountCredentials
from opencc import OpenCC
from typing import List, Dict
from urllib.parse import unquote_plus


APP_NAME = 'Mandarin Cantonese Translator'
DEPLOYMENT_TARGET = 'DEV'  # or 'PROD'
IS_DEBUGGING = False
# Secrets Name
GOOGLE_SERVICE_ACCOUNT_SECRET_NAME = {
    'DEV': 'dev/ygtq/mandarin_cantonese_translator',
    'PROD': 'prod/ygtq/mandarin_cantonese_translator'
}
# Google Sheet
GOOGLE_SPREAD_SHEET_URL = {
    'DEV': 'https://docs.google.com/spreadsheets/d/1SQ9bwDUxXbU6q8njvg4wtXBdJDAp7wJskApnDuS6vYY/edit?gid=0#gid=0',
    'PROD': 'https://docs.google.com/spreadsheets/d/1qCKGH5uNXkfn3L6XqwUPNhTYQhHE3r7r4PGiB21aEPo/edit?gid=0#gid=0'
}
MANDARIN_CANTONESE_MAPPING_SHEET_TITLE = 'Mappings'
SYMBOL_STANDARDIZATION_SHEET_TITLE = 'FirstPassConfig'


def get_lambda_last_modified_timestamp(context) -> str:
    client = boto3.client('lambda')

    # Get the function's configuration
    response = client.get_function_configuration(FunctionName=context.function_name)

    # Extract the last modified time
    last_modified = response['LastModified']
    return last_modified


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


def produce_html_lines(*, input: str) -> List[str]:
    lines = input.splitlines()
    html_lines = []
    for text_line in lines:
        html_line = f"<p>{text_line}</p>"
        html_lines.append(html_line)
    return html_lines


def get_all_records(
    *,
    sheet_title: str,
    gspread_client: gspread.client.Client
) -> List[Dict]:
    # Replace text using mappings specified in the Google Sheet
    spreadsheet_url = GOOGLE_SPREAD_SHEET_URL[DEPLOYMENT_TARGET]
    spreadsheet_id = extract_spreadsheet_id(spreadsheet_url)
    # Access the Google Sheet by Spreadsheet ID
    spreadsheet = gspread_client.open_by_key(spreadsheet_id)
    # Open the worksheet by name
    worksheet: gspread.worksheet.Worksheet = spreadsheet.worksheet(title=sheet_title)
    # Get all records from the worksheet
    records = worksheet.get_all_records()
    return records


def produce_mandarin_cantonese_replacement_outcome(
    *,
    input: str,
    gspread_client: gspread.client.Client
) -> str:
    records = get_all_records(
        sheet_title=MANDARIN_CANTONESE_MAPPING_SHEET_TITLE,
        gspread_client=gspread_client
    )

    if IS_DEBUGGING:
        print(f"Retrieved {len(records)} lines of Madarin Cantonese Mappings")
        # Example:
        # [
        #     {'Mandarin': '早上好', 'Cantonese': '早晨'},
        #     {'Mandarin': '现在', 'Cantonese': '依家'},
        #     {'Mandarin': '这里', 'Cantonese': '呢度'},
        #     {'Mandarin': '为什么', 'Cantonese': '点解'}
        # ]

    replaced_text = input
    for mapping in records:
        old = mapping['Mandarin']
        cantonese = mapping['Cantonese']
        # Add a space into the replacement output to avoid chain of changes
        # 1: 納斯拉勒 ==>【 納 斯 魯 拉 】* * 納 斯 拉 勒 * *
        # 2: 魯拉    ==>【 盧 拉 】* * 魯 拉 * *
        # So that output does not result 【納斯【盧拉】**魯拉**】**納斯拉勒**
        char_list = list(cantonese)
        new = ' '.join(char_list)
        replaced_text = replaced_text.replace(old, new)
    return replaced_text


def retrieve_input(event) -> str:
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
    
    # Split request payload body using '=' because form values 
    # comes in as pairs and each pair is connected by '='
    input_text = decoded_body.split('=')[1] if decoded_body else ''
    
    parsed_input = unquote_plus(input_text)
    return parsed_input


def produce_app_heading_html(
    *,
    http_method: str,
    last_modified: str,
) -> str:
    spreadsheet_url = GOOGLE_SPREAD_SHEET_URL[DEPLOYMENT_TARGET]
    html = f"""
        <div style="display: flex; flex-direction: column;">
            {
                """
                <a href="/mandarin-cantonese-translator">&lt;&lt; Back</a>
                """ if http_method == 'POST' else ''
            }
            <div style="display: flex; justify-content: space-between">
            <h1>
                {APP_NAME}
                {
                    """
                    <span style="color: #f57e42;">(TESTING)</span>
                    """ if DEPLOYMENT_TARGET != 'PROD' else ''
                }
            </h1>
            <span>Last modified: {last_modified}</span>
            </div>
        </div>
        {
            """
            <div style="color: #f57e42;">
                Please use the PRODUCTION site with this 
                <a href="https://gvpun3viu9.execute-api.us-east-1.amazonaws.com/mandarin-cantonese-translator">link</a>. Thanks.
            </div>
            """ if DEPLOYMENT_TARGET != 'PROD' else ''
        }
        <div style="margin: 1rem 0;">
            <a href="{spreadsheet_url}" target="_blank">Translation Config</a>
        </div>
    """
    return html


def produce_initial_form_html(
    *,
    app_heading_html: str,
) -> str:
    html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{APP_NAME}</title>
            <meta content="text/html; charset=utf-8" http-equiv="content-type"/>
        </head>
        <body>
            {app_heading_html}
            <form action="/mandarin-cantonese-translator" method="post">
                <textarea name="input_text" rows="20" cols="60"></textarea><br><br>
                <input type="submit" value="Convert">
            </form>
        </body>
        </html>
        """
    return html


def produce_replacement_outcome_html(
    *,
    app_heading_html: str,
    original_html_lines: List[str],
    replaced_text_html_lines: List[str],
) -> str:
    # Return the result
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{APP_NAME}</title>
        <meta content="text/html; charset=utf-8" http-equiv="content-type"/>
    </head>
    <body>
        {app_heading_html}
        <div style="display: flex">
            <div style="width: 50%; overflow: hidden; padding: 0 1rem 1rem; margin: 1rem; border: solid 1px #ccc;">
                <h2>Original input</h2>
                <button onclick="copyToClipboard('input')">Copy input</button>
                <div id="input">
                {''.join(original_html_lines)}
                </div>
            </div>
            <div style="width: 50%; overflow: hidden; padding: 0 1rem 1rem; margin: 1rem; border: solid 1px #ccc;">
                <h2>Convert outcome</h2>
                <button onclick="copyToClipboard('output')">Copy outcome</button>
                <div id="output">
                {''.join(replaced_text_html_lines)}
                </div>
            </div>
        </div>
        <script>
            function copyToClipboard(elementId) {{
                var range = document.createRange();
                range.selectNode(document.getElementById(elementId));
                window.getSelection().removeAllRanges(); // clear current selection
                window.getSelection().addRange(range); // to select text
                document.execCommand("copy");
                window.getSelection().removeAllRanges();// to deselect
            }}
        </script>
    </body>
    </html>
    """
    return html


def get_gspread_client() -> gspread.client.Client:
    # Create a Secrets Manager client
    secrets_client = boto3.client('secretsmanager')
    # Retrieve the secret
    secret_id = GOOGLE_SERVICE_ACCOUNT_SECRET_NAME[DEPLOYMENT_TARGET]
    response = secrets_client.get_secret_value(SecretId=secret_id)
    # Parse the secret's value as JSON
    service_account_secret = json.loads(response['SecretString'])
    
    # Use the credentials to access the Google Sheets API
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_secret, scope)
    gspread_client = gspread.authorize(creds)
    return gspread_client


def produce_symbol_standardization(
    *,
    input: str,
    gspread_client: gspread.client.Client
) -> str:
    records = get_all_records(
        sheet_title=SYMBOL_STANDARDIZATION_SHEET_TITLE,
        gspread_client=gspread_client
    )

    if IS_DEBUGGING:
        print(f"Retrieved {len(records)} lines of Symbol Standardization Mappings")

    replaced_text = input
    for mapping in records:
        old = mapping['Original']
        new = mapping['Replace']
        replaced_text = replaced_text.replace(old, new)
    return replaced_text


def convert_to_traditional_chinese(
    *,
    input: str
) -> str:
    # Initialize the converter
    cc = OpenCC('s2t')  # s2t means Simplified to Traditional

    # Convert Simplified Chinese text to Traditional Chinese
    traditional_text = cc.convert(input)
    return traditional_text


def lambda_handler(event, context):
    print (f"{APP_NAME} starts ...")

    if IS_DEBUGGING:
        print(f"Event: {event}")
        
    http_method = event['requestContext']['http']['method']
    
    # 1. Make sure we get the HTTP method used by the requester
    print(f"HTTP method: {http_method}")
    
    lambda_last_modified = get_lambda_last_modified_timestamp(context=context)

    app_heading_html = produce_app_heading_html(
        http_method=http_method,
        last_modified=lambda_last_modified,
    )

    if http_method == 'GET':
        # Return the HTML form
        html_content = produce_initial_form_html(
            app_heading_html=app_heading_html
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html'
            },
            'body': html_content
        }
        
    elif http_method == 'POST':
        parsed_input = retrieve_input(event)
        
        if IS_DEBUGGING:
            print(f"Parsed request body: {parsed_input}")

        traditionalized_content = convert_to_traditional_chinese(
            input=parsed_input
        )

        gspread_client = get_gspread_client()

        symbol_standardized_content = produce_symbol_standardization(
            input=traditionalized_content,
            gspread_client=gspread_client
        )

        replaced_text = produce_mandarin_cantonese_replacement_outcome(
            input=symbol_standardized_content,
            gspread_client=gspread_client,
        )

        if IS_DEBUGGING:
            print(f"Replaced outcome: {replaced_text}")

        replaced_text_html_lines = produce_html_lines(
            input=replaced_text
        )
        
        original_html_lines = produce_html_lines(
            input=parsed_input
        )
        result_content = produce_replacement_outcome_html(
            app_heading_html=app_heading_html,
            original_html_lines=original_html_lines,
            replaced_text_html_lines=replaced_text_html_lines,
        )
        
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
