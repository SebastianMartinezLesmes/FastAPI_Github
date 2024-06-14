from fastapi import HTTPException
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
from dotenv import load_dotenv
from datetime import datetime
from config import config, data_repositorios, data_usuarios_activos
import requests
import logging
import asyncio
import os

load_dotenv()

ELASTIC_SEARCH_URL = os.getenv("ELASTIC_SEARCH_URL")
ELASTICSEARCH_USERNAME = os.getenv("ELASTICSEARCH_USERNAME").strip()
ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD").strip()

es = Elasticsearch(
    [ELASTIC_SEARCH_URL], http_auth=(ELASTICSEARCH_USERNAME, ELASTIC_PASSWORD)
)

# 1 contador_commits_usuariosRepo


async def commits_usuario_repo():
    repo_commits_count = []
    headers = {"Authorization": f"token {config['TOKEN']}"}
    try:
        for usuario in data_usuarios_activos:
            login = usuario["login"]
            for repo_info in usuario["Repositorios"]:
                repo_nombre = repo_info["Nombre"]
                repo_id = repo_info.get("id_repositorio")
                commits_url = f"{config['GITHUB_API_URL']}/repos/{config['ORG']}/{repo_nombre}/commits?author={login}&per_page=100"
                try:
                    commits_response = requests.get(commits_url, headers=headers)
                    commits_response.raise_for_status()
                    commits = commits_response.json()
                    if not commits:
                        continue

                    repo_commits_count.append(
                        {
                            "id_repositorio": repo_id,
                            "Repositorio": repo_nombre,
                            "usuario": login,
                            "commits": len(commits),
                        }
                    )
                    await asyncio.sleep(1)
                except requests.HTTPError as http_err:
                    status_code = http_err.response.status_code
                    if status_code == 404:
                        logging.warning(
                            f"404: Recurso no encontrado para URL {commits_url}"
                        )
                    elif status_code == 409:
                        logging.warning(f"409: Conflicto para URL {commits_url}")
                    elif status_code == 422:
                        logging.warning(
                            f"422: Error en la validación para URL {commits_url}"
                        )
                    elif status_code == 500:
                        logging.error(f"500: Error interno para URL {commits_url}")
                    elif status_code == 503:
                        logging.error(
                            f"503: Servicio no disponible para URL {commits_url}"
                        )
                    else:
                        logging.error(
                            f"Error HTTP desconocido {status_code} para URL {commits_url}"
                        )
                except Exception as e:
                    logging.error(f"Error en la solicitud para URL {commits_url}: {e}")
    except Exception as e:
        logging.error(f"Error interno en commits_usuario_repo: {e}")
        raise

    return repo_commits_count


# 2 obtener_media_commits_por_dia


async def commits_por_dia_func():
    headers = {"Authorization": f"token {config['TOKEN']}"}
    resultados = []

    try:
        for repo in data_repositorios:
            repo_nombre = repo["Repositorio"]
            repo_id = repo["id_repositorio"]
            commits_page = 1
            all_commit_dates = []
            while True:
                commits_url = f"{config['GITHUB_API_URL']}/repos/{config['ORG']}/{repo_nombre}/commits?per_page=100&page={commits_page}"
                try:
                    commits_response = requests.get(commits_url, headers=headers)
                    commits_response.raise_for_status()
                    repo_commits = commits_response.json()
                    if not repo_commits:
                        break

                    for commit in repo_commits:
                        commit_date = commit["commit"]["committer"]["date"].split("T")[
                            0
                        ]
                        all_commit_dates.append(commit_date)

                    commits_page += 1
                except requests.HTTPError as http_err:
                    status_code = http_err.response.status_code
                    if status_code == 404:
                        logging.warning(
                            f"404: Recurso no encontrado para URL {commits_url}"
                        )
                    elif status_code == 409:
                        logging.warning(f"409: Conflicto para URL {commits_url}")
                    elif status_code == 500:
                        logging.error(f"500: Error interno para URL {commits_url}")
                    else:
                        logging.error(
                            f"Error HTTP desconocido {status_code} para URL {commits_url}"
                        )
                    break
                except Exception as e:
                    logging.error(f"Error en la solicitud para URL {commits_url}: {e}")
                    break

            total_dias = len(set(all_commit_dates))
            total_commits = len(all_commit_dates)
            media_commits_por_dia = total_commits / total_dias if total_dias > 0 else 0
            commits_por_dia = {
                "Repositorio": repo_nombre,
                "id_repositorio": repo_id,
                "media_commits_dia": round(media_commits_por_dia, 3),
            }
            resultados.append(commits_por_dia)

    except Exception as e:
        logging.error(f"Error interno en commits_por_dia_func: {e}")
        raise

    return resultados


# 3 obtener_media_commits_por_hora


async def commits_por_hora_func():
    headers = {"Authorization": f"token {config['TOKEN']}"}
    resultados = []

    try:
        for repo in data_repositorios:
            repo_nombre = repo["Repositorio"]
            repo_id = repo["id_repositorio"]
            commits_page = 1
            commit_hours = []
            while True:
                commits_url = f"{config['GITHUB_API_URL']}/repos/{config['ORG']}/{repo_nombre}/commits?per_page=100&page={commits_page}"
                try:
                    commits_response = requests.get(commits_url, headers=headers)
                    commits_response.raise_for_status()
                    repo_commits = commits_response.json()
                    if not repo_commits:
                        break

                    for commit in repo_commits:
                        commit_date = commit["commit"]["committer"]["date"]
                        commit_hour = datetime.strptime(
                            commit_date, "%Y-%m-%dT%H:%M:%SZ"
                        ).hour
                        commit_hours.append(commit_hour)

                    commits_page += 1
                except requests.HTTPError as http_err:
                    status_code = http_err.response.status_code
                    if status_code == 404:
                        logging.warning(
                            f"404: Recurso no encontrado para URL {commits_url}"
                        )
                    elif status_code == 409:
                        logging.warning(f"409: Conflicto para URL {commits_url}")
                    elif status_code == 500:
                        logging.error(f"500: Error interno para URL {commits_url}")
                    else:
                        logging.error(
                            f"Error HTTP desconocido {status_code} para URL {commits_url}"
                        )
                    break
                except Exception as e:
                    logging.error(f"Error en la solicitud para URL {commits_url}: {e}")
                    break

            total_commits = len(commit_hours)
            if total_commits > 0:
                media_commits_por_hora = total_commits / 24.0
                commits_por_hora = {
                    "Repositorio": repo_nombre,
                    "id_repositorio": repo_id,
                    "media_commits_hora": round(media_commits_por_hora, 3),
                }
                resultados.append(commits_por_hora)

    except Exception as e:
        logging.error(f"Error interno en commits_por_hora_func: {e}")
        raise

    return resultados


# SERVICIO DE INDEXACIÓN


async def index_commits(repos_data, index_name):
    for repo in repos_data:
        doc_id = repo["id_repositorio"]
        try:
            existing_doc = es.get(index=index_name, id=doc_id)
            existing_data = existing_doc["_source"]
            existing_data.update(repo)
            es.update(index=index_name, id=doc_id, body={"doc": existing_data})
        except NotFoundError:
            es.index(index=index_name, id=doc_id, body=repo)
        except Exception as e:
            logging.error(f"Error al indexar documento en Elasticsearch: {e}")


async def index_commits_usu(repos_data, index_name):
    for repo_info in repos_data:
        try:

            doc_id = f"{repo_info['id_repositorio']}_{repo_info['usuario']}"

            existing_doc = es.get(index=index_name, id=doc_id)

            existing_data = existing_doc["_source"]
            existing_data["Repositorio"] = repo_info["Repositorio"]
            existing_data["commits"] = repo_info["commits"]
            es.update(index=index_name, id=doc_id, body={"doc": existing_data})
        except NotFoundError:
            es.index(
                index=index_name,
                id=doc_id,
                body={
                    "id_repositorio": repo_info["id_repositorio"],
                    "Repositorio": repo_info["Repositorio"],
                    "usuario": repo_info["usuario"],
                    "commits": repo_info["commits"],
                },
            )
        except Exception as e:
            logging.error(f"Error al indexar documento en Elasticsearch: {e}")
