# Introduction to Repo
The goal of this page is to explain the execution flow whenever you start the app. 

## Basic app
Let's first look at the most basic flask app
```Python
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<h1>Hello World!</h1>"

if __name__ == "__main__":
     app.run()
```
Pretty simple code... When you run `python <file name>`, you start the flask server because it sets up `app` and executes `app.run()`. Remember that whenever you run a python file, it runs top to bottom, and it will execute whatever is under [`if __name__ == "__main__"`](https://thepythonguru.com/what-is-if-__name__-__main__/). 

## Now, obviously, we wouldn't want to put everything in one file...
You always want your code to flow well and be readable based on the logic and dependencies of your application. For many applications, especially building out REST APIs with Postgres, we want to split out the **models**( which describe our interaction with the database tables), as well as splitting out the **endpoints** (based on what the endpoints are written for (authentication, different resources?, etc.)). 

Thus, like many other projects, this repo puts the entire flask application in one folder, which I name `api`. And, for the reasons mentioned above, we should also split up the database model abstractions and the endpoints into `models` and `views` folders. 

## Python's import system
So, how do we move the same executions as shown by the initial code and move it over to this new structure?

First, we must understand [python's import system](https://docs.python.org/3/reference/import.html). In python, whenever a folder has `__init__.py`, it is a package. Whenever you import the package, the code in `__init__.py` will be executed. Whenever you import a file, you will also execute whatever is in that file. Remember that python is an interpreted language, and if you provide any code instructions in the file, it will execute. Obviously, if you define functions or classes, they won't execute... but if you have a print statement outside of any defined function/class, it will execute once -- when you import it the first time in the scope of your application's execution. 

So, say you had a module mypackage:
```
package/
    __init__.py
    app.py
```
When you do `from mymodule import app` the first time, it will execute whatever is in `package/__init__.py` and put the variables, functions, etc into its namespace. If you import other modules (files) in `__init__.py`, they will also be imported and executed. Thus, whatever instructions are in `package/app.py` will be executed.

## In the case of this repo
In this repo, we have 
```
api/
    __init__.py
    models/
        __init__.py
    views/
        __init__.py
```
Inside `api/__init__.py`, we see the function `create_app`. This function creates the app, the same way the simple code above did it, and sets up logging, flask blueprints, database connections, as well as the [application configuration](http://flask.pocoo.org/docs/1.0/config/) (`app.config`). We have different application configurations, which is chosen through the environment variable `FLASK_ENV` and taken from the file `api/config.py`, which describes different types of configurations. Most of the setup is pretty straightforward, but I'd love to discuss flask blueprints and the database connection a little more.

#### Database
As mentioned everywhere in this documentation, we use SQLAlchemy to interact with postgres. It wraps SQL tables as Python objects so we easily and safely work with the database, instead of injecting SQL commands. [Flask-SQLALchemy](http://flask-sqlalchemy.pocoo.org/latest) simplifies the connection process by allowing us to connect to postgres with the command
```
db = SQLAlchemy()
```
However, you must be **inside the [flask application context](http://flask.pocoo.org/docs/1.0/appcontext/)**, which keeps track of application-level data (including the app config). This is because Flask-SQLAlchemy looks into the app config and finds `SQLALCHEMY_DATABASE_URI`, which should hold the url to the database and tries to connect to it. This is why we don't import `api.models` outside of `create_app`, since the line `db = SQLALchemy()` is called whenever you import `api.models`. **We import it `api.models` the flask app is instantiated.** 

For tests, we setup a temporary postgres database, get it's URL and then set `SQLALCHEMY_DATABASE_URI` in the test app config to be that url... and the process happens over again, but with the [flask test client](http://flask.pocoo.org/docs/1.0/testing/)


#### [Blueprints](http://flask.pocoo.org/docs/1.0/blueprints/)
Blueprints extends the flask app object itself, which we use in the modules inside `views/`, such as `api/views/main.py`. We must tell the flask app instance that we have this blueprint and it's logic, which is through the `app.register_blueprint` function.

## Conclusion
To wrap it up, whenever you run `python manage.py runserver` you would create the app (look at `manage.py`), which would instantiate the flask app, setup logging, connect to the database, etc, and then run it (look at the function `runserver` in `manage.py`. It's very similar to the last line of the simple code we have above). 

For more on python code structure, look [here](https://docs.python-guide.org/writing/structure/). For the official documentation on code structure for large applications, look [here](http://flask.pocoo.org/docs/0.12/patterns/packages/)

# Getting Started (Docker 101)
We will be utilizing Docker to provide the same development environment across your team. This will eliminate aggravating environment troubleshooting in different Operating Systems. 
## Prereqs
- [Docker](https://docs.docker.com/engine/installation/#time-based-release-schedule) – if you are running Linux, install the Server version and install [Docker-Compose](https://docs.docker.com/compose/install/#install-compose).
And that's it! For Mac, you will see a Docker icon on the top bar, indicating that docker is running. 
## Understanding Docker
Docker is a powerful tool that allows you to spin up containers(isolated and reproducible application environments), thus, allowing independence between applications and the infrastucture(ie your OS). 
For in-depth information, check out the [Docker Docs](https://docs.docker.com/get-started/)<br>
- **Docker Images**, what you get when you ```docker-compose build```. They are snapshots of your code at that certain time. This describes a container
- **Docker Containers** are instances of images. You can see the containers you are running with ```docker ps```
- **Docker Compose** is a tool for running multi-container applications with Docker. In our case, we use it to spin up ```app``` and ```postgres``` containers. 
## Our Docker Configuration
We have two Docker Images: 
- ```app```: Our Flask Application
- ```postgres```: Postgres Database<br>
Note: A docker volume will be created to persist the Postgres data. You may remove it by using `docker volume prune`. However, you must remove the container using it (`app`) with the command `docker rm app`.
## Setup
Check if you have installed **Docker** and **Docker-Compose**(Installing Docker on Mac/Windows will automatically install Docker-Compose):
```
$ docker -v
Docker version 17.09.1-ce, build 19e2cf6
$ docker-compose -v
docker-compose version 1.17.1, build 6d101fb
```
Now build the Docker images(the flask app and postgres database) and setup the database:
```
$ docker-compose up -d
```
Check if your Docker Containers are running:
```
$ docker ps
```
Now go to ```http://localhost:5000``` and you should see the app running! Since it is in development configurations, any changes in your code will appear in the container and will auto-reload just like it would normally. 
## Running and Stopping Docker Containers
To start your Postgres and your flask api:
```
$ docker-compose start
```
To stop them:
``` 
$ docker-compose stop
```
To view your logs for the api:
```
$ docker-compose logs app
```
If you need to rebuild your containers, delete the previous containers and rebuild
```
$ docker-compose rm -f
$ docker-compose up -d
```
#### NOTE: Be careful to not run multiple containers of the same image. Check with ```docker ps``` and use ```docker-compose stop``` to stop all the containers if you are running multiple containers and restart. 
## Docker and Databases
Any commands, such as ```python manage.py db migrate``` **MUST** be performed inside the ```app``` Docker Container. If you need to access the postgres CLI, you MUST be inside the ```postgres``` Docker Container. <br>
#### Migrating the database
You must access the ```app``` container's bash. You will then see your app directory copied inside: 
```
$ docker-compose exec app bash
# ls
Dockerfile  Procfile   __pycache__  config.py		docs	   postgres-data     runtime.txt  venv
LICENSE     README.md  api	    docker-compose.yml	manage.py  requirements.txt  tests	  wait-for-postgres.sh
```
Then initalize migration files and migrate
```
# python manage.py db init
# python manage.py db migrate
# python manage.py db upgrade
# exit
```
#### Accessing Postgres CLI
You must access the ```postgres``` container's bash. 
```
$ docker-compose exec postgres bash
```
Then, you can ```psql``` inside and delete tables, databases, etc.
```
# su - postgres
$ psql
```

## Wiping all Docker Containers and Starting all over again
If you've given up trying to troubleshoot whatever is going wrong in Docker, here's a way to start all over. 

First, stop the postgres container that you are running. Then, delete the postgres container. I like to just use `docker system prune` to delete all unused containers. Afterwards, we need to delete the volume persisting all of the database data.
```
$ docker volume rm flask-app-db
```

If you are using docker-compose, then delete all your related Docker Images and Containers
```
$ docker-compose stop
$ docker-compose rm
$ docker rmi $(docker images)
```
Now follow the setup steps again
## Common Docker commands
Stop the API and Postgres Containers
```
docker-compose stop
```
List all Containers:
```
$ docker ps
```
Stop all Containers:
```
$ docker stop $(docker ps -a)
```
Remove all images:
```
$ docker rmi $(docker images -q)
```
To get all images
```
$ docker images
```
Remove specific images:
```
$ docker rmi [IMAGE_ID]
```
Bash in a certain container, ie: ```api```
```
$ docker-compose run api bash
```
You can also run bash if you have the container's id. To get a container's id, do ```docker ps```
```
$ docker exec -it [CONTAINER_ID] /bin/bash
```
Or run a specific bash command, id: ```ls```
```
$ docker exec -it [CONTAINER_ID] ls
```
Remove 
- all stopped containers
- all volumes not used by at least one container
- all networks not used by at least one container
- all images without at least one container associated to them
```
$ docker system prune
```

Show all stopped Docker containers
```
$ docker ps -a | grep Exit
```
# Tests
Tests are a very important part of software development. Untested applications make it hard to improve existing code and creating new features without knowing whether you've regressed or not. Note that there should be integration tests if there are multiple services to your application. For the official documentation on Flask testing, look [here](http://flask.pocoo.org/docs/1.0/testing/). In addition, [here's](https://docs.python-guide.org/writing/tests/) a good document on testing in python.

I've provided unit tests in the `tests/` folder, which uses [pytest](https://docs.pytest.org/en/latest/) to execute tests. The tests spins up a temporary postgres instance and connects the flask test client to it. This means that with the same code and same versions of dependencies, it should produce the same result. So, you can't have a persisting postgres database that you use in your tests because if you added a row to a Table, the tests may return a different result. Instead of stubbing SQLAlchemy, which is very cumbersome and difficult in my opinion, it's much easier to spin up a temporary database that SQLAlchemy would connect to. With testing, you want to figure out whether the code you wrote works, and generally when errors occur, it's probably not some complex database incompatibility issue, it's probably something that you wrote incorrectly.

To run the tests, do:
```
$ pipenv install --dev
$ pipenv run pytest tests
```
or do `pipenv shell` and blah blah blah
