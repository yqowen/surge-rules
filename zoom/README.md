# Zoom Surge Rule

A cleaned Zoom rule list for Surge / rule-provider usage.

## Files

- `Zoom.list` — normalized classical rule list

## Suggested repo layout

```text
surge-rules/
└── zoom/
    ├── Zoom.list
    └── README.md
```

## Suggested Rule Provider config

```ini
[Rule]
RULE-SET,zoom,Zoom

[Rule Provider]
zoom = type=http,behavior=classical,interval=86400,url=https://raw.githubusercontent.com/<your-name>/surge-rules/main/zoom/Zoom.list,path=zoom.list
```

## Maintenance notes

- Prefer official Zoom domains over giant CDN `/32` snapshots.
- Keep IP ranges only when Zoom docs or real traffic show they are stable service ranges.
- If Zoom updates their network ranges, update this file and bump the `# UPDATED:` line.
```
