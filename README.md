# Innovationsdaten

Daten aus 10 Jahre Innovationserhebung ab Innovationserhebung 2013

Tested with Python 3.11.4

## Installation guide

### Set your virtual environment

The following steps are not required but recommended. This will allow you to install packages in your isolated virtual environment instead of globally, reducing the risk of breaking system tools or other projects.

1. Download the required font files ([Source Serif](https://adobe-fonts.github.io/source-serif/) and Clan Pro) and place them inside `/app/static/fonts`.
2. Install [pyenv](https://github.com/pyenv/pyenv) and the [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv) plugin.
3. Download the appropriate Python version with 
```shell
pyenv install 3.11.4
``` 
in the command line.
4. Create a virtual environment with the appropriate Python version and name for your environment, for example 
```shell
pyenv virtualenv 3.11.4 innovationserhebung
```
5. Activate the environment with 
```shell
pyenv activate innovationserhebung
```

### Install requirements

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

1. If you want to work on the html templating files as well it would be useful to install tailwind, prettier and use the prettier-plugin-jinja-template as well.

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

1. After setting up the project according to the past two chapters. Run 
```shell
$ chmod +x run_dev.sh
```
from your root directory to give the bash file executable permission.

2. Now you should be able to start a development server via 
```shell
./run_dev.sh
```
This also runs the tailwind watcher
