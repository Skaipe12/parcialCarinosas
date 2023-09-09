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
from Models.models import Victima, Asesinato

client = pymongo.MongoClient('mongodb+srv://admin:admin123@cluster0.7fnfgrt.mongodb.net/?retryWrites=true&w=majority')

db = client["asesinatos"]
asesinatos_collection = db["asesinatosCollection"]
victimas_collection = db["victimasCollection"]



app = FastAPI()
app.title = "La ciudad de las cariñosas"
app.description = "API para la ciudad de las cariñosas"


@app.get("/",tags=['Home'])
async def root():
    return {"message": "Hello World"}

#Registrar Victima
@app.post("/victimas",tags=['Victimas'])
def registrar_victima(victima: Victima):
    victimas_collection.insert_one(victima.dict())
    return {"message": "Victima registrada"}

#Obtener victimas
@app.get("/victimas",tags=['Victimas'])
def obtener_victimas():
    victimas = list(victimas_collection.find({}))
    if victimas:
        for victima in victimas:
            victima["_id"] = str(victima["_id"])
        return JSONResponse(content=victimas, status_code=200)
    else:
        return JSONResponse(content={"message":"Sin victimas encontradas"}, status_code=404)
    
#Obtener victima por id
@app.get("/victimas/{id}",tags=['Victimas'])
def obtener_victima(id: int):
    victima = victimas_collection.find_one({"id": id})
    if victima:
        victima["_id"] = str(victima["_id"])
        return JSONResponse(content=victima, status_code=200)
    else:
        return JSONResponse(content={"message":"Sin victima encontrada"}, status_code=404)
    
#Eliminar Victima
@app.delete("/victimas/{id}", tags=['Victimas'])
def eliminar_victima(id: int):
    victima = victimas_collection.find_one_and_delete({"id": id})
    if victima:
        return {"message": "Victima eliminada"}
    else:
        raise JSONResponse(status_code=404, content={"message": "Victima no encontrada"})
    
#Actualizar Victima
@app.put("/victimas/{id}", tags=['Victimas'])
def actualizar_victima(id: int, victima: Victima):
    victima_actualizada = victimas_collection.find_one_and_update(
        {"id": id},
        {"$set": victima.dict()},
        return_document=True
    )
    if victima_actualizada:
        victima_actualizada["_id"] = str(victima_actualizada["_id"])
        return {"message": "Victima Actualizada", "victima": victima_actualizada}
    else:
        raise JSONResponse(status_code=404, content={"message": "Victima no encontrada"})


#Obtener asesinatos
#actualizado
@app.get("/asesinatos", tags=['Asesinatos'])
def obtener_asesinatos():
    asesinatos = list(asesinatos_collection.find({},{"_id":0}))
    if asesinatos:
        for asesinato in asesinatos:
            asesinato["victima_id"] = str(victimas_collection.find_one({"id": asesinato["victima_id"]},{"_id":0}))
            if asesinato["casos_relacionados"] is not None:
                asesinato["casos_relacionados"] = [str(victimas_collection.find_one({"id": caso},{"_id":0})) for caso in asesinato["casos_relacionados"]]
        return JSONResponse(content=asesinatos, status_code=200)
    else:
        return JSONResponse(content={"message": "Sin asesinatos encontrados"}, status_code=404)


#Obtener asesinato por id
@app.get("/asesinatos/{id}",tags=['Asesinatos'])
def obtener_asesinato(id: int):
    asesinato = asesinatos_collection.find_one({"id": id},{"_id":0})
    if asesinato:
        asesinato["victima_id"] = str(victimas_collection.find_one({"id": asesinato["victima_id"]},{"_id":0}))
        if asesinato["casos_relacionados"] is not None:
                asesinato["casos_relacionados"] = [str(victimas_collection.find_one({"id": caso},{"_id":0})) for caso in asesinato["casos_relacionados"]]
        return JSONResponse(content=asesinato, status_code=200)
    else:
        return JSONResponse(content={"message":"Sin asesinato encontrado"}, status_code=404)


#Registrar asesinato
@app.post("/asesinatos",tags=['Asesinatos'])
def registrar_asesinato(asesinato: Asesinato):
    victima = victimas_collection.find_one({"id": asesinato.victima_id})
    if victima is None:
        raise HTTPException(status_code=404, detail="Víctima no encontrada")
    else:
        asesinatos_collection.insert_one(asesinato.dict())
        return {"message": "Asesinato registrado"}

#Eliminar Asesinato
@app.delete("/asesinatos/{id}", tags=['Asesinatos'])
def eliminar_asesinato(id: int):
    asesinato = asesinatos_collection.find_one_and_delete({"id": id})
    if asesinato:
        return {"message": "Asesinato eliminado"}
    else:
        raise HTTPException(status_code=404, detail="Asesinato no encontrado")

#Actualizar Asesinato
@app.put("/asesinatos/{id}", tags=['Asesinatos'])
def actualizar_asesinato(id: int, asesinato: Asesinato):
    asesinato_actualizado = asesinatos_collection.find_one_and_update(
        {"id": id},
        {"$set": asesinato.dict()},
        return_document=True
    )
    if asesinato_actualizado:
        asesinato_actualizado["_id"] = str(asesinato_actualizado["_id"])
        return {"message": "Asesinato Actualizado", "asesinato": asesinato_actualizado}
    else:
        raise HTTPException(status_code=404, detail="Asesinato no encontrado")


#------------------------Filtros------------------------#


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
    