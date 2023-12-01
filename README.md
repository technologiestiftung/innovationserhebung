[![Technologiestiftung Berlin](https://img.shields.io/badge/Built%20with%20%E2%9D%A4%EF%B8%8F-at%20Technologiestiftung%20Berlin-blue)](https://www.technologiestiftung-berlin.de)

# Innovationsdaten

This informational long-read is a digital version of the study "Innovationserhebung" which is conducted by the [Technologiestiftung Berlin](https://www.technologiestiftung-berlin.de) in german language. The study takes a look into data about business innovation since 2012 and was released in a [print version](https://www.technologiestiftung-berlin.de/downloads/innovationserhebung-2022) since then.

The digital version now enhances the findings and data with interactive charts to enable viewers to find even more customised insights. The data of the study is based on the yearly published [Innovationserhebung](https://www.zew.de/publikationen/zew-gutachten-und-forschungsberichte/forschungsberichte/innovationen/innovationserhebung) by the ZEW - Zentrum für Europäische Wirtschaftsforschung.

## Installation guide

### Prerequisites

- Python version 3.11.4 (other versions might work as well) – You can e.g. use pyenv, see below.
- A Node version that’s defined in `.nvmrc` – You can e.g. use [nvm](https://github.com/nvm-sh/nvm) to switch to the right version (with `nvm use` or `nvm install`).


### General setup

1. Create a `.env` file by copying the `.env.example` file and filling out the variables.
2. Install npm dependencies:
    ```shell
    npm install
    ```
3. Run the `get-fonts` script to download the required font files (they will be placed in the `/app/static/fonts` directory):
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


### Changing HTML & CSS

If you need to change HTML templates or CSS, you should use the Tailwind watcher to automatically recompile the CSS:

1. Move to the root directory
2. Start the tailwind watcher:
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

## Deployment

To deploy the app, these commands should be run (in the root directory) to build the app:

```shell
pip install -r requirements.txt && npm install && npm run build
```

Afterwards, the app can be started with these commands:

```shell
cd app/; uvicorn main:app --host 0.0.0.0 --port $PORT
```

These **environment variables** should be set:

| Variable       | Value        |
|----------------|--------------|
| FONTS_URL      | <secret-URL> |
| PORT           | 8000         |
| PYTHON_VERSION | 3.11.4       |


## Content Licencing

Texts and content available as [CC-BY-SA](https://creativecommons.org/licenses/by-sa/4.0/).


## Credits

<table>
  <tr>
    <td>
      A project by: <a href="https://www.technologiestiftung-berlin.de/en/">
        <br />
        <br />
        <img width="150" src="https://logos.citylab-berlin.org/logo-technologiestiftung-berlin-en.svg" />
      </a>
    </td>
    <td>
      Supported by: <a href="https://www.berlin.de/sen/web/">
        <br />
        <br />
        <img width="100" src="https://logos.citylab-berlin.org/logo-berlin-senweb-de.svg" />
      </a>
    </td>
  </tr>
</table>
