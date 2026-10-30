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

`.env`, `.env.*`, and `*.env` files are ignored by Git.

## Model configuration

`config.yaml` specifies the OpenRouter API address and the names of settings to
read from the ignored `src/.env` file. Set `model` to your chosen model ID and
`model_auth_key` to your API key in that file. Neither value is stored in
`config.yaml`. To let OpenRouter choose a free model, set `model=openrouter/free`
in `src/.env`. The CSV summary command does not contact the model or need a key.

## Ana's protest clip

[Saved model terminal output](artifacts/ana-protest-context-terminal-output.txt)

- Removal: The model returned `age-restricted`, matching `ground_truth_label=age_restrict`; the CSV calls for age restriction rather than removal because the injury footage has news value.
- Timestamp fit: The violation evidence at `[01:50]` falls within the labelled violent segment `[00:55-02:10]`; the reply cites only the injury evidence, without predicting full segment boundaries.
