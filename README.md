# BDIX IPTV

A curated IPTV playlist of Bangladeshi and international live TV channels, in M3U format. Works with any IPTV player that supports M3U playlists (VLC, TiviMate, IPTV Smarters, Kodi, and others).

## Playlist

| File | Description |
| --- | --- |
| [`bdix/playlist.m3u`](bdix/playlist.m3u) | Main playlist — **326 channels** |
| [`bdix/Channels_data.json`](bdix/Channels_data.json) | Channel data in JSON format (43 featured channels) |

Use the raw playlist URL in your player:

```
https://raw.githubusercontent.com/tunnabri-ops/BDIX-IPTV/main/bdix/playlist.m3u
```

## Categories

Bangla, Sports, News, Kids, Hindi, English, Indian Bangla, Religious, Music, Radio, Cricket, Football, and more.

## How to use

1. Copy the raw playlist URL above.
2. Open your IPTV player and add a new playlist from URL.
3. Paste the URL and save. Channels load automatically.

In VLC: Media → Open Network Stream → paste the URL → Play.

## Updates

The playlist is refreshed automatically every 6 hours by a GitHub Actions workflow (`.github/workflows/main.yml`), so new channels appear without a manual update. Just reload the playlist in your player. After every sync, `scripts/cleanup_playlist.py` cleans the playlist automatically — it removes exact-duplicate entries, drops orphan lines, fixes invalid URL schemes, and tidies channel names, so the published file stays valid. It never removes a stream for failing a check.

## Disclaimer

This repository does not host any content. It aggregates publicly available streams for informational and testing purposes only. All trademarks and channel names belong to their respective owners. If you are a rights holder and want a stream removed, please open an issue.
