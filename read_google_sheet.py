import csv
# We need to import require library
import gspread
from google.oauth2.service_account import Credentials
from __future__ import print_function
import pickletools
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from auth import spreadsheet_service
from auth import drive_service
from auth import drive_service
import datetime
from datetime import date, timedelta
import time
import schedule
from heartbeat_email1 import send_heartbeat_email
from dotenv import load_dotenv
import os
import smtplib
from email.message import EmailMessage

# We first need to access google sheet
load_dotenv()
# We need to define the SCOPES
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

credentials = None

credentials = service_account.Credentials.from_service_account_file('./credential.json', scopes=SCOPES)


# We need to define an function to read from google sheet's file and turn into dictionary
def get_specific_cell_value(spreadsheet_id, cell_range):
    try:
        service = build('sheets', 'v4', credentials=credentials)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=spreadsheet_id, range=cell_range).execute()
        values = result.get('values',[])
        return values[0][0]
# We are define an function to read csv file and turn into dictionary
def read_csv_to_dict(csv_file):
    # create a empty dictionary to store
    mandarin_cantonese_dict = {}
    # we are open the csv file
    with open(csv_file, 'r', encoding='utf-8-sig') as file:
        # We are using DictReader method
        reader = csv.DictReader(file)
        # We are taking care of each row
        for row in reader:
            mandarin = row['Mandarin']
            cantonese = row['Cantonese']
            mandarin_cantonese_dict[mandarin] = cantonese
        return mandarin_cantonese_dict
    
# We are creating a function to turn text into strings
def read_txt_to_string(txt_file):
    # We first need an empty string
    articles = ""
    with open(txt_file, 'r', encoding='utf-8') as file:
        # We are read each line in file
        for line in file:
            articles += line
    # We are Return the concatenated string containing the contents of the file
    return articles
# We are creating another function to replace words in the article
def replace_names(articles, mandarin_cantonese_dict):
    for original, new in mandarin_cantonese_dict.items():
        articles = articles.replace(original,new)
    return articles
        
# We are define the main method
def main():
    # We are defining the csv_file path
    csv_file = 'Mandarin to Cantonese - Sheet1.csv'
    mandarin_cantonese_dict = read_csv_to_dict(csv_file)
    text_file = 'article.txt'
    article = read_txt_to_string(text_file)
    modified_article = replace_names(article,mandarin_cantonese_dict)
    # We are printing out to check the result
    # print(mandarin_cantonese_dict)
    print(article)
    print(modified_article)
    
    
# We are define the entrypoint of the function
if __name__ == "__main__":
    main()