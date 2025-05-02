import requests
import sseclient
import json

# Endpoint to connect to
url = 'http://localhost:5002/process_dispute_sse'

# Your request payload
payload = {
    "dispute": "Delayed payment after contractual work was completed"
}

# Send the POST request and set up the SSE stream
headers = {'Content-Type': 'application/json'}
response = requests.post(url, data=json.dumps(payload), headers=headers, stream=True)
client = sseclient.SSEClient(response)

# Buffers for capturing memo content
initial_memo_chunks = []
final_memo_full = []

print("\n--- START STREAM ---\n")

for event in client.events():
    print(f"Event: {event.event}")
    print(f"Data: {event.data}\n")

    if event.event == "partial_memo":
        initial_memo_chunks.append(event.data)

    elif event.event == "final_memo":
        final_memo_full.append(event.data)

    elif event.event == "done":
        break

print("\n--- FINAL OUTPUT ---")
initial_memo = "".join(initial_memo_chunks)
print("\n🔹 Initial Memo:\n", initial_memo)
print("\n🔹 Final Memo:\n", final_memo_full)
