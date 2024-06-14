from dotenv import load_dotenv
import os
 
load_dotenv()
 

config = {
    "TOKEN": os.getenv("TOKEN"),
    "GITHUB_API_URL": os.getenv("GITHUB_API_URL"),
    "ORG": os.getenv("ORG"),
    "ELASTIC_SEARCH_URL": os.getenv("ELASTIC_SEARCH_URL")
}

issues_repo_consultados = set()
commits_repo_consultados = set()

data_repositorios = []
data_lenguajes = []
data_usuarios = []
data_usuarios_activos = []
data_commits = []