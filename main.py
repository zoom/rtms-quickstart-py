import rtms
import threading
from dotenv import load_dotenv

load_dotenv()

# Store active clients by stream ID
clients = {}

# Queue for pending client setups (webhook thread -> main thread)
pending_setups = []
pending_lock = threading.Lock()


@rtms.onWebhookEvent
def handle_webhook(webhook):
    event, payload = webhook.get('event'), webhook.get('payload', {})
    stream_id = payload.get('rtms_stream_id')

    if event == 'meeting.rtms_stopped':
        if not stream_id:
            print('Received meeting.rtms_stopped event without stream ID')
            return
        client = clients.get(stream_id)
        if not client:
            print(f'Received meeting.rtms_stopped event for unknown stream ID: {stream_id}')
            return
        client.leave()
        del clients[stream_id]
        return

    if event != 'meeting.rtms_started':
        print('Ignoring unknown event')
        return

    # Queue this for processing on main thread (client creation must happen there)
    with pending_lock:
        pending_setups.append(payload)


def process_pending_setups():
    """Process pending client setups - must be called from main thread"""
    with pending_lock:
        if not pending_setups:
            return
        setups = pending_setups[:]
        pending_setups.clear()

    for payload in setups:
        stream_id = payload.get('rtms_stream_id')

        # Create client on main thread so _main_thread_id is correct
        client = rtms.Client()
        clients[stream_id] = client

        @client.onTranscriptData
        def on_transcript(data, size, timestamp, metadata):
            print(f'[{timestamp}] -- {metadata.userName}: {data.decode("utf-8")}')

        # Join (now _process_join_queue isn't needed since we're on main thread)
        client.join(
            meeting_uuid=payload.get('meeting_uuid'),
            rtms_stream_id=payload.get('rtms_stream_id'),
            server_urls=payload.get('server_urls'),
            signature=payload.get('signature')
        )


if __name__ == '__main__':
    import time
    try:
        while True:
            process_pending_setups()
            for client in list(clients.values()):
                client._poll_if_needed()
            time.sleep(0.01)
    except KeyboardInterrupt:
        for client in clients.values():
            client.leave()
