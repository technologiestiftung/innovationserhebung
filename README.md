# Innovationsdaten

Daten aus 10 Jahre Innovationserhebung ab Innovationserhebung 2013

## Installation guide

### Prerequisites

- Python version 3.11.4 (other versions might work as well) – You can e.g. use pyenv, see below.
- A Node version that’s defined in `.nvmrc` – You can e.g. use [nvm](https://github.com/nvm-sh/nvm) to switch to the right version (with `nvm use` or `nvm install`).
- If you are not using macOS or Linux, you might need to source the `.env` file manually to use the `get-fonts` script.


### General setup

1. Create a `.env` file by copying the `.env.example` file and filling out the variables.
2. Download the required font files (they will be placed in the `/app/static/fonts` directory):
    ```shell
    npm run get-fonts
    ```


### Set your virtual environment

The following steps are not required but recommended. This will allow you to install packages in your isolated virtual environment instead of globally, reducing the risk of breaking system tools or other projects.

1. Install [pyenv](https://github.com/pyenv/pyenv) and the [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv) plugin.
2. Download the appropriate Python version with 
```shell
pyenv install 3.11.4
``` 
in the command line.
3. Create a virtual environment with the appropriate Python version and name for your environment, for example 
```shell
pyenv virtualenv 3.11.4 innovationserhebung
```
4. Activate the environment with 
```shell
pyenv activate innovationserhebung
```


### Install Python requirements

Install the required libraries with the command line 
```shell
pip install -r requirements.txt
```


### Run the APP

1. Move to the `/app` directory.
2. Run the server with the command line 
```shell
uvicorn main:app --reload
```
3. Your terminal should show something like: 

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```


### Use tailwindcss and prettier-plugin-jinja-template

If you want to work on the html templating files as well it would be useful to install Tailwind, Prettier and use the prettier-plugin-jinja-template as well:

```shell
npm install
```


### Run tailwind watcher

1. Move to the root directory
2. From now on you can start the tailwind watcher from the root directory via 
```shell
npm run dev:tailwind
```

### Run server in development mode

1. After setting up the project according to the previous chapters, run
```shell
$ chmod +x run_dev.sh
```
from your root directory to give the bash file executable permission.

2. Now you should be able to start a development server via 
```shell
./run_dev.sh
```
This also runs the tailwind watcher
