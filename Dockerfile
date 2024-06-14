FROM python:3.9

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

LABEL org.opencontainers.image.source https://github.com/Grupo-ASD/github-elk

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]