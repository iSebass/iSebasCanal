import asyncio
import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import socketio
import webbrowser
from bridge_manager import GatewayBridge
from config_manager import ConfigManager

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Create Socket.IO server
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

# State management
bridge = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global bridge
    loop = asyncio.get_running_loop()
    print(f"DEBUG: Lifecycle started - Initializing Bridge...")
    
    # Callback for Socket.IO status updates from bridge threads
    def on_status(service, state, message):
        asyncio.run_coroutine_threadsafe(
            sio.emit('status', {'service': service, 'state': state, 'message': message}),
            loop
        )

    # Callback for data updates
    def on_data(data):
        asyncio.run_coroutine_threadsafe(
            sio.emit('data', data),
            loop
        )
    
    bridge = GatewayBridge(loop, on_data=on_data, on_status=on_status)
    print("DEBUG: Gateway ready.")
    
    yield
    
    if bridge:
        bridge.stop()
    print("DEBUG: Shutdown complete.")

# Create FastAPI with lifespan
app = FastAPI(lifespan=lifespan)
socket_app = socketio.ASGIApp(sio, app)

# Static files and frontend
static_dir = resource_path("static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def get_index():
    index_path = os.path.join(static_dir, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), media_type="text/html; charset=utf-8")

@app.get("/api/config")
async def get_config():
    return ConfigManager.load()

@app.post("/api/config")
async def save_config(config: dict):
    ConfigManager.save(config)
    return {"status": "success"}

@app.get("/api/bridge/status")
async def get_bridge_status():
    if bridge and bridge.running:
        return {"running": True, "simulation": bridge.simulation_mode}
    return {"running": False}

@app.post("/api/bridge/start")
async def start_bridge(request: Request):
    data = await request.json()
    mode = data.get("mode", "real")
    if bridge and not bridge.running:
        bridge.start(simulation=(mode == "simulation"))
        return {"status": "started", "mode": mode}
    return {"status": "already_running"}

@app.post("/api/bridge/stop")
async def stop_bridge():
    if bridge and bridge.running:
        bridge.stop()
        # Notify UI manually since the workers stop
        await sio.emit('status', {'service': 'serial', 'state': 'offline', 'message': 'Detenido'})
        await sio.emit('status', {'service': 'mqtt', 'state': 'offline', 'message': 'Detenido'})
        return {"status": "stopped"}
    return {"status": "not_running"}

if __name__ == "__main__":
    import uvicorn
    # Open browser after a short delay
    def open_browser():
        time.sleep(1.5)
        webbrowser.open("http://localhost:8000")
        
    import threading
    import time
    threading.Thread(target=open_browser, daemon=True).start()
    
    uvicorn.run(socket_app, host="0.0.0.0", port=8000)
