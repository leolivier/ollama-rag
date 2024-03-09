# Basic LLM + RAG system, fully local and open source

based on the ["Build your own RAG and run them locally"](https://blog.duy-huynh.com/build-your-own-rag-and-run-them-locally/) paper by Duy Huynh.

## Install Ollama
The application uses Ollama for running any compatible LLM so you must first install Ollama (see https://ollama.com), then run the Ollama server:
`$ ollama serve`

Then open another terminal and pull the LLM you want to use. 
By default, the code uses mistral:latest but you can change it in the code (in the ChatPDF constructor in local_rag.py). 
Although it's been tested only with mistral, you should be able to use virtually any Ollama compatible model (see https://ollama.com/library).
So, by default:
`$ ollama pull mistral`


## Installing the ollama-rag application

- it is recommended to first install miniconda:
```shell
$ conda create -n basic-rag python=3.12
$ conda activate basic-rag
```
- then clone this repo, change directory into the repo and install the requirements:
```shell
$ git clone https://github.com/leolivier/ollama-rag.git
$ cd ollama-rag 
$ pip install -r requirements.txt
```

## Running the application

### To run it locally with the WEB UI
`streamlit run local_rag_app.py`

### To run in batch mode
`python batch_rag.py [-h] -d DIRECTORY [-q QUESTION] [-s]`

This will run one question about a set of PDFs using an LLM

Options are:
  * -h, --help            show this help message and exit
  * -d DIRECTORY, --directory DIRECTORY
                        directory containing pdfs to be interrogated
  * -q QUESTION, --question QUESTION
                        question to be sent to the LLM about the documents
  * -s, --separately      process each pdf separately. Use this option if you want to ask the same question to each file.

### To run it with Docker
- First, build the image:
`docker build -t local_rag .`
- Then copy .env.example to .env and fill in the values for the environment variables.
  Particularly, you need to fill in the values for the Ollama server and the LLM you want to use.
- Then run the image:
`docker run -p 8501:8501 -d --name local_rag -v ./chromadb_data:/app/chromadb_data -v ./.env:/app/.env local_rag`
The volumes will store the data in the host machine and the .env file will be used to configure the app.

