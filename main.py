from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

import pandas as pd
from io import StringIO, BytesIO
from datetime import datetime
import requests

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ou ["*"] para liberar geral
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/baixar/")
def baixar_dados(api_key: str = Form(...), phantom_id: str = Form(...)):
    url = f'https://api.phantombuster.com/api/v2/agents/fetch?id={phantom_id}'
    headers = {
        'Content-Type': 'application/json',
        'x-phantombuster-key': api_key,
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        org_folder = data.get('orgS3Folder')
        s3_folder = data.get('s3Folder')

        if not org_folder or not s3_folder:
            raise HTTPException(status_code=400, detail="Diretórios não encontrados.")

        csv_url = f"https://phantombuster.s3.amazonaws.com/{org_folder}/{s3_folder}/result.csv"
        csv_response = requests.get(csv_url)
        csv_response.raise_for_status()

        df = pd.read_csv(StringIO(csv_response.content.decode('utf-8')))
        output = BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)

        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f"resultado_{timestamp}.xlsx"

        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
