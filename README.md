# Screenshot-as-a-Service

This application is a backend component responsible for taking screenshots
of URLs provided by users. The server endpoints and the workers (the ones that
take screenshots) are separated by a job queue using RabbitMQ.

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

To see that the application is working, run `pip install requests` and run the
`client.py` script. You can edit the payload at `payload.json`.

The script will save the screenshots to a `screenshots/` folder.

## Scaling It

Since taking screenshots is not a cheap job, to scale this application it might
be a good idea to run multiple workers. Since the worker is in a container
image, we can just run more containers to accelerate the task of taking
screenshots.

If our problem is also having a lot of concurrent users, we can also scale the
server by having more containers of it. For that, we would also need a load
balancer to distribute the load.

By putting all of this together, we could use Kubernetes to orchestrate all of
this. With it, we could have the load balancer, the wiring of all the
containers together (including Redis and RabbitMQ) and also a horizontal pod
autoscaler.

## Scaling It (With Changes)

We could change some design decisions to scale this application a bit more.
For example, we could store the image data on Redis and use it like a cache,
but that depends if we always want to offer the most recent image to the user.
A good trade-off would be to use a cache but delete the image after 5 minutes
(for example).

If we did that, we could also benefit from using references and pointers inside
Redis to avoid duplicating image data and save more disk. For instance, if Bob
requests a screenshot of `google.com` but Alice requested it as well 1 minute
ago, we could just return that data instead of taking a new screenshot.
