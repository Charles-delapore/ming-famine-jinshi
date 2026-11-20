# Known issues and open items

## Reporting and claims

| Item | Status | Effect |
|---|---|---|
| `48/135` is a 20-lag max-F count | resolved in the text | reported as a diagnostic; fixed 1–5 year test is 2/135 |
| Median lag is bimodal | resolved in the text | short-lag share and paired changes are reported instead |
| Long-lag tail | open question | no evidence of a distinct long-run effect; multiscale finds 0 at 11–20 years |
| Report-intensity bias | partially controlled | dose-response test does not support a strong bias, but no gazetteer-survival proxy is available |
| Quota system (南/北/中卷) | not modelled | regional Jinshi counts are partly policy-constrained; see the discussion |

## Data

| Item | Status | Effect |
|---|---|---|
| 911-record Jinshi layer | retired | kept as an encoding audit only |
| National-sample representativeness | limited | the panel is a 1° grid, not a random sample of events |
| Coordinate precision | not fully testable | the export has no administrative-level field; `xy_count` is a shared-coordinate count |
| Raw tables | private | full reproduction needs the private inputs; aggregates and synthetic samples are public |
| SHAP / GeoShapley on v0.3 | not re-estimated | only the multiscale/GWR/GeoDetector/Granger stack was re-run; SHAP claims are not repeated |
| STL on v0.3 | done | 160 shared grids; variance shares identical, `sig_trend` 26 → 18 |
| CCM | not identifiable | reported as a negative result, not tuned |

## Engineering

| Item | Status |
|---|---|
| Python 3.9/3.10 | declared but CI runs 3.12/3.13; Dependabot major bumps are blocked |
| Browser/UI tests | none; the map is checked by generation, not by interaction |
| Network access in CI | none; all checks use the repository contents |
| Old commit `a051045` | still resolvable by SHA; contains a removed person-level table |
