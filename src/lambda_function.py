import urllib.parse
import base64

APP_NAME = 'Mandarine Cantonese Translator'
IS_DEBUGGING = True

def lambda_handler(event, context):
    if IS_DEBUGGING:
        print(f"Event: {event}")
        
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
        
        # Replace text example
        replaced_text = input_text.replace('!', '?')
        
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