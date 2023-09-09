from pydantic import BaseModel
from typing import List

class Victima(BaseModel):
    id: int
    nombre: str
    familia: str
    edad: int
    lugar: str

class Asesinato(BaseModel):
    id: int
    victima_id: int
    forma_asesinato: str
    casos_relacionados: List[int] = []