# rabbitmq-fallback-evaluation

## Setup rabbmitmq via docker

⇝ docker pull rabbitmq:3-management  
⇝ docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management

## Create a venv & activate it

⇝ python -m venv venv
⇝ source ./venv/bin/activate

## Install pika dependancy

⇝ pip install pika

## Run each file in a new terminal

⇝ python producer.py
⇝ python processor.py
⇝ python fallback_processor.py

## Check the queues created in the management console

`guest` is the default user for the management console
```
http://localhost:15672/ | guest | guest  
```
