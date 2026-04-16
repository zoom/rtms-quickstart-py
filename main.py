import rtms
from dotenv import load_dotenv

load_dotenv()

clients = {}


@rtms.on_webhook_event
def handle_webhook(webhook):
    event = webhook.get('event')
    payload = webhook.get('payload', {})
    stream_id = payload.get('rtms_stream_id')

    if event == 'meeting.rtms_stopped':
        client = clients.pop(stream_id, None)
        if client:
            client.leave()
        return

    if event != 'meeting.rtms_started':
        return

    client = rtms.Client()
    clients[stream_id] = client

    @client.on_transcript_data
    def _(data, _, timestamp, metadata):
        print(f'[transcript] ts={timestamp} user="{metadata.userName}": {data.decode()}')

    client.join(payload)


rtms.run()