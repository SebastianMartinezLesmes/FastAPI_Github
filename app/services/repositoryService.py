from fastapi import HTTPException
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
from datetime import datetime, timedelta
from requests.exceptions import HTTPError
from dotenv import load_dotenv
from config import (
    config,
    data_repositorios,
    data_lenguajes,
)
import logging
import requests
import asyncio
import os

load_dotenv()

ELASTIC_SEARCH_URL = os.getenv("ELASTIC_SEARCH_URL")
ELASTICSEARCH_USERNAME = os.getenv("ELASTICSEARCH_USERNAME").strip()
ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD").strip()

es = Elasticsearch(
    [ELASTIC_SEARCH_URL], http_auth=(ELASTICSEARCH_USERNAME, ELASTIC_PASSWORD)
)


# 1 repositorios_org


async def services_repositorios_org():
    PAGE = 1
    repositorios = []
    while True:
        url = f"{config['GITHUB_API_URL']}/orgs/{config['ORG']}/repos?state=all&per_page=100&page={PAGE}"
        headers = {"Authorization": f"token {config['TOKEN']}"}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            if not data:
                break
            repositorios.extend(data)
            PAGE += 1
            await asyncio.sleep(1)
        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error al obtener la lista de repositorios: {str(e)}",
            )
    return repositorios


# 2 lenguajes_repositorio


async def service_Lenguajes_repos():
    if data_repositorios:
        lista_lenguajes = []
        for repo in data_repositorios:
            id_repo = repo["id_repositorio"]
            nombre_repo = repo["Repositorio"]
            url_languages = f"{config['GITHUB_API_URL']}/repos/{config['ORG']}/{nombre_repo}/languages?"
            headers = {
                "Authorization": f"token {config['TOKEN']}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
            response_languages = requests.get(url_languages, headers=headers)
            if response_languages.status_code == 200:
                languages = response_languages.json()
                nombre_lenguajes = list(languages.keys())
                lista_lenguajes.append(
                    {
                        "id_repositorio": id_repo,
                        "Repositorio": nombre_repo,
                        "numero de lenguajes": len(languages),
                        "nombre lenguajes": nombre_lenguajes,
                    }
                )
                data_lenguajes.append(
                    {
                        "id_repositorio": id_repo,
                        "Repositorio": nombre_repo,
                        "Lenguajes": {
                            lenguaje: puntaje for lenguaje, puntaje in languages.items()
                        },
                    }
                )
            else:
                lista_lenguajes.append(
                    {
                        "id_repositorio": id_repo,
                        "Repositorio": nombre_repo,
                        "error": f"Error en la consulta: {response_languages.text}",
                    }
                )
        return lista_lenguajes
    else:
        return Exception(
            status_code=response_languages.status_code, detail=response_languages.text
        )


# 4 inactivos


async def services_repos_inactivos_filtro():
    try:
        inactive_repos = []
        two_months_ago = datetime.utcnow() - timedelta(days=30)
        for repo in data_repositorios:
            last_commit_date = await service_ultimo_commit(repo)
            if last_commit_date and last_commit_date < two_months_ago:
                days_inactive = (datetime.utcnow() - last_commit_date).days
                formatted_date = last_commit_date.strftime("%d-%B-%Y")
                inactive_repos.append(
                    {
                        "id_repositorio": repo["id_repositorio"],
                        "Repositorio": repo["Repositorio"],
                        "Fecha_Ultimo_Commit": formatted_date,
                        "Dias_Inactivo": days_inactive,
                    }
                )
        inactive_repos.sort(key=lambda x: x["Fecha_Ultimo_Commit"])
        return inactive_repos
    except HTTPError as http_err:
        status_code = http_err.response.status_code
        detail = f"Error al obtener la lista de repositorios: {http_err}"
        raise HTTPException(status_code=status_code, detail=detail)
    except Exception as err:
        raise HTTPException(
            status_code=500, detail=f"Error interno del servidor: {err}"
        )


async def service_ultimo_commit(repo):
    branches_url = repo["branches_url"].split("{")[0]
    headers = {"Authorization": f"token {config['TOKEN']}"}
    last_commit_date = datetime.min
    try:
        response = requests.get(branches_url, headers=headers)
        response.raise_for_status()
        branches = response.json()
        if not branches:
            return None
        for branch in branches:
            commits_url = f"{config['GITHUB_API_URL']}/repos/{config['ORG']}/{repo['Repositorio']}/commits?sha={branch['name']}&per_page=1"
            commit_response = requests.get(commits_url, headers=headers)
            commit_response.raise_for_status()
            commits = commit_response.json()
            if commits:
                commit_date = datetime.strptime(
                    commits[0]["commit"]["author"]["date"], "%Y-%m-%dT%H:%M:%SZ"
                )
                last_commit_date = max(last_commit_date, commit_date)
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener la fecha del último commit: {str(e)}",
        )
    return last_commit_date


# 5 Issues_repositorio


async def service_Issues_repos():

    repositorios = data_repositorios
    if repositorios:
        lista_issues = []

        for repo in repositorios:
            total_tiempos_solucion = timedelta()
            num_issues_total = 0
            num_issues_abiertos_total = 0
            num_issues_cerrados_total = 0

            nombre_repo = repo["Repositorio"]
            id_repo = repo["id_repositorio"]
            PAGE = 1
            await asyncio.sleep(1)
            while True:
                url = f"{config['GITHUB_API_URL']}/repos/{config['ORG']}/{nombre_repo}/issues?state=all&per_page=100&page={PAGE}"
                headers = {
                    "Authorization": f"token {config['TOKEN']}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                }
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    issues = response.json()
                    num_issues = len(issues)
                    num_issues_total += num_issues
                    num_issues_abiertos_total += len(
                        [issue for issue in issues if issue["state"] == "open"]
                    )
                    num_issues_cerrados_total += len(
                        [issue for issue in issues if issue["state"] == "closed"]
                    )

                    for issue in issues:
                        if issue["closed_at"] and issue["created_at"]:
                            creado_txt = datetime.strptime(
                                issue["created_at"], "%Y-%m-%dT%H:%M:%SZ"
                            )
                            cerrado_txt = datetime.strptime(
                                issue["closed_at"], "%Y-%m-%dT%H:%M:%SZ"
                            )

                            tiempo_solucion = cerrado_txt - creado_txt
                            total_tiempos_solucion += tiempo_solucion

                    if num_issues < 100:
                        break
                    else:
                        PAGE += 1
                        await asyncio.sleep(1)

                else:
                    lista_issues.append(
                        {
                            "Repositorio": nombre_repo,
                            "error": f"Error en la consulta: {response.text}",
                        }
                    )
                    break

            tiempo_x_repo_promedio_d = (
                round(total_tiempos_solucion.days / num_issues_total, 4)
                if num_issues_total > 0
                else 0
            )
            tiempo_x_repo_promedio_h = (
                round(
                    total_tiempos_solucion.total_seconds() / (num_issues_total * 3600),
                    4,
                )
                if num_issues_total > 0
                else 0
            )

            lista_issues.append(
                {
                    "id_repositorio": id_repo,
                    "Repositorio": nombre_repo,
                    "total_incidencias": num_issues_total,
                    "incidencias_abiertas": num_issues_abiertos_total,
                    "incidencias_cerradas": num_issues_cerrados_total,
                    "tiempo_solucion_issues": str(total_tiempos_solucion),
                    "promedio_total_dias_resolucion": tiempo_x_repo_promedio_d,
                    "promedio_total_horas_resolucion": tiempo_x_repo_promedio_h,
                }
            )

        return lista_issues
    else:
        raise Exception("Error al obtener los repositorios")


# 6 total_commits_repositorio


async def commits_repositorio():
    repositorios = data_repositorios
    resultados_con_formato = []
    for repo in repositorios:

        commits_del_repo = await obtener_commits_por_repositorio(
            repo["Repositorio"], repo["rama por defecto"]
        )

        num_commits = len(commits_del_repo) if commits_del_repo else 0

        resultados_con_formato.append(
            {
                "id_repositorio": repo["id_repositorio"],
                "Repositorio": repo["Repositorio"],
                "commits_repo": num_commits,
            }
        )
    return resultados_con_formato


async def obtener_commits_por_repositorio(nombre_repo, rama_por_defecto):
    commits = []
    page = 1
    if not rama_por_defecto:
        return commits
    while True:
        url_commits = f"{config['GITHUB_API_URL']}/repos/{config['ORG']}/{nombre_repo}/commits?sha={rama_por_defecto}&per_page=100&page={page}"
        headers = {
            "Authorization": f"token {config['TOKEN']}",
            "Accept": "application/vnd.github+json",
        }
        response = requests.get(url_commits, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if not data:
                break
            commits.extend(data)
            page += 1
        elif response.status_code == 409 or response.status_code != 200:
            logging.warning(
                f"Repositorio '{nombre_repo}' en la rama '{rama_por_defecto}' sin commits o inexistente. Código: {response.status_code}"
            )
            break
    return commits


# 7 ramas_repositorio


async def services_Branches_repos():
    if data_repositorios:
        lista_ramas = []
        for repo in data_repositorios:
            nombre_repo = repo["Repositorio"]
            id_repo = repo["id_repositorio"]
            page = 1
            ramas_totales = []
            while True:
                url_B = f"{config['GITHUB_API_URL']}/repos/{config['ORG']}/{nombre_repo}/branches?per_page=100&page={page}"
                headers = {
                    "Authorization": f"token {config['TOKEN']}",
                    "Accept": "application/vnd.github.v3+json",
                }
                response_B = requests.get(url_B, headers=headers)
                if response_B.status_code == 200:
                    ramas = response_B.json()
                    ramas_totales.extend(ramas)
                    if len(ramas) < 100:
                        break
                    page += 1
                    await asyncio.sleep(1)
                else:
                    logging.error(f"Error {response_B.status_code}: {response_B.text}")
                    break

            lista_ramas_activas = []
            lista_ramas_inactivas = []
            for rama in ramas_totales:
                branch_name = rama["name"]
                commits_url = f"{config['GITHUB_API_URL']}/repos/{config['ORG']}/{nombre_repo}/commits?sha={branch_name}&per_page=1"
                response_commits = requests.get(commits_url, headers=headers)
                if response_commits.status_code == 200:
                    commit_data = response_commits.json()
                    if commit_data:
                        commit_date_str = commit_data[0]["commit"]["author"]["date"]
                        commit_date = datetime.strptime(
                            commit_date_str, "%Y-%m-%dT%H:%M:%SZ"
                        )
                        today = datetime.utcnow()
                        if (today - commit_date).days > 30:
                            lista_ramas_inactivas.append(branch_name)
                        else:
                            lista_ramas_activas.append(branch_name)
                    else:
                        logging.warning(
                            f"No hay commits para la rama {branch_name} en el repositorio {nombre_repo}."
                        )
                else:
                    logging.error(
                        f"Error {response_commits.status_code}: {response_commits.text}"
                    )

            lista_ramas.append(
                {
                    "id_repositorio": id_repo,
                    "Repositorio": nombre_repo,
                    "numero_ramas": len(ramas_totales),
                    "num_activos": len(lista_ramas_activas),
                    "num_inactivos": len(lista_ramas_inactivas),
                }
            )

        return lista_ramas
    else:
        return None


# 9 pulls_repositorio


# 6 total_commits_repositorio


async def commits_repositorio():
    repositorios = data_repositorios
    resultados_con_formato = []
    for repo in repositorios:

        commits_del_repo = await obtener_commits_por_repositorio(
            repo["Repositorio"], repo["rama por defecto"]
        )

        num_commits = len(commits_del_repo) if commits_del_repo else 0

        resultados_con_formato.append(
            {
                "id_repositorio": repo["id_repositorio"],
                "Repositorio": repo["Repositorio"],
                "commits_repo": num_commits,
            }
        )
    return resultados_con_formato


async def obtener_commits_por_repositorio(nombre_repo, rama_por_defecto):
    commits = []
    page = 1
    if not rama_por_defecto:
        return commits
    while True:
        url_commits = f"{config['GITHUB_API_URL']}/repos/{config['ORG']}/{nombre_repo}/commits?sha={rama_por_defecto}&per_page=100&page={page}"
        headers = {
            "Authorization": f"token {config['TOKEN']}",
            "Accept": "application/vnd.github+json",
        }
        response = requests.get(url_commits, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if not data:
                break
            commits.extend(data)
            page += 1
        elif response.status_code == 409 or response.status_code != 200:
            logging.warning(
                f"Repositorio '{nombre_repo}' en la rama '{rama_por_defecto}' sin commits o inexistente. Código: {response.status_code}"
            )
            break
    return commits


# 7 ramas_repositorio


async def services_Branches_repos():
    if data_repositorios:
        lista_ramas = []
        for repo in data_repositorios:
            nombre_repo = repo["Repositorio"]
            id_repo = repo["id_repositorio"]
            page = 1
            ramas_totales = []
            while True:
                url_B = f"{config['GITHUB_API_URL']}/repos/{config['ORG']}/{nombre_repo}/branches?per_page=100&page={page}"
                headers = {
                    "Authorization": f"token {config['TOKEN']}",
                    "Accept": "application/vnd.github.v3+json",
                }
                response_B = requests.get(url_B, headers=headers)
                if response_B.status_code == 200:
                    ramas = response_B.json()
                    ramas_totales.extend(ramas)
                    if len(ramas) < 100:
                        break
                    page += 1
                    await asyncio.sleep(1)
                else:
                    logging.error(f"Error {response_B.status_code}: {response_B.text}")
                    break

            lista_ramas_activas = []
            lista_ramas_inactivas = []
            for rama in ramas_totales:
                branch_name = rama["name"]
                commits_url = f"{config['GITHUB_API_URL']}/repos/{config['ORG']}/{nombre_repo}/commits?sha={branch_name}&per_page=1"
                response_commits = requests.get(commits_url, headers=headers)
                if response_commits.status_code == 200:
                    commit_data = response_commits.json()
                    if commit_data:
                        commit_date_str = commit_data[0]["commit"]["author"]["date"]
                        commit_date = datetime.strptime(
                            commit_date_str, "%Y-%m-%dT%H:%M:%SZ"
                        )
                        today = datetime.utcnow()
                        if (today - commit_date).days > 30:
                            lista_ramas_inactivas.append(branch_name)
                        else:
                            lista_ramas_activas.append(branch_name)
                    else:
                        logging.warning(
                            f"No hay commits para la rama {branch_name} en el repositorio {nombre_repo}."
                        )
                else:
                    logging.error(
                        f"Error {response_commits.status_code}: {response_commits.text}"
                    )

            lista_ramas.append(
                {
                    "id_repositorio": id_repo,
                    "Repositorio": nombre_repo,
                    "numero_ramas": len(ramas_totales),
                    "num_activos": len(lista_ramas_activas),
                    "num_inactivos": len(lista_ramas_inactivas),
                }
            )

        return lista_ramas
    else:
        return None


# 9 pulls_repositorio


async def service_Pulls_repos():
    if data_repositorios:
        repos_lista = []
        for repo in data_repositorios:
            id_repo = repo["id_repositorio"]
            nombre_repo = repo["Repositorio"]
            total_tiempo_cierre = timedelta()
            page = 1
            suma_pulls = 0
            while True:
                url = f"{config['GITHUB_API_URL']}/repos/{config['ORG']}/{nombre_repo}/pulls?state=all&per_page=100&page={page}"
                headers = {
                    "Authorization": f"token {config['TOKEN']}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                }
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    pulls = response.json()
                    suma_pulls += len(pulls)
                    for pull in pulls:
                        if pull["closed_at"] and pull["created_at"]:
                            fecha_creacion = datetime.strptime(
                                pull["created_at"], "%Y-%m-%dT%H:%M:%SZ"
                            )
                            fecha_cierre = datetime.strptime(
                                pull["closed_at"], "%Y-%m-%dT%H:%M:%SZ"
                            )
                            tiempo_cierre = fecha_cierre - fecha_creacion
                        total_tiempo_cierre += tiempo_cierre
                    repo_existente = next(
                        (
                            repo
                            for repo in repos_lista
                            if repo["Repositorio"] == nombre_repo
                        ),
                        None,
                    )
                    if repo_existente:
                        repo_existente["numero_pulls"] += len(pulls)
                        repo_existente["numero_pulls_abiertos"] += len(
                            [pull for pull in pulls if pull["state"] == "open"]
                        )
                        repo_existente["numero_pulls_cerrados"] += len(
                            [pull for pull in pulls if pull["state"] == "closed"]
                        )
                    else:
                        repos_lista.append(
                            {
                                "id_repositorio": id_repo,
                                "Repositorio": nombre_repo,
                                "numero_pulls": len(pulls),
                                "numero_pulls_abiertos": len(
                                    [pull for pull in pulls if pull["state"] == "open"]
                                ),
                                "numero_pulls_cerrados": len(
                                    [
                                        pull
                                        for pull in pulls
                                        if pull["state"] == "closed"
                                    ]
                                ),
                                "total_tiempo_cierre_pulls": str(total_tiempo_cierre),
                                "promedio_dias_cierre": (
                                    round(
                                        total_tiempo_cierre.days
                                        / len(
                                            [
                                                pull
                                                for pull in pulls
                                                if pull["state"] == "closed"
                                            ]
                                        ),
                                        2,
                                    )
                                    if len(pulls) > 0
                                    and len(
                                        [
                                            pull
                                            for pull in pulls
                                            if pull["state"] == "closed"
                                        ]
                                    )
                                    > 0
                                    else 0
                                ),
                            }
                        )
                    if len(pulls) != 100:
                        break
                    else:
                        page += 1
                        await asyncio.sleep(1)
                else:
                    continue
        return repos_lista
    else:
        return {"error": "No se encontraron repositorios"}


# SERVICIO DE INDEXACIÓN


async def index_repos(repos_data, index_name):
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
