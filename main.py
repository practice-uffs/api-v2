from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel, Field, ValidationError
from uuid import UUID
import gspread
from oauth2client.service_account import ServiceAccountCredentials
# from models.information import Information
import controller
import models
import schemas
import datetime
import time
import asyncio


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
# a api do google possui um limite de acesso de 60/minuto
@app.get("/planilha/{planilha_id}")
def obter_conteudo_abas(planilha_id: str):
    try:
        # carregar o log do ultimo acesso

        # Autenticar com as credenciais do Google Drive
        creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_DRIVE_CREDS, SCOPE)
        client = gspread.authorize(creds)

        # Abrir a planilha pelo ID
        planilhas = client.open_by_key(planilha_id).worksheets()

        # Obter o conteúdo de todas as abas
        abas = {}
        for aba in planilhas:
            time.sleep(1.05)
            conteudo = aba.get_all_values()
            if aba.title!="_Rules" and aba.title!="_Default":
                print(aba.title)
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


@app.get("/listall")
async def synchronizeDB():
    rows = []
    id_position = 'C:C'
    try:
        # Autenticar com as credenciais do Google Drive
        creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_DRIVE_CREDS, SCOPE)
        client = gspread.authorize(creds)

        # Abrir a planilha central
        planilha = client.open_by_key('1U0tVzmz0h1aeIE-4QEvrEnUvwLitmA2nUykO1j-vA2w')
        # id_sheets será uma matriz [1][n] sendo n a quantidade de campus mais o título da coluna
        id_sheets = planilha.worksheets()[0].get_values(id_position)
        if id_sheets[0][0]!='id':
            return f"foi identificado uma mudança na coluna onde localiza-se o id das planilha, atualmente o codigo considera {id_position}"
        id_sheets.pop(0) # remove o id_sheets[0][0] que contem apenas o titulo para não gerar consulta

        for id_campus in id_sheets:
            rows.append(obter_conteudo_abas(id_campus[0]))
        return rows
    except Exception as e:
        print(e)
