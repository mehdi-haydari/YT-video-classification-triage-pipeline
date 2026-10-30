"""Load a clip by title and save its unedited OpenRouter reply."""

import argparse
import json
import math
from pathlib import Path
import sys
import urllib.error
import urllib.request

from dotenv import dotenv_values
import pandas as pd
import yaml

from youtube_triage.prompt import SYSTEM_PROMPT


def load_clip(csv_path: Path, title: str) -> tuple[int, dict]:
    """Select exactly one title; copy only the three authorized input fields."""
    clips = pd.read_csv(csv_path, keep_default_na=False)
    fields = ("transcript_timestamped", "frame_captions_timestamped")
    required = {"title", "duration_seconds", *fields}
    missing = required - set(clips.columns)
    if missing:
        raise ValueError(f"CSV is missing columns: {', '.join(sorted(missing))}")
    rows = clips.loc[clips["title"].eq(title)]
    if len(rows) != 1:
        raise ValueError(f"Expected one title match, found {len(rows)}")
    row = rows.iloc[0]
    clip = {name: row[name] for name in fields}
    if any(not isinstance(value, str) or not value.strip() for value in clip.values()):
        raise ValueError("Selected clip needs a transcript and frame captions")
    duration = float(row["duration_seconds"])
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError("Selected clip needs a finite, positive duration")
    clip["duration_seconds"] = duration
    return len(clips), clip


def load_settings(config_path: Path) -> tuple[dict, str, str]:
    config = yaml.safe_load(config_path.read_text())
    if not isinstance(config, dict):
        raise ValueError("Configuration must be a YAML mapping")
    if config.get("provider") != "openrouter" or config.get("api_base_url") != "https://openrouter.ai/api/v1":
        raise ValueError("Expected the OpenRouter API address in config.yaml")
    model = config.get("model")
    if not isinstance(model, str) or not model.strip():
        raise ValueError("config.yaml must contain a nonempty model ID")
    env_path = config_path.parent / config["env_file"]
    env = dotenv_values(env_path, interpolate=False)
    key = env.get(config["api_key_variable"])
    if not key:
        raise ValueError("The configured env file must contain an API key")
    return config, model, key


def build_payload(clip: dict, config: dict, model: str) -> dict:
    return {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(clip, ensure_ascii=False)},
        ],
        "temperature": config["temperature"],
        "max_tokens": config["max_tokens"],
    }


def call_model(payload: dict, config: dict, key: str) -> dict:
    request = urllib.request.Request(
        config["api_base_url"] + "/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.load(response)


def terminal_output(response: dict) -> str:
    """Preserve message.content without parsing, stripping, or fixing its JSON."""
    choice = response["choices"][0]
    content = choice["message"]["content"]
    if not isinstance(content, str) or not content:
        raise ValueError(f"Model returned no reply text (finish_reason={choice.get('finish_reason')})")
    return (
        f"Response model: {response.get('model')}\n"
        f"Finish reason: {choice.get('finish_reason')}\n"
        f"{content}\n"
    )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--title", required=True, help="Exact title to select from the CSV")
    parser.add_argument("--config", type=Path, default=Path("config.yaml"))
    parser.add_argument("--output", type=Path, help="Save the exact terminal output to this file")
    args = parser.parse_args(argv)
    try:
        # Row count is reported, never assumed to be 200 or used as a loading gate.
        count, clip = load_clip(args.csv_path, args.title)
        print(f"Loaded {count} clips; selected one matching title.", file=sys.stderr)
        config, model, key = load_settings(args.config.resolve())
        reply = terminal_output(call_model(build_payload(clip, config, model), config, key))
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_bytes(reply.encode("utf-8"))
        print(reply, end="")
    except urllib.error.HTTPError as exc:
        parser.exit(1, f"OpenRouter returned HTTP {exc.code}; saved output was not changed.\n")
    except (OSError, ValueError, KeyError, IndexError, TypeError, yaml.YAMLError) as exc:
        parser.exit(1, f"Request failed: {exc}\n")


if __name__ == "__main__":
    main()
