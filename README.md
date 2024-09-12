# Video Warehouse

## Google Cloud Setup

```shell
gcloud init
gcloud auth application-default login
```

## Setup from scratch

Make sure you have pipx and poetry already installed.

Note, below are some additional dependencies on 'ratelimit', this will help if you want to manage quota
and usage



```shell
cd <base-project-directory>

poetry new video-warehouse
cd video-warehouse

# Really installs everything
poetry add google-cloud-aiplatform
poetry add google-cloud-storage
poetry add ratelimit
poetry add tomlkit
```

## Running the project

```shell

cd <project directory>

# Create a virtual environment, install dependencies
poetry install

# Start virtual environment
poetry shell

# Run the program
warehouse

```