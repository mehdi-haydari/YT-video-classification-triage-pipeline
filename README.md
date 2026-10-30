# YouTube video classification triage pipeline

A small Python starter for exploring labelled YouTube clip datasets with pandas.
The initial command reports the number of clips, available columns, and label
counts when a `ground_truth_label` column exists. It does not classify videos yet.

## Setup

Requires Python 3.10 or newer.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

## Summarize a dataset

```sh
youtube-triage "/path/to/labelled-clips.csv"
```

You can also run `python -m youtube_triage "/path/to/labelled-clips.csv"`.
Any CSV with a header is supported; `ground_truth_label` is optional.

## Local files

Keep datasets in `data/` and generated results in `outputs/`; both are ignored
by Git. No dataset is bundled with this project.

`.env`, `.env.*`, and `*.env` files are ignored by Git. The starter needs no
credentials and does not automatically load environment files.
