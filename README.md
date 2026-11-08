# Light–Matter Intelligence Lab website

A single-page site for the lab at the Photonics Initiative, CUNY Advanced Science Research Center.
`index.html` is generated from the YAML files in `data/` and is served as-is by GitHub Pages.

## Edit content

| To change | Edit | Rebuild? |
|---|---|---|
| Headline, intro, address, links, hiring line, headline photo, featured papers | `data/site.yml` | yes |
| Latest news and activities | `data/news.yml` (newest first) | yes |
| Research programs | `data/research.yml` | yes |
| PI, members, openings, former postdocs, collaborators | `data/people.yml` | yes |
| **Publications, conference papers, patents, reports, thesis, talks** | **`data/publications.json`** | **no** |
| Corrections and entries Scholar doesn't have | `data/publications_extra.json` | no |

Rebuild after editing YAML:

```bash
pip install -r requirements.txt   # first time only
python build.py
```

## Publications

The Publications section is rendered in the browser by `assets/publications.js` from
**`data/publications.json`**. To update it, replace that file with a new export from your Scholar
updater (same fields) and commit. No rebuild and no code changes are needed.

Fields per entry: `title`, `auth` (full author list), `venue`, `year`, `typ`
(`journal` | `conference` | `preprint` | `patent` | `report` | `thesis` | `talk`),
and optionally `url`, `doi`, `pdf`, `arxiv`, `abstract`.

What the page does with it:
- groups entries by year (newest first), with five filter tabs: Selected, All,
  Journal Articles (`journal` + `preprint`), Conference Proceedings (`conference` + `talk`) and Patent;
  reports and the thesis appear only under All (the grouping is the `TABS` list at the top of
  `assets/publications.js`);
- shows the full author list and bolds Prasad P Iyer / Prasad Iyer / Prasad Padmanabha Iyer / PP Iyer / P Iyer;
- links the title to `url`, and adds DOI, PDF and arXiv buttons when those fields exist
  (a PDF link identical to the DOI link is not repeated);
- puts each abstract in a collapsible toggle, rendering simple inline LaTeX and `<sup>/<sub>`;
- keeps near-duplicates (e.g. conference and journal versions); only byte-for-byte duplicate
  records (same title, venue, year and type) are shown once;
- offers "Download all as BibTeX", generated from the same data.

**`data/publications_extra.json`** survives every Scholar update:
- entries with `"patch": true` change fields of the entry with the same title (for example a
  missing link, or a preprint that has since been accepted at a conference);
- entries with `"fill": true` only fill fields that are empty in `publications.json` (used for
  abstracts recovered from the previous website), so anything Scholar later provides wins;
- other entries are added as new rows (e.g. Sandia patent filings that aren't on Scholar).

**Featured papers** for the "Selected" tab are listed by title under `selected_publications`
in `data/site.yml` (rebuild after changing it).

## Images

- People photos go in `assets/img/people/` (square, about 400 px) and are referenced by `photo:` in `data/people.yml`.
- Research figures go in `assets/img/research/` and are referenced by `image:` in `data/research.yml`.
- The headline photo is set by `hero_image:` in `data/site.yml`. Use a photo you have permission to publish.
