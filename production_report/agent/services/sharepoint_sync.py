from requests import request
import os
import msal
import requests
from dotenv import load_dotenv
from O365 import Account

load_dotenv()

CLIENT_ID = os.environ.get('AZURE_CLIENT_ID')
CLIENT_SECRET = os.environ.get('AZURE_CLIENT_SECRET')
TENANT_ID = os.environ.get('AZURE_TENANT_ID')
SITE_NAME = os.environ.get('SHAREPOINT_SITE_NAME')

def connect_sharepoint():
    authority = f"https://login.microsoftonline.com/{TENANT_ID}"
    
    app = msal.ConfidentialClientApplication(
        client_id=CLIENT_ID,
        client_credential=CLIENT_SECRET,
        authority=authority
    )

    scopes = ["https://graph.microsoft.com/.default"]
    result = app.acquire_token_for_client(scopes=scopes)

    if "access_token" in result:
        print("Token Obtenido")
        access_token = result["access_token"]

        headers = {'Authorization': f'Bearer {access_token}'}
        test_response = requests.get("https://graph.microsoft.com/v1.0/sites/root", headers=headers)
        
        if test_response.status_code == 200:
            print("Permisos confirmados")
        else:
            print(f"Token was success but no response from Sharepoint: {test_response.json()}")
    
    else:
        print("Fallo en autenticacion")
        print(f"Error: {result.get('error')}")
        print(f"Descripcion: {result.get('error_description')}")

if __name__ == "__main__":
    connect_sharepoint()