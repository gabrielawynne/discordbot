import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

DEFAULT_CONFIG = {
    "vote_channels": [],
    "heart_channels": [],
    "weekly_source_channel": None,
    "weekly_post_channel": None,
    "weekly_message": "🏆 Weekly winner!",
    "weekly_day": None,
    "weekly_hour": None,
    "weekly_minute": None,
    "vc_log_channel": None,
    "tc_log_channel": None
}



def load_config():
    """
    Load config.json and merge it with DEFAULT_CONFIG.
    Guarantees all expected keys always exist.
    """
    cfg = DEFAULT_CONFIG.copy()

    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    cfg.update(data)
        except json.JSONDecodeError:
            # corrupted config.json → fall back to defaults
            pass

    return cfg


def save_config(cfg):
    """
    Save the current config back to disk.
    """
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
