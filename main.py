import rtms
from dotenv import load_dotenv

load_dotenv()

# Store active clients by stream ID (equivalent to JS Map)
clients = {}


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

    # Create a new RTMS client for this stream
    client = rtms.Client()
    clients[stream_id] = client

    @client.onTranscriptData
    def on_transcript(data, size, timestamp, metadata):
        print(f'[{timestamp}] -- {metadata.userName}: {data.decode("utf-8")}')

    # Join the meeting
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
            for client in clients.values():
                client._poll_if_needed()
            time.sleep(0.01)
    except KeyboardInterrupt:
        pass
