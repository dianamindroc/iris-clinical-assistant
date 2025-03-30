# IRIS Clinical Assistant

A generative AI application built on InterSystems IRIS for Health that enables natural language querying of patient clinical data.

## Project Overview

The IRIS Clinical Assistant leverages vector embeddings and large language models to provide an intuitive way to query patient data stored in FHIR format. Using a Retrieval Augmented Generation (RAG) approach, the system enables natural language queries about patient conditions, medications, and procedures.

## Technical Architecture

The solution follows a Retrieval Augmented Generation (RAG) architecture:

1. **Data Pipeline**:
   * Fetches FHIR resources (Conditions, Medications, Procedures)
   * Generates comprehensive patient summaries
   * Creates vector embeddings using sentence-transformers
2. **Storage Layer**:
   * Stores embeddings in IRIS database
   * Maintains connections between summaries and patient IDs
3. **Query Processing**:
   * Converts natural language queries to embeddings
   * Performs hybrid search for relevant context
   * Generates responses using LLMs

## Prerequisites

* InterSystems IRIS for Health (Community Edition) - can be installed from docker directly with this application
* Python 3.10 or higher
* Hugging Face API token (for LLM access)
* **Note:** The InterSystems IRIS DB-API package is required for Python applications to connect to IRIS databases. This package is not available on PyPI and must be downloaded from the InterSystems distribution repository. For convenience, the package was already downloaded and placed in the wheels folder for this application.

## Installation

1. Clone repository

```git
git clone https://github.com/dianamindroc/iris-clinical-assistant.git
cd iris-clinical-assistant
```

2. Create environment and install requirements

```code
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt 
```

3. Start InterSystems IRIS for Health (you can use the provided docker-compose.yml)

```docker
docker-compose up -d
```

4. The FHIR server needs to be installed inside the container:

```docker
docker exec -it <container_name> iris session iris
zn "<namespace>"
zpm "install fhir-server"
```

Now you can exit the container by entering ```HALT```.

5. Additionally, we need to make sure that Admin has SQL privileges. For this, go to [dashboard](http://localhost:52773/csp/sys/UtilHome.csp), go to System Administration -> Security -> Users -> Go, click on Admin and at SQL Admin Privileges, Assign CREATE_TABLE, CREATE_QUERY, CREATE_PROCEDURE.

6. Install IRIS driver wheel (can be downloaded from [IRIS website](https://intersystems-community.github.io/iris-driver-distribution/), it was already downloaded and placed in the wheels folder)

```wheel
cd wheels
pip install intersystems_irispython-3.2.0-py3-none-any.whl
```
7. In ```.env```, make sure to update IRIS username, password, namespace and add a HuggingFace token for LLM inference.
8. Run app

```code
cd ..
python -m app.app
```
9. Access [localhost:5000](https://localhost:5000) and interact with the app
