from fastapi import APIRouter
from app.services.repositoryService import (
    service_Issues_repos,
    service_Pulls_repos,
    services_Branches_repos,
    service_Lenguajes_repos,
    services_repositorios_org,
    services_repos_inactivos_filtro,
    commits_repositorio,
    index_repos,
)


from app.services.repositoryOrgService import (
    service_repositorios_actividad,
    rama_con_mas_commits,
    verificar_dependencias_desactualizadas,
)
from dotenv import load_dotenv
from datetime import datetime
from config import (
    data_repositorios,
    data_lenguajes,
    issues_repo_consultados,
    commits_repo_consultados,
)
import logging
import asyncio
import os


load_dotenv()
ORG = os.getenv("ORG")
GITHUB_API_URL = os.getenv("GITHUB_API_URL")


router = APIRouter(prefix="/Repository", tags=["Repository"])


async def repetir_tareas_repositorio_v1():
    logging.info(f"Módulo repositorios v1: {datetime.now()}")
    await repositorios_org()
    await lenguajes_repositorio()
    await dependencias_desactualizadas()
    await inactivos()
    await Issues_repositorio()


async def repetir_tareas_repositorio_v2():
    logging.info(f"Módulo repositorios v2: {datetime.now()}")
    await total_commits_repositorio()
    await ramas_repositorio()
    await mas_actividad()
    await pulls_repositorio()


@router.get("/Org")
async def repositorios_org():
    repositorios = await services_repositorios_org()
    data = []
    for repo in repositorios:
        created_at = datetime.strptime(repo["created_at"], "%Y-%m-%dT%H:%M:%SZ")
        meses = [
            "enero",
            "febrero",
            "marzo",
            "abril",
            "mayo",
            "junio",
            "julio",
            "agosto",
            "septiembre",
            "octubre",
            "noviembre",
            "diciembre",
        ]
        formatted_date = (
            created_at.strftime("%d-")
            + meses[created_at.month - 1]
            + created_at.strftime("-%Y")
        )
        repo_data = {
            "id_repositorio": repo["id"],
            "Repositorio": repo["name"],
            "Creación repositorio": formatted_date,
        }
        data.append(repo_data)
        data_repositorios.append(
            {
                "id_repositorio": repo["id"],
                "Repositorio": repo["name"],
                "Creación repositorio": formatted_date,
                "rama por defecto": repo["default_branch"],
                "branches_url": repo["branches_url"],
            }
        )
    try:
        await index_repos(data, "data_github")
        return data
    except Exception as e:
        logging.error(f"No se pudo enviar datos a Elasticsearch: {e}")
        return data


@router.get("/Lenguajes_repos")
async def lenguajes_repositorio():
    lenguajes = await service_Lenguajes_repos()
    try:
        await index_repos(lenguajes, "data_github")
        return lenguajes
    except Exception as e:
        logging.error(f"No se pudo enviar datos a Elasticsearch: {e}")
        return lenguajes


@router.get("/dependencias-desactualizadas")
async def dependencias_desactualizadas():
    resultado = []
    for repo in data_repositorios:
        repo_id = repo["id_repositorio"]
        nombre_repo = repo["Repositorio"]
        rama = await rama_con_mas_commits(nombre_repo)
        lenguaje_principal = None
        for datos_lenguaje in data_lenguajes:
            if datos_lenguaje["id_repositorio"] == repo_id:
                lenguajes = datos_lenguaje["Lenguajes"]
                if lenguajes:
                    lenguaje_principal = max(lenguajes, key=lenguajes.get)
                break
        desactualizadas = await verificar_dependencias_desactualizadas(
            nombre_repo, rama, lenguaje_principal
        )
        resultado.append(
            {
                "id_repositorio": repo["id_repositorio"],
                "Repositorio": repo["Repositorio"],
                "dependencias_desactualizadas": desactualizadas,
            }
        )
    try:
        await index_repos(resultado, "data_github")
        return resultado
    except Exception as e:
        logging.error(f"No se pudo enviar datos a Elasticsearch: {e}")
        return resultado


@router.get("/Inactivos")
async def inactivos():
    inactive_repos = await services_repos_inactivos_filtro()
    try:
        await index_repos(inactive_repos, "data_github")
        return inactive_repos
    except Exception as e:
        logging.error(f"No se pudo enviar datos a Elasticsearch: {e}")
        return inactive_repos


@router.get("/issues_repos")
async def Issues_repositorio():
    issues = await service_Issues_repos()
    try:
        await index_repos(issues, "data_github")
        return issues
    except Exception as e:
        logging.error(f"No se pudo enviar datos a Elasticsearch: {e}")
        return issues


@router.get("/total-commits")
async def total_commits_repositorio():
    todos_los_commits = await commits_repositorio()
    try:
        await index_repos(todos_los_commits, "data_github")
        return todos_los_commits
    except Exception as e:
        logging.error(f"Error: {e}")
        return {"error": "Error al obtener los commits de la rama por defecto"}


@router.get("/branches_repos")
async def ramas_repositorio():
    branches = await services_Branches_repos()
    try:
        await index_repos(branches, "data_github")
        return branches
    except Exception as e:
        logging.error(f"No se pudo enviar datos a Elasticsearch: {e}")
        return branches


@router.get("/Mas_Activo")
async def mas_actividad():
    actividad = await service_repositorios_actividad()
    try:
        await index_repos(actividad, "data_github")
        return actividad
    except Exception as e:
        logging.error(f"No se pudo enviar datos a Elasticsearch: {e}")
        return {"Repositorio": actividad}


@router.get("/Pulls_repos")
async def pulls_repositorio():
    pulls = await service_Pulls_repos()
    try:
        await index_repos(pulls, "data_github")
        return pulls
    except Exception as e:
        logging.error(f"No se pudo enviar datos a Elasticsearch: {e}")
        return pulls
