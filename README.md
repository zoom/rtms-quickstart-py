# 🚀 RTMS Quickstart

This simple app demonstrates integration with the [Zoom Realtime Media Streams SDK](https://pypi.org/project/rtms/) for Python.

[![PyPI](https://img.shields.io/pypi/v/rtms)](https://pypi.org/project/rtms/)
[![docs](https://img.shields.io/badge/docs-online-blue)](https://zoom.github.io/rtms/python/)

## ⚙️ Configuration

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Set your Zoom OAuth credentials:
```bash
ZM_RTMS_CLIENT=your_client_id
ZM_RTMS_SECRET=your_client_secret
```

## 🏃‍♂️ Running the App

Using [uv](https://github.com/astral-sh/uv) (recommended):

```bash
uv run main.py
```

Or manually with pip:

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install .
python main.py
```

For webhook testing with ngrok:

```bash
ngrok http 8080
```

Use the generated ngrok URL as your Zoom webhook endpoint. Then, start a meeting to see your data!

## 🎯 Basic Usage

Here's how you can implement the SDK yourself.

### Import the SDK

```python
import rtms
```

### 🏢 Client-Based Approach

Create a client for each meeting to handle multiple concurrent meetings:

```python
import rtms

clients = {}

@rtms.onWebhookEvent
def handle_webhook(webhook):
    event, payload = webhook.get('event'), webhook.get('payload', {})

    if event == 'meeting.rtms_started':
        client = rtms.Client()
        clients[payload.get('rtms_stream_id')] = client

        @client.onTranscriptData
        def on_transcript(buffer, size, timestamp, metadata):
            print(f"💬 {metadata.userName}: {buffer.decode('utf-8')}")

        client.join(
            meeting_uuid=payload.get('meeting_uuid'),
            rtms_stream_id=payload.get('rtms_stream_id'),
            server_urls=payload.get('server_urls'),
            signature=payload.get('signature')
        )

if __name__ == '__main__':
    import time
    while True:
        for client in clients.values():
            client._poll_if_needed()
        time.sleep(0.01)
```

## 📊 Media Parameter Configuration

Configure audio, video, and deskshare processing parameters before joining:

### 🎵 Audio Parameters

```python
params = rtms.AudioParams(
    content_type=rtms.AudioContentType['RAW_AUDIO'],
    codec=rtms.AudioCodec['OPUS'],
    sample_rate=rtms.AudioSampleRate['SR_16K'],
    channel=rtms.AudioChannel['STEREO'],
    data_opt=rtms.AudioDataOption['AUDIO_MIXED_STREAM'],
    duration=20,      # 20ms frames
    frame_size=640    # 16kHz * 2 channels * 20ms
)
client.setAudioParams(params)
```

### 📹 Video Parameters

```python
params = rtms.VideoParams(
    content_type=rtms.VideoContentType['RAW_VIDEO'],
    codec=rtms.VideoCodec['H264'],
    resolution=rtms.VideoResolution['HD'],
    data_opt=rtms.VideoDataOption['VIDEO_SINGLE_ACTIVE_STREAM'],
    fps=30
)
client.setVideoParams(params)
```

### 🖥️ Deskshare Parameters

```python
params = rtms.DeskshareParams(
    content_type=rtms.VideoContentType['RAW_VIDEO'],
    codec=rtms.VideoCodec['H264'],
    resolution=rtms.VideoResolution['FHD'],
    fps=15
)
client.setDeskshareParams(params)
```

## 📞 Available Callbacks

- `@client.onJoinConfirm` - ✅ Join confirmation
- `@client.onSessionUpdate` - 🔄 Session state changes
- `@client.onUserUpdate` - 👥 Participant join/leave
- `@client.onParticipantEvent` - 👥 Participant join/leave (typed)
- `@client.onActiveSpeakerEvent` - 🎤 Active speaker changes
- `@client.onSharingEvent` - 🖥️ Screen sharing start/stop
- `@client.onAudioData` - 🎵 Audio data
- `@client.onVideoData` - 📹 Video data
- `@client.onTranscriptData` - 💬 Live transcription
- `@client.onLeave` - 👋 Meeting ended

## 📚 API Reference

For complete parameter options and detailed documentation:

- 🎵 **[Audio Parameters](https://zoom.github.io/rtms/python/)** - Complete audio configuration options
- 📹 **[Video Parameters](https://zoom.github.io/rtms/python/)** - Complete video configuration options
- 🖥️ **[Deskshare Parameters](https://zoom.github.io/rtms/python/)** - Complete deskshare configuration options
- 📖 **[Full API Documentation](https://zoom.github.io/rtms/python/)** - Complete SDK reference
