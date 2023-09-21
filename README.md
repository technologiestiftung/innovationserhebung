# Innovationsdaten

Daten aus 10 Jahre Innovationserhebung ab Innovationserhebung 2013

Tested with Python 3.11.4

## Installation guide

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

### Run the APP

1. Move to the `/app` directory.
2. Install the required libraries with the command line 
```shell
pip install -r requirements.txt
```
3. Run the server with the command line 
```shell
uvicorn main:app --reload
```
4. Your terminal should show something like: 

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### Run tailwind watcher

1. Move to the root directory
2. Run 
```shell
tailwindcss init
```
3. From now on you can start the tailwind watcher from the root directory via 
```shell
tailwindcss -i app/styles/main.css -o app/static/css/main.css --watch
```

### Run server in development mode

1. After setting up the project according to the past two chapters. Run 
```shell
$ chmod +x run_dev.sh
```
from your root directory to give the bash file executale permission.

2. Now you should be able to start a development server via 
```shell
./run_dev.sh
```

### Use prettier-plugin-jinja-template

1. If u want to work on the html templating files as well it it useful to install prettier and use the prettier-plugin-jinja-template as well.

```shell
npm install
```
