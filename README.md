# Basic LLM + RAG system, fully local and open source
based on the ["Build your own RAG and run them locally"](https://blog.duy-huynh.com/build-your-own-rag-and-run-them-locally/) paper by Duy Huynh.
## Install Ollama
The application uses Ollama for running any compatible LLM so you must first install Ollama (see https://ollama.com), then run the Ollama server:
```shell
$ ollama serve
```
then open another terminal and pull the LLM you want to use. 
By default, the code uses mistral:latest but you can change it in the code (in the ChatPDF constructor in local_rag.py). So, by default:
```shell
$ ollama pull mistral
```
Although it's been tested only with mistral, you could use virtually any model compatible with Ollama (see https://ollama.com/library).

## Installing the ollama-rag application
- it is recommended to first install miniconda then
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
To run it:
`streamlit run local_rag_app.py`

# what's next
- create a Docker image
- allow saving and reloading of the vector database.