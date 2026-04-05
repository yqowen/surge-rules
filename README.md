# surge-rules

Auto-generated Surge rule files, starting with Zoom.

## Files

- `zoom/Zoom.list` — full list generated from official Zoom TXT files
- `zoom/ZoomLite.list` — lightweight curated variant for personal use

## Upstream sources

Current generator uses official Zoom TXT endpoints:

- `https://assets.zoom.us/docs/ipranges/Zoom.txt`
- `https://assets.zoom.us/docs/ipranges/ZoomApps.txt`

## Automation

GitHub Actions runs on schedule and on manual dispatch:

- scheduled daily at `02:15 UTC`
- can also be triggered from the Actions tab

## Surge example

```ini
[Rule]
RULE-SET,zoom,Zoom
RULE-SET,zoom-lite,Zoom

[Rule Provider]
zoom = type=http,behavior=classical,interval=86400,url=https://raw.githubusercontent.com/yqowen/surge-rules/main/zoom/Zoom.list,path=zoom.list
zoom-lite = type=http,behavior=classical,interval=86400,url=https://raw.githubusercontent.com/yqowen/surge-rules/main/zoom/ZoomLite.list,path=zoom-lite.list
```

## Regeneration locally

```bash
python3 scripts/update_zoom.py
```
