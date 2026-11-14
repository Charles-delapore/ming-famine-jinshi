# Zenodo release checklist

The repository has not minted a DOI yet. The metadata is prepared; the DOI must
be created from the author's Zenodo account.

## Preconditions

- [x] `CITATION.cff` exists.
- [x] `.zenodo.json` exists with title, description, creator, license, keywords.
- [x] `LICENSE` (MIT) and `README` are present.
- [ ] Author confirms the final title and author name.
- [ ] Jinshi provenance fields in `docs/data_provenance.md` are confirmed
      (source/version, inclusion/exclusion, 1523/1526 explanation).
- [ ] GitHub release tag chosen (suggest `v0.2.0` or `v1.0.0`).

## Steps (author account required)

1. Sign in to <https://zenodo.org> with GitHub.
2. Open **Settings → GitHub** and enable the repository
   `Charles-delapore/ming-famine-jinshi`.
3. Create a GitHub release (draft or published) with the chosen tag.
4. Zenodo archives the release and mints a DOI.
5. Add the DOI badge and the DOI string to:
   - `README.md` (top or citation section),
   - `CITATION.cff` (`doi:` and `identifiers:`),
   - `docs/zenodo_release.md` (this file).
6. Re-run the Pages build if the README badge is added.

## After minting

```yaml
# CITATION.cff additions
doi: "10.5281/zenodo.XXXXXXX"
identifiers:
  - type: doi
    value: "10.5281/zenodo.XXXXXXX"
```

Do not invent a DOI or add a badge before Zenodo returns one. Until then the
repository is citable by URL and commit hash.
