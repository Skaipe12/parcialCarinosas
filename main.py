from fastapi import FastAPI, Body, Path, Query, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security.http import HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional, List
from starlette.requests import Request
from fastapi.security import HTTPBearer
from fastapi.encoders import jsonable_encoder
import pymongo
from pymongo import MongoClient
from bson import ObjectId

client = pymongo.MongoClient('mongodb+srv://admin:admin123@cluster0.7fnfgrt.mongodb.net/?retryWrites=true&w=majority')

db = client["asesinatos"]
collection = db["asesinatosCollection"]


app = FastAPI()
app.title = "La ciudad de las cariñosas"

class Asesinato(BaseModel):
    id: int
    victima: str
    familia: str
    lugar: str
    forma_asesinato: str
    casos_relacionados: List[int] = []



@app.get("/",tags=['Home'])
async def root():
    return {"message": "Hello World"}



@app.get("/asesinatos",tags=['Asesinatos'])
def obtener_asesinatos():
    asesinatos = list(collection.find({}))
    if asesinatos:
        for asesinato in asesinatos:
            asesinato["_id"] = str(asesinato["_id"])
        return JSONResponse(content=asesinatos, status_code=200)
    else:
        return JSONResponse(content={"message":"Sin asesinatos encontrados"}, status_code=404)

@app.post("/asesinatos",tags=['Asesinatos'])
def registrar_asesinato(asesinato: Asesinato):
    collection.insert_one(asesinato.dict())
    return {"message": "Asesinato registrado"}

@app.delete("/asesinatos/{id}", tags=['Asesinatos'])
def eliminar_asesinato(id: int):
    asesinato = collection.find_one_and_delete({"id": id})
    if asesinato:
        return {"message": "Asesinato eliminado"}
    else:
        raise HTTPException(status_code=404, detail="Asesinato no encontrado")


@app.put("/asesinatos/{id}", tags=['Asesinatos'])
def actualizar_asesinato(id: int, asesinato: Asesinato):
    asesinato_actualizado = collection.find_one_and_update(
        {"id": id},
        {"$set": asesinato.dict()},
        return_document=True
    )
    if asesinato_actualizado:
        asesinato_actualizado["_id"] = str(asesinato_actualizado["_id"])
        return {"message": "Asesinato Actualizado", "asesinato": asesinato_actualizado}
    else:
        raise HTTPException(status_code=404, detail="Asesinato no encontrado")


#Obtener las familias de las victimas
@app.get("/asesinatos/familias", tags=['Familias'])
def obtener_familias():
    familias = list(collection.find({},{"familia":1, "_id":0}))
    if familias:
        return JSONResponse(content=familias, status_code=200)
    else:
        return JSONResponse(content={"message":"Sin familias encontradas"}, status_code=404)


#Obtener los casos relacionados de las victimas que los tengan
@app.get("/asesinatos/casos_relacionados", tags=['Casos Relacionados'])
def obtener_casos_relacionados():
    casos_relacionados = list(collection.find({"casos_relacionados": {"$exists": True, "$ne": []}}, {"casos_relacionados":1, "_id":0}))
    if casos_relacionados:
        return JSONResponse(content=casos_relacionados, status_code=200)
    else:
        return JSONResponse(content={"message":"Sin casos relacionados encontrados"}, status_code=404)

#filtrar victimas por orden de asesinato
@app.get("/asesinatos/orden", tags=['Orden de Asesinatos'])
def obtener_orden():
    orden = list(collection.find({},{"id":1, "victima":1, "_id":0}).sort("id", pymongo.ASCENDING))
    if orden:
        return JSONResponse(content=orden, status_code=200)
    else:
        return JSONResponse(content={"message":"Sin orden de asesinatos encontrados"}, status_code=404)

#obtener las formas de asesinatos
@app.get("/asesinatos/formas", tags=['Formas de Asesinatos'])
def obtener_formas():
    formas = list(collection.find({},{"forma_asesinato":1, "_id":0}))
    if formas:
        return JSONResponse(content=formas, status_code=200)
    else:
        return JSONResponse(content={"message":"Sin formas de asesinatos encontrados"}, status_code=404)
    