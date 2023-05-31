from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel, Field, ValidationError
from uuid import UUID
import gspread
from oauth2client.service_account import ServiceAccountCredentials
# from models.information import Information
import controller
import models
import schemas

from typing_extensions import Annotated

import yaml

from database import SessionLocal, engine
from sqlalchemy.orm import Session


app = FastAPI()

models.Base.metadata.create_all(bind=engine)

# Definir as informações da credencial do Google Drive
GOOGLE_DRIVE_CREDS = 'config/google/api-v2-387112-af2901f23eb9.json'
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Rota para obter o conteúdo das abas da planilha
@app.get("/planilha/{planilha_id}")
def obter_conteudo_abas(planilha_id: str):
    try:
        # Autenticar com as credenciais do Google Drive
        creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_DRIVE_CREDS, SCOPE)
        client = gspread.authorize(creds)

        # Abrir a planilha pelo ID
        planilha = client.open_by_key(planilha_id)

        # Obter o conteúdo de todas as abas
        abas = {}
        for aba in planilha.worksheets():
            conteudo = aba.get_all_values()
            abas[aba.title] = conteudo

        return abas

    except Exception as e:
        return {"erro": str(e)}

    # rota para obter todos os items
@app.get("/items/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = controller.getItems(db, skip=skip, limit=limit)
    return items


@app.post("/items/")
async def create_item(item: schemas.Item, db: Session = Depends(get_db)):
    controller.create_item(db, item)
    return {**item.dict()}

