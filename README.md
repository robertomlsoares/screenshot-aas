# Screenshot-as-a-Service

This application is a backend component responsible for taking screenshots
of URLs provided by users. The server endpoints are separated by the worker
that takes the screenshots by a job queue using RabbitMQ.

## RabbitMQ and Redis

Before proceeding, you'll need to run RabbitMQ and Redis in order to run
this application. It's recommended to run them using Docker containers:

`docker run --name redis -d redis`

`docker run -d --hostname rabbit --name rabbit rabbitmq`

Later on, you'll need to know the ip addresses of both of these containers.
Use `docker inspect` to find that out.

## Server

The server is a Flask application that will listen to `POST` and `GET` requests
on `/screenshot` (`POST`) and `/screenshot/<job_id>` (`GET`).

When `POST`ing, the payload should have a key named `urls` where the value is a
list of URLs. You can find an example at `payload.json`. This request will
return an id that you should use on the `GET` request to retrieve the results.

When making the `GET` request, put the id you received from the `POST` request at
the end of route like this `/screenshot/<job_id>`. This request will return
the results, if they are ready, in the form of a dictionary where the keys are
the URLs that were provided and the values are the screenshots in `base64`
format. If the results are not ready, the response will be a string
corresponding to the status of the job.

To run the server, go to the `server` folder on your terminal and run this:

`docker build . -t screenshot-aas-server`

`docker run -d -e REDIS_IP=<redis_ip> -e RABBIT_IP=<rabbit_ip> -p 5000:5000 screenshot-aas-server`

## Worker

The worker is just a Python script consuming the job queue from RabbitMQ. It
uses the Selenium WebDriver in order to take screenshots of websites.

To run the worker,  go to the `worker` folder on your terminal and run this:

`docker build . -t screenshot-aas-worker`

`docker run -d -e REDIS_IP=<redis_ip> -e RABBIT_IP=<rabbit_ip> screenshot-aas-worker`

## Demo

`curl -H "Content-Type: application/json" -d @payload.json -X POST http://127.0.0.1:5000/screenshot`

`curl http://127.0.0.1:5000/screenshot/<job_id>` where `job_id` is provided by
the first `curl` command.
