# Quick Start Demo Guide

## Running the Full Demo

### Step 1: Start the Server
```bash
uvicorn server.server:app --host 0.0.0.0 --port 8000
```

### Step 2: Start the Node Daemon (in another terminal)
```bash
python -m node.node_daemon
```

### Step 3: Test the API

**Get Random Hex Data (32 bytes):**
```bash
curl "http://localhost:8000/v1/random?bytes=32&format=hex"
```

**Get Random Base64 Data (64 bytes):**
```bash
curl "http://localhost:8000/v1/random?bytes=64&format=b64"
```

**Check System Status:**
```bash
curl "http://localhost:8000/v1/status" | python -m json.tool
```

**Check Node Configuration:**
```bash
curl "http://localhost:8000/v1/nodes/node-001/config" | python -m json.tool
```

## Quick Test Script

```bash
# Run all demo commands
echo "=== Starting Demo ==="
echo ""
echo "1. System Status:"
curl -s "http://localhost:8000/v1/status" | python -m json.tool
echo ""
echo "2. Random Hex (32 bytes):"
curl -s "http://localhost:8000/v1/random?bytes=32&format=hex" | python -m json.tool
echo ""
echo "3. Random Base64 (64 bytes):"
curl -s "http://localhost:8000/v1/random?bytes=64&format=b64" | python -m json.tool
echo ""
echo "=== Demo Complete ==="
```

## Running Tests

```bash
pytest tests/ -v
```

## Configuration

Edit `config.yaml` to customize:
- Node ID
- Server URL
- Buffer capacity
- Upload chunk size
- Heartbeat interval

## Expected Results

- ✅ Server starts on port 8000
- ✅ Node connects and starts generating
- ✅ API returns random data immediately
- ✅ All tests pass (6/6)
- ✅ Zero errors in logs
