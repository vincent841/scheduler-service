# Scalable Scheduler Service

## Service Overview

![Scalable Scheduler Service](./assets/scheduler-service-diagram.png "Scalable Scheduler Service")

This service triggers events according to the schedule information specified by the user, and is intended for use in a cloud environment as well as a local environment.

### Features

- Asynchronous schedule event handling
- Horizontal scalability according to service load
- Schedule recovery when service restarts
- Schedule Event History


## Setup

### Prerequistes

- python 3.9 or later


### Install the required modules

```bash
pip install -r src/requirements.txt
```

### Prepare ***config.yaml***

copy ***config/config.yaml*** to ***src/*** after modifying it if necessary.


### Start API server

```bash
cd src
python3 main.py
```

### Run test codes.

```bash
cd src
python3 -m unittest discover -s test -p "*_test.py"
```

## Deployment

#### Build a docker image

```bash
# build a docker image
./build.sh

# push the docker image
./push.sh
```


## API Manual

```bash
{URL}:9902/docs

```

![Scalable Scheduler OpenAPI](./assets/scheduler-service-openapi.png "Scalable Scheduler OpenAPI")

### Schedule Type

#### Once
- now
  - no specific schedule 
  
  ```json
   {
  "name": "test01",
  "type": "now",
  "schedule": "",
  "task": {
    ...
  }
  ```

- date 
  - iso time format (ex. "2023-02-03T13:33:12") 
  
  ```json
   {
  "name": "test02",
  "type": "date",
  "schedule": "2023-02-03T13:33:12",
  "task": {
    ...
  }
  ```

- delay 
  - unit: seconds (ex. "10") 

  ```json
   {
  "name": "test03",
  "type": "delay",
  "schedule": "30",
  "task": {
    ...
  }
  ```


#### Recurring
- cron
  - ex. */1 * * * *

  ```json
   {
  "name": "test04",
  "type": "cron",
  "schedule": "*/1 * * * *",
  "task": {
    ...
  }
  ```

- delay-recur
  - unit: every seconds (ex "10")

  ```json
   {
  "name": "test05",
  "type": "delay-recur",
  "schedule": "60",
  "task": {
    ...
  }
  ```


### Task Type

- Rest

  ```json
   {
  "name": "test06",
  "type": "cron",
  "schedule": "*/1 * * * *",
  "task": {
    "type": "rest",
    "connection": {"host": "http://localhost:3000/api/unstable/run-scenario/test-scenario-1", "headers": {"Content-Type": "application/json", "accept": "*/*"}},
    "data": {"instanceName": "test-scenario-1", "variables": {}}
  }
  ```

- Kafka

  ```json
   {
  "name": "test07",
  "type": "cron",
  "schedule": "*/1 * * * *",
  "task": {
    "type": "kafka",
    "connection": {"host": "localhost:9092", "topic": "example-topic"},
    "data": { ... }
  }
  ```

- Redis

  ```json
   {
  "name": "test08",
  "type": "cron",
  "schedule": "*/1 * * * *",
  "task": {
    "type": "redis",
    "connection": {"host": "redis://localhost", "topic": "example-topic"},
    "data": { ... }
  }
  ```


#### Task Rest Example with Cron Schedule

```json
{
  "name": "cron-test",
  "type": "cron",
  "schedule": "*/1 * * * *",
  "task": {
    "type": "rest",
    "connection": {
      "host": "http://localhost:3000/api/unstable/run-scenario/DELAY-TEST", 
      "headers": {"Content-Type": "application/json", "accept": "*/*"},
      "data": {"instanceName": "delay-test", "variables": {}}
    }
  }
}
```

#### Task Kafka Example with Now Schedule

```json
{
  "name": "ap3",
  "type": "now",
  "schedule": "",
  "task": {
    "type": "kafka",
    "connection": {
      "host": "localhost:9092", 
      "topic": "example-topic"},
    "data": {"id": "toboe"}
  }
}
```



## Additional Things

### k8s deployment

Please refer to k8s/*.

### Code Formatter

Black(https://github.com/psf/black)

```bash
pip install black
```
