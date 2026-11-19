# FAQ

## Why is the headline 2/135 and not 48/135?

The 48/135 count comes from a max-F search over 20 lags per grid. That search
inflates the discovery count: after a within-grid Bonferroni correction it is
7/135, and a fixed, pre-specified 1–5 year joint test finds 2/135. The
multiscale model finds 8/135 at 1–5 years and 0 at longer horizons. The
fixed-window result is the headline; 48/135 is reported as a diagnostic.

## Why is there no single "median lag"?

The selected lag is bimodal (1–3 years or 15–20 years), so a median moves with
the search window. We report the short-lag share and the paired lag change
instead.

## Is the long-lag result a real long-run effect?

No evidence for that. Long-lag grids are not more famine-prone and are not
spatially clustered; they simply have fewer Jinshi records. The multiscale
model finds no signal at 11–20 years.

## Why are the raw data not in the repository?

CBDB and the famine tables are third-party or private research tables. Only
aggregates, synthetic samples and code are published. See
[`../DATA_AVAILABILITY.md`](../DATA_AVAILABILITY.md).

## How do I run the code without the private data?

```bash
python scripts/make_sample_data.py
python scripts/run_sample_figures.py
python scripts/make_interactive_map.py --sample
```

The sample is synthetic and is labelled as such in the figures.

## How do I report a wrong number?

Open a data-correction issue with the file, the published value and the expected
value. Corrections are versioned in `CHANGELOG.md`.
