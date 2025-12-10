# RNGaaS - Random Number Generator as a Service

A minimal but production-ready PoC for a distributed random number generation service.

## Architecture

- **Node Daemon**: Generates entropy, conditions it via SHA-256, buffers it, and uploads to central server
- **Central Server**: Aggregates random data from nodes and serves it via REST API

## Quick Start

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Server

```bash
uvicorn server.server:app --reload
```

Server runs on http://localhost:8000

### Run Node Daemon

```bash
python -m node.node_daemon
```

Configure via `config.yaml`

### Run Tests

```bash
pytest tests/
```

## API Endpoints

### Client Endpoints

- `GET /v1/random?bytes=32&format=hex` - Get random bytes
- `GET /v1/status` - Get system status

### Node Endpoints

- `POST /v1/nodes/{node_id}/chunks` - Upload random data
- `POST /v1/nodes/{node_id}/heartbeat` - Send health status
- `GET /v1/nodes/{node_id}/config` - Get node configuration

## Example Usage

```bash
curl "http://localhost:8000/v1/random?bytes=32&format=hex"
curl "http://localhost:8000/v1/status"
```
