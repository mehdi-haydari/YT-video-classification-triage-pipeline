# YouTube video classification triage pipeline

A small Python starter for exploring labelled YouTube clip datasets with pandas.
The summary command reports the number of clips, available columns, and label
counts. A separate raw-call loader selects a clip by title and calls OpenRouter.

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

The committed `config.yaml` specifies the OpenRouter API address and the model
ID under `model`: `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free`, matching
the model in the saved reply. Only the API key, under `model_auth_key`, belongs
in the ignored `src/.env` file. The loader reads the model ID directly from
`config.yaml` and does not use a model setting from `.env`. To let OpenRouter
choose a free model instead, change `model` in `config.yaml` to `openrouter/free`.
The CSV summary command does not contact the model or need a key.

## Run the raw model call

From the repository root, after installing the project, setting the model in
`config.yaml`, and setting `model_auth_key` in `src/.env`:

```sh
python -m youtube_triage.call_model "/path/to/labelled-clips.csv" \
  --title "Tear gas on Avenida Central: what I filmed from the second line" \
  --output artifacts/ana-protest-context-terminal-output.md
```

The [loader](src/youtube_triage/call_model.py) uses pandas to select exactly one
row by its `title` field. Only that row's transcript, frame captions, and duration
are sent; ground-truth columns are excluded. The CSV path and title are arguments,
and the dataset row count is reported without requiring 200 rows. The supplied
resource currently contains 80 records.

The [prompt](src/youtube_triage/prompt.py) contains the injury rule and response
format used for this test. This is a raw call, not the full triage pipeline.
The output file preserves `message.content` exactly, with the two model/finish
metadata lines and the terminal's final newline. It does not repair or reformat
the model's JSON. A failed API request leaves the existing artifact untouched.

## Ana's protest clip

[Saved model terminal output](artifacts/ana-protest-context-terminal-output.md)

- Removal: The model returned `age-restricted`, matching `ground_truth_label=age_restrict`; the CSV calls for age restriction rather than removal because the injury footage has news value.
- Timestamp fit: The violation evidence at `[01:50]` falls within the labelled violent segment `[00:55-02:10]`; the reply cites only the injury evidence, without predicting full segment boundaries.
