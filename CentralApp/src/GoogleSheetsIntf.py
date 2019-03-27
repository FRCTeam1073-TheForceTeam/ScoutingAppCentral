from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import json

import argparse

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_credentials():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds

def read_spreadsheet( spreadsheet_id, cell_range ):
    credentials = get_credentials()
    service = build('sheets', 'v4', credentials=credentials, cache_discovery=False)

    cell_ranges = cell_range.split(',')
    if len(cell_ranges) == 1:
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range=cell_range).execute()
        rows = result.get('values', [])
    else:
        rows = []
        result = service.spreadsheets().values().batchGet(
            spreadsheetId=spreadsheet_id, ranges=cell_ranges).execute()
        values = result.get('valueRanges', [])
        
        num_columns = len(values)
        num_rows = len(values[0]['values'])
        
        for i in range(0,num_rows):
            row = []
            for j in range(0,num_columns):
                try:
                    row.append(values[j]['values'][i])
                except:
                    row.append('')
            rows.append(row)
    
    return rows

def read_spreadsheet_data( spreadsheet_id, cell_range ):
    rows = read_spreadsheet( spreadsheet_id, cell_range )

    column_headers = rows[0]    

    spreadsheet_data = []
    for row in rows[1:]:
        row_dict = {}
        for i in range(0, len(row)):
            row_dict[column_headers[i]] = row[i]

        spreadsheet_data.append(row_dict)

    return spreadsheet_data

def read_spreadsheet_json( spreadsheet_id, cell_range ):
    
    rows = read_spreadsheet( spreadsheet_id, cell_range )
    
    column_headers = rows[0]    
    columns = []
    for header in column_headers:
        column = {}
        column['sTitle'] = header
        columns.append(column)

    sheet_dict = {}    
    sheet_dict['columns'] = columns
    sheet_dict['data'] = rows[1:]
    
    json_data = json.dumps( sheet_dict )

    return json_data
        
    
def add_scouting_data_row( sheet_name, row_data ):
    spreadsheet_id = '1oD9qvNCM_mxM_gTdXtGsZyUYVw56jnqdZp5XHkrukXU'

    rows = read_spreadsheet( spreadsheet_id, sheet_name )

    row_values = []
    column_headers = []
    
    if len(rows) is not 0:
        column_headers = rows[0]
        if len(column_headers) > 0:
            row_values = [''] * len(column_headers)

    for row_item in row_data:
        # Each row item is a tuple of name/value. Use the name to find the index
        # into the spreadsheet data. If the spreadsheet does not yet have a 
        # column with this name, then add a column to the spreadsheet
        try:
            column_index = column_headers.index( row_item[0] )
            row_values[column_index] = row_item[1]
        except ValueError:
            column_headers.append( row_item[0] )
            row_values.append( row_item[1] )

    update_row( spreadsheet_id, sheet_name, column_headers )
    update_row( spreadsheet_id, sheet_name, row_values, append=True )

def update_row( spreadsheet_id, cell_range, row_values, append=False ):
    credentials = get_credentials()
    service = build('sheets', 'v4', credentials=credentials, cache_discovery=False)

    # Call the Sheets API
    sheet = service.spreadsheets()

    body = { 'values': [ row_values ] }

    if append is True:
        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id, range=cell_range,
            valueInputOption='USER_ENTERED', body=body).execute()
    else:
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=cell_range,
            valueInputOption='USER_ENTERED', body=body).execute()

    
    
if __name__ == '__main__':

    spreadsheet_id = '1oD9qvNCM_mxM_gTdXtGsZyUYVw56jnqdZp5XHkrukXU'
    cell_range = 'MAREA2019'
    
    spreadsheet_data = read_spreadsheet_data( spreadsheet_id, cell_range )
    json_data = json.dumps( spreadsheet_data )

    print( json_data )
