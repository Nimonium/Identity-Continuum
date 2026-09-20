import asyncio
import json
import websockets

async def main():
    uri = "ws://127.0.0.1:8000/ws/verification-stream"
    print(f"Connecting to {uri}...")
    async with websockets.connect(uri) as ws:
        print("Connected! Sending verification payload...")
        await ws.send(json.dumps({"scenario": "clean"}))
        
        while True:
            msg = await ws.recv()
            data = json.loads(msg)
            event = data.get("event")
            progress = data.get("progress")
            latency = data.get("latency_ms")
            summary = data.get("summary") or data.get("message") or ""
            p_str = f"{progress}%" if progress is not None else "--"
            lat_str = f"{latency}ms" if latency is not None else "--"
            print(f">> [{event:<30}] {p_str:>5} | Latency: {lat_str:<10} | {summary}")
            
            if event == "PIPELINE_COMPLETE":
                print("\n==========================================")
                print(f"Total Verification Latency: {data.get('total_latency_ms')} ms")
                print("Module-by-Module Latency Breakdown:")
                for k, v in data.get("latency_breakdown_ms", {}).items():
                    print(f"   * {k:<30}: {v:>6.2f} ms")
                print("==========================================")
                break

if __name__ == "__main__":
    asyncio.run(main())
