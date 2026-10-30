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

[Original model terminal output](artifacts/ana-protest-terminal-output.txt)

- Removal: Ana's protest clip (`yt_c0041`) was correctly age-restricted rather than removed, matching `ground_truth_label=age_restrict` and the CSV's injury/news-value reason.
- Timestamp fit: The cited injury frame `[01:50]` (110 seconds) falls within `ground_truth_violent_segments=55.0-130.0` (`[00:55-02:10]`); it supports the decision but does not identify the full segment boundaries.

The original reply cited a single injury frame, so it did not demonstrate consideration of the surrounding clip context. A subsequent test requested assessment of every supplied transcript segment and frame caption, with evidence from before the injury, the injury itself, and later reporting context.

- [Full request: prompt, complete supplied transcript, frame captions, and duration](artifacts/ana-protest-context-request.json)
- [Unedited terminal reply from the context review](artifacts/ana-protest-context-terminal-output.txt)
- [Pydantic, source evidence, and ground-truth comparison](artifacts/ana-protest-context-validation.json)

The new reply returns `age-restricted` and cites `[00:20-00:55]`, `[01:50]`, and `[03:05-03:50]`, addressing both the injury and the reporting context when distinguishing age restriction from removal. Structure, exact quotes, timestamp fit, and the ground-truth label comparison pass. The request contains no ground-truth fields; evaluation is performed afterward.

This assesses the supplied text, not the video itself. The input contains seven transcript segments ending at `[04:10]` and nine frame captions, with a stated duration of 254 seconds (`[04:14]`). The last four seconds have no transcript, and sparse captions do not establish continuous visual coverage. The saved input and broader citations make the test auditable, but cannot prove that the model considered every segment.

The first context-review attempt returned malformed JSON and insufficient context citations; it is preserved as an [unedited reply](artifacts/ana-protest-context-attempt-1.txt) with its [request](artifacts/ana-protest-context-attempt-1-request.json).
