# Ugoki API Server

Ugoki is a simple server for storing categorized gifs where anyone can suggest
gifs but the owner can approve them only.

## Usage

### Production

To install the last stable version, simply run

```
$ pip install ugoki
```

To start a ugoki API server, run `ugoki-prod` with correct arguments.

```
$ ugoki-prod -h
usage: ugoki-prod [-h] [-p PORT] [-H HOST] STORAGE SERVE_ROOT AUTH_USER AUTH_PASSWORD DB_STRING

positional arguments:
  STORAGE               Path to store gifs
  SERVE_ROOT            Root where the gifs are served by the web server
  AUTH_USER             Username for API
  AUTH_PASSWORD         Password for API
  DB_STRING             String to connect to database. (e.g. sqlite:///ugoki.sqlite)

optional arguments:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  Port to listen on. Default: 8000
  -H HOST, --host HOST  Host to listen for. Default: 127.0.0.1
```

### Development

- `git clone https://gitlab.com/ceda_ei/ugoki.git/`
- `cd ugoki`
- `poetry install`
- `poetry shell`
- `ugoki-dev`
