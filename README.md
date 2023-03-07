# Event Notification Service(ENS)


## User




## Prerequistes

- python 3.9 or later


## Install the required modules

```bash
pip install -r src/requirements.txt
```


## Code Formatter

#### Install Black

```bash
pip install black
```

## Start API server

```bash
cd src
python3 main.py
```

## Run test codes.

```bash
cd src
python3 -m unittest discover -s unit_test -p "*_test.py"
```

## Deployment

#### Build a docker image

```bash
# build a docker image
./build.sh

# push the docker image
./push.sh
```

