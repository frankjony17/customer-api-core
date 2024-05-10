# python-microservice-template

[![Build Status](https://travis-ci.com/alichtman/shallow-backup.svg?branch=master)](https://travis-ci.com/alichtman/shallow-backup)

`python-microservice-template` simple template with  tools, written for python microservices.

Contents
========

* [Why?](#why)
* [Folders?](#folders)
* [Installation](#installation)
* [Configuration](#configuration)
* [Want to contribute?](#want-to-contribute)

### Why?

I wanted a tool that allows you to:

* Create new python-template for your microservice _from where they live on the system_.
* Create python ecosystem with tooling and feats.
* Facilitate setup new project with some tools already configurated.
* Create patterns about our softwares.

And is incredibly fast.

### Folders

| domain        | details                                                                                                                   |   |
|---------------|---------------------------------------------------------------------------------------------------------------------------|---|
| exceptions.py | Here we declare every domain exceptions, used only in this context                                                        |   |
| model.py      | Here we declare every models of database connections.                                                                     |   |
| repository.py | Here we create all connections with database, queries, insertions and manipulation in data.                               |   |
| schema.py     | Here we declare every schemas of our service, and validations.                                                            |   |
| service.py    | Here we create every handlers of routes, our services should connect routers with database and domain/schemas validations |   |

### Installation

---

> **Warning**
> Be careful running this with elevated privileges. Code execution can be achieved with write permissions on the config file.
> Verify if you put corrects .envs

### Before the methods

```bash
git clone git@github.com:frankjony17/fastapi-backend-template.git
cd fastapi-backend-template
```

#### Method 1: [`docker-compose`](https://docs.docker.com/compose/)

```bash
docker compose up
```

#### Method 2: Install From Source

```bash
make postgres

make install

make debug
make run
```

### Configuration

If you'd like to modify which files are backed up, you have to edit/create new domains and routers and add some logic in boths.

#### .gitignore

In .gitignore we will discart every `envs` `dependencies` and ``.

#### Output Structure

---

```shell
fastapi-backend-template/
├── domain
│ ├── common
│ │ └── *_base.py
│ ├── domain_1
│ │ └── ...
│ └── domain_2
│     └── ...
├── routers
│   ├── router_1.py
│   └── healthcheck.py
├── internal
│ ├── config
│   │   └── *_base.py
│   ├── kafka
│   │   └── *_base.py
│ ├── utils.py
│ └── others.py
├──
tests/
│ all.py
└── all.txt
```

## Testing

Three objects for testing:

1. Integration testing: Routers meet the requriements and peform the required actions in an evironment that is as close to a production environment as possible.
2. Migration testing: Migrations that change the state of the database should work without errors.
3. Unit testing: Critical business logic functions should also be coveved by unit tests.

We will need a database fixture that creates a separate database before executing each test, and delete it after exectuion.

We will need databases in different states: testing migrations requires a clean database, while testing routes require all migrations to be applied. We an change the state of the database programmatically using Alembic commands. For that, we will need a Alembic configuration object fixture.

When there are a lot of migrations, applying them to each test will take too much time. Therefore, we will need a migrated database fixture.

Here is the testing workflow:

1. The fixture `migrated_postgres_template` will create the database (dependency for `migrated_postgres`).
2. The fixture `alembic_config` will create an Alembic configuration object connected to the temporary database (dependency for `migrated_postgres`).
3. The fixture `migrated_postgres_template` will apply the migrations.
4. The fixture `app` will return the application.
5. The fixture `api_client` will return the client to make requests.
6. The test will run.
7. The fixture `api_client` will disconnect the client and stop the application.
8. The fixture `migrated_postgres_template` will delete the database.

Fixture help us prepare the test environment, but also help us avoid code duplication. Another potential step in which there will be a lot of duplicated code is when making requests to the application. When we make a request, we receive an HTTP status. If the status is as expected we need to make sure the response is in the correct format (e.g., the response is wrapped in a dictionary with a key `data`). We can use Marshmallow to check the HTTP status and response in each integration test function.

### Migration Testing

#### Technical Note

We need to rum alembic programmatically to test migrations. Internally, the `upgrade` and `downgrade` commands in alembic uses `asyncio.run` to run migrations via `asyncpg` driver. That's fine if running from CLI, however pytest runs tests inside an `asyncio` event loop, so therefore we cannot use `asyncio.run`. Since we don't want to rewrite alembic's internals, we need to run an async function from the sync [`run_migrations_online`](./migrations/env.py) while an event loop is already runing.

So we first check if there is an event loop running. If not, we just create one with `asyncio.run(run_migrations_online())`. If there is, meaning we are inside a test, we add attach a task to the current event loop with `asyncio.create_task`. The major problem is that we need to await for this task inside our pytest fixture, but the task is created when we ran alembic's `upgrade`. The current solution (due to failure of finding a more elegant solution) was to add a new global variable to [`conftest.py`](./tests/conftest.py) and set it from alembic.

Finally, when we run `upgrade`, alembic loads data into the `context` object using the `EnvironmentContext` object. Inside of it it runs the `script.run_env()` command whihc loads `migrations/env.py` which runs `run_migrations_online()`. Since we crated an `asyncio.Task` and it returns from `run_migrations_online()`, it endes the context manager and clears the `context` object. Therefore, when we try to run from inside the task context is None. We need to pass the context object into our task. We use `contextvars`. We create teh contexvars before creating the task so the task has access to them.

Although cumbersome, this setup allows to run everything using the `asyncpg` driver, including alembic migrations. The entire testing setup is async and parallelizable, meaning we can use `pytest-xdist` to split our test suite into chunks and run each chunk in different processes. It works without problems, because, on top of all we discussed so far, we create a unique test database for each test.

#### Stairway test

Simple and efficient method to check if migration does not have typos, rolls back all schema changes (no forgotten downgrade methods or undeleted data types) and many other errors. Does not require maintenance---you can add this test to your project once and forget about it.

In particular, test detects the data types, that were previously created by `upgrade` method and were not removed by `downgrade`: when creating a table or column, Alembic automatically creates custom data types specificed in columns (e.g., enum), but does not delete them when deleting table or column---currently, developer has to do it manually.
For now, using [this workaround](https://github.com/sqlalchemy/alembic/issues/89#issuecomment-1456195426).
Here is an [example in code](./migrations/versions/2024_04_05_0744_17__aad3da757bf9_add_example_table.py#L60).

##### How it works

Test retrieves all migrations list, and for each migration executes `upgrade`, `downgrade`, `upgrade` Alembic commands.

![Stairway test](assets/stairway.gif)

## Database

### Session Manager

We use a singleton database session manager (`DatabaseSessionManager`) for abstracting database connection and session handling.

We use init and close methods in FastAPI's lifespan event, to run it during startup and shutdown of our application.

The benefits of this approach are:

* In theory, you can connect to as many databases as you need, just create different SessionManager for each database. Here we are strictly using the Database Session Manager as a singleton.
* Your DB connections are released at application shutdown instead of garbage collection, which means you won't run into issues if you use `uvicorn --reload`.
* Your DB sessions will automatically be closed when the route using session dependency finishes, so any uncommitted operations will be rolled back.

### Alembic

Add all your models to the dunder init file in the [`db` module](./python_api_template/db/__init__.py). This approach not only simplifies the distrintion between the ORM and Business models, but also make sure all the database mdoels are imported and added to SQLAlchemy's `Base.metadata` object before the alembic configuration is loaded. This is done by importing `BaseOrmModel` in [alembic's `env.py`](./migrations/env.py).

### Want to Contribute?

---

Check out `CONTRIBUTING.md` and the `docs` directory.
