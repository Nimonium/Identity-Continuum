import asyncio
import json
import websockets

async def execute_ws_scenario(scenario_name):
    uri = "ws://127.0.0.1:8000/ws/verification-stream"
    print(f"\n--- Testing Scenario: {scenario_name} ---")
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({"scenario": scenario_name}))
        while True:
            msg = await ws.recv()
            data = json.loads(msg)
            event = data.get("event")
            if event == "PIPELINE_COMPLETE":
                res = data.get("data", {}).get("result") or data.get("result")
                score = res["trust_evaluation"]["identity_trust_score"]
                intact = res["trust_evaluation"]["is_trust_chain_intact"]
                broken = res["trust_evaluation"]["broken_layer"]
                tamper = res["forensics"]["is_tampered"]
                fracture = res["fracture_detected"]
                print(f"[{scenario_name.upper()}] Trust Score: {score:.1f}/100 | Intact: {intact} | Broken Layer: {broken} | Tamper: {tamper} | Fracture: {fracture}")
                print(f"Total Latency: {data.get('latency_ms') or data.get('total_latency_ms')}ms")
                break

async def main():
    for sc in ["clean", "tampered", "fracture"]:
        await execute_ws_scenario(sc)
    print("\nALL 3 SCENARIOS STREAMED SUCCESSFULLY VIA WEBSOCKET!")

if __name__ == "__main__":
    asyncio.run(main())
