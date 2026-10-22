# Mixtape search helper

YouTube search for Mixtape that uses no API key and no quota. It runs `yt-dlp` on your computer.

## Run it

```
pip install yt-dlp
python mixtape_search.py
```

Leave the window open while you DJ. If searches start failing, YouTube has changed something; update with `pip install -U yt-dlp`.

## How Mixtape uses it

Mixtape's `dj.js` checks for the helper at `http://127.0.0.1:8765` whenever you search. It uses the helper for both the 🔍 search window and the overnight music-video run. The search window then shows "search helper on · no daily limit".

When the helper isn't running, Mixtape uses your YouTube search key as before (about 100 searches a day). Without a key, the helper alone is enough.

One difference: the helper can't filter out videos whose owners block playback outside YouTube. If you pick one of those, the player shows its usual "can't play this video" message. The overnight run then tries the next match from the same search.
