from fastapi import APIRouter
from app.services.userService import (
    miembros_organización_servicio,
    miembros_activos_servicio,
    index_miembros,
)
from dotenv import load_dotenv
from datetime import datetime
import logging


load_dotenv()
router = APIRouter(prefix="/Users", tags=["Usuarios"])


async def repetir_tareas_usuario():
    logging.info(f"Módulo Usuarios: {datetime.now()}")
    await miembros_grupoASD()
    await miembros_activos()


@router.get("/")
async def miembros_grupoASD():
    miembros_data = await miembros_organización_servicio()
    try:
        await index_miembros(miembros_data, "data_github")
        return miembros_data
    except Exception as e:
        logging.error(f"No se pudo enviar datos a Elasticsearch: {e}")
        return miembros_data


@router.get("/activos")
async def miembros_activos():
    miembros_activos = await miembros_activos_servicio()
    try:
        await index_miembros(miembros_activos, "data_github")
        return miembros_activos
    except Exception as e:
        logging.error(f"No se pudo enviar datos a Elasticsearch: {e}")
        return miembros_activos
