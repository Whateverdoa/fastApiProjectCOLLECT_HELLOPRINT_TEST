import json
from pathlib import Path
import requests
from fastapi import FastAPI, Request, UploadFile, File

from SQL_lite.database_connection import initialize_database

# Schiet in naar : • http://172.27.23.70:51080/helloprint (lokaal).
# • http://92.65.9.78:61112/helloprint (web). http://92.65.9.78:61112/

app = FastAPI()


# if the json is uploaded as a json body then:
@app.post("/helloprint")
async def collect_json_body(request: Request):
    data = await request.json()

    # Generate a unique identifier for the payload
    payload_identifier = f"{data['orders'][0]['orderId']}-{data['orders'][0]['orderLines'][0]['orderDetailId']}"

    # Check if the payload is unique using the database
    db_conn, db_cursor = initialize_database()
    db_cursor.execute('SELECT * FROM received_payloads WHERE payload_identifier = ?', (payload_identifier,))
    existing_payload = db_cursor.fetchone()

    if existing_payload:
        db_conn.close()
        return "Payload already received. Not accepting duplicates."

    # If the payload is unique, insert it into the database along with the payload data
    payload_data = json.dumps(data)  # Serialize the JSON data
    db_cursor.execute('INSERT INTO received_payloads (payload_identifier, payload_data) VALUES (?, ?)',
                      (payload_identifier, payload_data))
    db_conn.commit()
    db_conn.close()

    # Save the JSON file with orderId and orderDetailId as the file name
    json_filename = f"{payload_identifier}.json"

    directory_path = Path('E:/Python_scripts/Helloprint_in_tmp')
    json_filename_switch = directory_path / json_filename

    with open(json_filename, 'w') as json_file:
        json.dump(data, json_file)

    try:
        with open(json_filename_switch, 'w') as json_file:
            json.dump(data, json_file)
    except Exception as e:
        print(e)

    # Download the PDF file from the URL in the 'filename' field
    pdf_url = data['orders'][0]['orderLines'][0]['filename']
    response = requests.get(pdf_url)

    # Save the PDF file with orderId and orderDetailId as the file name
    pdf_filename = f"{payload_identifier}.pdf"
    with open(pdf_filename, 'wb') as pdf_file:
        pdf_file.write(response.content)

    return f'[200:  {payload_identifier} ]'


# if the json is uploaded as a file then:
@app.post("/helloprint/")
async def collect_json_file(file: UploadFile = File(...)):
    # Read the contents of the file

    contents = await file.read()

    # Parse the JSON data
    data = json.loads(contents)

    orderId = data['orders'][0]['orderId']
    orderDetailId = data['orders'][0]['orderLines'][0]['orderDetailId']

    # Save the JSON file with orderId and orderDetailId as the file name
    json_filename = f"{orderId}_{orderDetailId}.json"
    with open(json_filename, 'w') as json_file:
        json.dump(data, json_file)

    # Download the PDF file from the URL in the 'filename' field
    pdf_url = data['orders'][0]['orderLines'][0]['filename']
    response = requests.get(pdf_url)

    # Save the PDF file with orderId and orderDetailId as the file name
    pdf_filename = f"{orderId}_{orderDetailId}.pdf"
    with open(pdf_filename, 'wb') as pdf_file:
        pdf_file.write(response.content)

    return {"message": "JSON as a file collected and PDF file saved successfully!"}

# uvicorn main:app --host 92.65.9.78 --port 61112
# uvicorn main:app --host 172.27.23.70 --port 51080 --reload

