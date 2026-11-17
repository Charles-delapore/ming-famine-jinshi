# Release checklist

Use this for every tagged release (current target: `v0.4.0`).

## 1. Freeze

- [ ] `pytest -q` passes.
- [ ] `python tools/check_public_tree.py` passes.
- [ ] `ruff check .` passes.
- [ ] `CHANGELOG.md` has the version and date.
- [ ] No uncommitted changes in `git status`.

## 2. Version metadata

- [ ] `CITATION.cff`: `version` and `date-released`.
- [ ] `.zenodo.json`: `version`, `publication_date`, description.
- [ ] `README.md` / `README.zh.md` do not contradict the released numbers.

## 3. Tag and push

```bash
git tag -a v0.4.0 -m "Ming famine-Jinshi 0.4.0"
git push origin main
git push origin v0.4.0
```

## 4. GitHub release

- [ ] Title: `v0.4.0 — fixed-window results and data boundary`.
- [ ] Body: copy the `0.4.0` section of `CHANGELOG.md`.
- [ ] Attach nothing that is not already in the repository.

## 5. Zenodo

- [ ] Connect the repository if not already connected.
- [ ] Publish the release; copy the DOI.
- [ ] Add the DOI to `CITATION.cff` and `README.md` (one follow-up commit).

## 6. Pages

- [ ] Pages builds on the tagged commit.
- [ ] Site returns HTTP 200.
- [ ] Landing page shows the fixed-window result, not the 20-lag count.

## 7. After release

- [ ] Open a `v0.4.1` section in `CHANGELOG.md` if fixes are pending.
- [ ] If a data correction is needed, version it and update the data dictionary.

## Rollback

If the release is wrong, do not delete the tag silently. Publish a patched
release, document the reason in `CHANGELOG.md`, and keep the DOI history.
