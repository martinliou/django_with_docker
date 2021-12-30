import asyncio
import websockets

async def client_test(uri):
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            print(f"(client) recv from server {message}")

asyncio.get_event_loop().run_until_complete(
    client_test('ws://127.0.0.1:5566'))