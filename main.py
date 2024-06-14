from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import commits, user, repository
from app.api.routes.user import repetir_tareas_usuario
from app.api.routes.commits import repetir_tareas_commits
from app.api.routes.repository import (
    repetir_tareas_repositorio_v1,
    repetir_tareas_repositorio_v2,
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from dotenv import load_dotenv
from datetime import datetime
from config import (
    config,
    data_commits,
    data_repositorios,
    data_lenguajes,
    data_usuarios,
    data_usuarios_activos,
)
import requests
import logging
import asyncio
import os


app = FastAPI(title="github-elk", version="1.0.0", contact={"name": "github-elk"})
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exposición de rutas para pruebas
# app.include_router(repository.router, prefix="/api")
# app.include_router(commits.router, prefix="/api")
# app.include_router(user.router, prefix="/api")


async def tasa_ApiGithub():
    url = f"{config['GITHUB_API_URL']}/rate_limit"
    headers = {"Authorization": f"token {config['TOKEN']}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        limit = response.json()
        used = limit["rate"]["used"]
        remaining = limit["rate"]["remaining"]
        if remaining > 0:
            logging.info(
                f"Te quedan {remaining} consultas disponibles en la API de GitHub, USOS: {used}"
            )
        else:
            logging.warning(
                "Has alcanzado el límite máximo de consultas a la API de GitHub. Por favor, espera un rato antes de hacer más consultas."
            )
    else:
        logging.error(
            f"Hubo un error al hacer la consulta a la API de GitHub. Código de estado: {response.status_code}"
        )


async def tareas_programadas():
    global data_commits, data_repositorios, data_lenguajes, data_usuarios, data_usuarios_activos
    logging.info(f"Tarea ejecutada a las {datetime.now()}")

    print("Este es el array de commits", data_commits)
    print("Este es el array de repositorios", data_repositorios)
    print("Este es el array de lenguajes", data_lenguajes)
    print("Este es el array de usuarios", data_usuarios)
    print("Este es el array de usuarios activos", data_usuarios_activos)

    # MÓDULO REPOSITORIOS v1

    await tasa_ApiGithub()
    await repetir_tareas_repositorio_v1()
    await tasa_ApiGithub()
    await asyncio.sleep(4200)

    # MÓDULO REPOSITORIOS v2

    await tasa_ApiGithub()
    await repetir_tareas_repositorio_v2()
    await tasa_ApiGithub()
    await asyncio.sleep(4200)

    # MÓDULO USUARIOS

    await tasa_ApiGithub()
    await repetir_tareas_usuario()
    await tasa_ApiGithub()
    await asyncio.sleep(4200)

    # MÓDULO COMMITS

    await tasa_ApiGithub()
    await repetir_tareas_commits()
    await tasa_ApiGithub()

    data_commits.clear()
    data_repositorios.clear()
    data_lenguajes.clear()
    data_usuarios.clear()
    data_usuarios_activos.clear()

    print("Este es el array de commits", data_commits)
    print("Este es el array de repositorios", data_repositorios)
    print("Este es el array de lenguajes", data_lenguajes)
    print("Este es el array de usuarios", data_usuarios)
    print("Este es el array de usuarios activos", data_usuarios_activos)

    logging.info(f"Tareas terminadas a las {datetime.now()}")


@app.on_event("startup")
async def startup_event():
    logging.info(f"FastApi en ejecución: {datetime.now()}")
    load_dotenv()
    scheduler = AsyncIOScheduler(timezone="America/Bogota")
    task_interval = int(os.getenv("TASK_INTERVAL_MINUTES"))
    scheduler.add_job(
        tareas_programadas,
        IntervalTrigger(minutes=task_interval),
        id="tareas_programadas",
    )
    scheduler.start()
    await tareas_programadas()
