# Light–Matter Information Lab website

A single-page site for the lab at the Photonics Initiative, CUNY Advanced Science Research Center.
`index.html` is generated from the YAML files in `data/` and is served as-is by GitHub Pages.

## Edit content

| To change | Edit |
|---|---|
| Headline, intro, address, links, hiring line, headline photo | `data/site.yml` |
| Latest news and activities | `data/news.yml` (newest first) |
| Research programs | `data/research.yml` |
| PI, members, openings, former postdocs, collaborators | `data/people.yml` |
| Papers, talks, patents (and which are "selected") | `data/publications.yml` |

Then rebuild and commit:

```bash
pip install -r requirements.txt   # first time only
python build.py
```

## Update publications from Google Scholar

1. On your Google Scholar profile, tick the box above the article list to select all, then choose **Export → BibTeX** and save the file as `scholar.bib`.
2. Merge it, check the summary, then rebuild:

```bash
python tools/import_scholar.py scholar.bib --dry-run
python tools/import_scholar.py scholar.bib
python build.py
```

New papers are added, preprints are upgraded when the published version appears, and anything you edited by hand is kept.
Author lists cut short with "et al." are filled in automatically; add `--refresh-authors` to replace every author list with the export's full names.
Sandia/Los Alamos technical reports (`@techreport`) are skipped.

`python build.py` also writes `assets/publications.bib` from `data/publications.yml`; the page links to it as
"Download all as BibTeX", so the download always matches what the site shows.
Set `selected: true` on a paper in `data/publications.yml` to feature it under "Selected publications".

## Images

- People photos go in `assets/img/people/` (square, about 400 px) and are referenced by `photo:` in `data/people.yml`.
- Research figures go in `assets/img/research/` and are referenced by `image:` in `data/research.yml`.
- The headline photo is set by `hero_image:` in `data/site.yml`. Use a photo you have permission to publish.
