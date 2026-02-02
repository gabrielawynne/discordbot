import json
import os

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "vote_channels": [],
    "heart_channels": [],
    "weekly_source_channel": None,
    "weekly_post_channel": None,
    "weekly_message": "🏆 Weekly winner!",
    "weekly_day": None,
    "weekly_hour": None,
    "weekly_minute": None
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return DEFAULT_CONFIG.copy()

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    for k, v in DEFAULT_CONFIG.items():
        cfg.setdefault(k, v)

    return cfg

def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
