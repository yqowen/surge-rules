#!/usr/bin/env python3
from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "zoom"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OFFICIAL_URLS = {
    "Zoom": "https://assets.zoom.us/docs/ipranges/Zoom.txt",
    "ZoomApps": "https://assets.zoom.us/docs/ipranges/ZoomApps.txt",
}

DOMAIN_RULES = [
    "DOMAIN,zdmapi.zoom.us",
    "DOMAIN-SUFFIX,zoom.us",
    "DOMAIN-SUFFIX,zoom.com",
    "DOMAIN-SUFFIX,zoom.com.cn",
    "DOMAIN-SUFFIX,zoomstatus.com",
    "DOMAIN-SUFFIX,zoomapp.cloud",
]

LITE_KEEP_PREFIXES = (
    "3.7.35.0/25",
    "3.235.82.0/23",
    "3.235.96.0/23",
    "4.34.125.128/25",
    "4.35.64.128/25",
    "8.5.128.0/23",
    "15.220.80.0/24",
    "15.220.81.0/25",
    "20.203.158.80/28",
    "20.203.190.192/26",
    "50.239.202.0/23",
    "50.239.204.0/24",
    "52.61.100.128/25",
    "52.84.151.0/24",
    "64.125.62.0/24",
    "64.211.144.0/24",
    "64.224.32.0/19",
    "65.39.152.0/24",
    "69.174.57.0/24",
    "69.174.108.0/22",
    "101.36.167.0/24",
    "101.36.170.0/23",
    "103.122.166.0/23",
    "111.33.115.0/25",
    "111.33.181.0/25",
    "115.110.154.192/26",
    "115.114.56.192/26",
    "115.114.115.0/26",
    "115.114.131.0/26",
    "120.29.148.0/24",
    "121.244.146.0/27",
    "134.224.0.0/16",
    "137.66.128.0/17",
    "144.195.0.0/16",
    "147.124.96.0/19",
    "149.137.0.0/17",
    "156.45.0.0/17",
    "159.124.0.0/16",
    "160.1.56.128/25",
    "161.199.136.0/22",
    "162.12.232.0/22",
    "162.255.36.0/22",
    "165.254.88.0/23",
    "166.108.64.0/18",
    "168.140.0.0/17",
    "170.114.0.0/16",
    "173.231.80.0/20",
    "192.204.12.0/22",
    "198.251.128.0/17",
    "202.177.207.128/27",
    "203.200.219.128/27",
    "204.80.104.0/21",
    "204.141.28.0/22",
    "206.247.0.0/16",
    "207.226.132.0/24",
    "209.9.211.0/24",
    "209.9.215.0/24",
    "213.19.144.0/24",
    "213.19.153.0/24",
    "213.244.140.0/24",
    "221.122.63.0/24",
    "221.122.64.0/24",
    "221.122.88.64/27",
    "221.122.88.128/25",
    "221.122.89.128/25",
    "221.123.139.192/27",
    "18.254.23.128/25",
    "18.254.61.0/25",
)


def fetch_text(url: str) -> str:
    with urlopen(url, timeout=30) as resp:
        return resp.read().decode("utf-8", "ignore")


def normalize_rule(line: str) -> str | None:
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    if line.startswith("DOMAIN,") or line.startswith("DOMAIN-SUFFIX,") or line.startswith("DOMAIN-KEYWORD,"):
        parts = [p.strip() for p in line.split(",") if p.strip()]
        return ",".join(parts[:2])
    if line.startswith("IP-CIDR,"):
        cidr = line.split(",")[1].strip()
        return f"IP-CIDR,{cidr},no-resolve"
    if re.match(r"^\d+\.\d+\.\d+\.\d+/\d+$", line):
        return f"IP-CIDR,{line},no-resolve"
    return None


def load_official_rules() -> list[str]:
    rules: list[str] = []
    for _, url in OFFICIAL_URLS.items():
        text = fetch_text(url)
        for raw in text.splitlines():
            rule = normalize_rule(raw)
            if rule:
                rules.append(rule)
    return rules


def unique_keep_order(items: list[str]) -> list[str]:
    seen = set()
    out = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def split_rules(rules: list[str]):
    domains = [r for r in rules if not r.startswith("IP-CIDR,")]
    cidrs = [r for r in rules if r.startswith("IP-CIDR,")]
    return domains, cidrs


def sort_rules(rules: list[str]) -> list[str]:
    domains, cidrs = split_rules(rules)
    return sorted(domains) + sorted(cidrs, key=lambda x: x.split(",")[1])


def render(name: str, author: str, repo: str, rules: list[str], notes: list[str] | None = None) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    domain = sum(1 for r in rules if r.startswith("DOMAIN,"))
    domain_suffix = sum(1 for r in rules if r.startswith("DOMAIN-SUFFIX,"))
    domain_keyword = sum(1 for r in rules if r.startswith("DOMAIN-KEYWORD,"))
    ip_cidr = sum(1 for r in rules if r.startswith("IP-CIDR,"))
    lines = [
        f"# NAME: {name}",
        f"# AUTHOR: {author}",
        f"# REPO: {repo}",
        f"# UPDATED: {now}",
        f"# DOMAIN: {domain}",
        f"# DOMAIN-KEYWORD: {domain_keyword}",
        f"# DOMAIN-SUFFIX: {domain_suffix}",
        f"# IP-CIDR: {ip_cidr}",
        f"# TOTAL: {len(rules)}",
    ]
    if notes:
        lines.append("#")
        lines.extend(f"# {note}" for note in notes)
    return "\n".join(lines + rules) + "\n"


def main() -> None:
    official = unique_keep_order(DOMAIN_RULES + load_official_rules())
    official = sort_rules(official)

    lite = [r for r in official if not r.startswith("IP-CIDR,")]
    lite += [r for r in official if r.startswith("IP-CIDR,") and r.split(",")[1] in LITE_KEEP_PREFIXES]
    lite = unique_keep_order(lite)
    lite = sort_rules(lite)

    repo = "https://github.com/yqowen/surge-rules"
    (OUT_DIR / "Zoom.list").write_text(
        render(
            "Zoom",
            "Owen Ye / Clawd",
            repo,
            official,
            [
                "Generated automatically from official Zoom IP range TXT files.",
                "Sources: Zoom.txt + ZoomApps.txt",
            ],
        ),
        encoding="utf-8",
    )
    (OUT_DIR / "ZoomLite.list").write_text(
        render(
            "ZoomLite",
            "Owen Ye / Clawd",
            repo,
            lite,
            [
                "Curated lightweight version for personal use.",
                "Generated from official Zoom ranges, but trimmed to stable/common entries.",
            ],
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
