from fastapi import APIRouter, HTTPException
from app.services.commitsService import (
    commits_usuario_repo,
    commits_por_dia_func,
    commits_por_hora_func,
    index_commits_usu,
    index_commits,
)
from dotenv import load_dotenv
from datetime import datetime
import logging

load_dotenv()

router = APIRouter(prefix="/Commits", tags=["Commit"])


async def repetir_tareas_commits():
    logging.info(f"Módulo Commits: {datetime.now()}")
    await contador_commits_usuariosRepo()
    await obtener_media_commits_por_dia()
    await obtener_media_commits_por_hora()


@router.get("/")
async def contador_commits_usuariosRepo():
    try:
        commits_usuarioRep = await commits_usuario_repo()
        if not commits_usuarioRep:
            raise HTTPException(
                status_code=400, detail="No se encontraron datos de commits"
            )
        await index_commits_usu(commits_usuarioRep, "data_github")
        return commits_usuarioRep
    except HTTPException as http_err:
        logging.error(f"HTTP error: {http_err}")
        raise
    except Exception as e:
        logging.error(f"Error interno del servidor: {e} ")
        raise HTTPException(
            status_code=500, detail=f"Error interno del servidor: {str(e)}"
        )


@router.get("/PorDia")
async def obtener_media_commits_por_dia():
    try:
        commits_por_dia = await commits_por_dia_func()
        await index_commits(commits_por_dia, "data_github")
        return commits_por_dia
    except HTTPException as http_err:
        logging.error(f"HTTP error: {http_err}")
        raise
    except Exception as e:
        logging.error(f"Error interno del servidor: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error interno del servidor: {str(e)}"
        )


@router.get("/PorHora")
async def obtener_media_commits_por_hora():
    try:
        commits_por_hora = await commits_por_hora_func()
        await index_commits(commits_por_hora, "data_github")
        return commits_por_hora
    except HTTPException as http_err:
        logging.error(f"HTTP error: {http_err}")
        raise
    except Exception as e:
        logging.error(f"Error interno del servidor: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error interno del servidor: {str(e)}"
        )
