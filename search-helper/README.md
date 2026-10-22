# Mixtape search helper

YouTube search for Mixtape that uses no API key and no quota. It runs `yt-dlp` on your computer.

## Run it

```
pip install yt-dlp
python mixtape_search.py
```

Leave the window open while you DJ. If searches start failing, YouTube has changed something; update with `pip install -U yt-dlp`.

## Use it from Mixtape

Paste this into Mixtape's script. It tries the helper first and only falls back to the official API (100 searches a day) if the helper isn't running:

```js
async function ytSearch(q, n = 10) {
  try {
    const r = await fetch('http://127.0.0.1:8765/search?n=' + n + '&q=' + encodeURIComponent(q));
    const j = await r.json();
    if (j.ok) return j.items;            // [{id, title, author, dur, thumb}]
  } catch (e) { /* helper not running */ }
  return apiSearch(q, n);                // your existing YouTube Data API search, mapped to the same shape
}
```

Then play a result exactly as before: `player.postMessage({mx:'load', id: item.id, play: true}, '*')`.
