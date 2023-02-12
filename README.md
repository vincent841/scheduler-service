# Event Notification Service(ENS)

## Prerequistes

- python 3.6 & 3.7 & 3.8 & 3.9 & 3.10


## Install the required modules

```bash
pip install -r src/requirements.txt
```


## Code Formatter

### Install Black

```bash
pip install black
```

## Start API server

```bash
cd src
python3 main.py
```

## Deployment

### build a docker image

```bash
# build a docker image
./build.sh

# push the docker image
./push.sh
```
