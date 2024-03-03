FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential cmake \
		&& rm -rf /var/lib/apt/lists/*

# copy requirements.txt first to leverage Docker cache and not reinstall all requirements on every python code change
COPY requirements.txt .

RUN pip install -r requirements.txt

COPY *.py .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "local_rag_app.py", "--server.port=8501", "--server.address=0.0.0.0"]