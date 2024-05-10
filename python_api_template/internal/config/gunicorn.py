import multiprocessing

from python_api_template.internal.config.logger import Logger
from python_api_template.internal.config.settings import global_settings

# Host and port
bind = global_settings.gunicorn.bind

# Workers
worker_class = global_settings.gunicorn.worker_class
workers_per_core = global_settings.gunicorn.workers_per_core
cores = multiprocessing.cpu_count() // 2
default_web_concurrency = workers_per_core * cores
default_web_concurrency = max(int(default_web_concurrency), 4, key=int)
workers = global_settings.gunicorn.workers or default_web_concurrency

# Logs
logger_class = Logger

# Timeouts
keepalive = global_settings.gunicorn.keepalive
graceful_timeout = global_settings.gunicorn.graceful_timeout
timeout = global_settings.gunicorn.timeout

# WSGI application path
wsgi_app = global_settings.gunicorn.wsgi_app

# Debug Gunicorn configurations
log_data = {
    "bind": bind,
    "worker_class": worker_class,
    "workers_per_core": workers_per_core,
    "cores": cores,
    "workers": workers,
    "keepalive": keepalive,
    "graceful_timeout": graceful_timeout,
    "timeout": timeout,
    "wsgi_app": wsgi_app,
}
