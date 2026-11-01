# Churchill Strategy daily news carousels

Slides for the 5:00 a.m. provincial and territorial government briefing, one folder per day and time zone. Public so Instagram, Facebook and Google Drive can fetch them.

## index.json (for churchillstrategy.ca)

`index.json` lists the latest briefing for each province or territory: slide paths, the PDF, headlines and their sources. churchillstrategy.ca reads it to show the briefing on each election tracker page and all of them on /elections.

It rebuilds itself: the "Build briefing index" workflow runs `scripts/build_index.py` on every push to `daily/` and commits the new `index.json`. Keep the folder pattern `daily/YYYY-MM-DD/<region>/` with `captions.md`, `<CODE>-<Name>.pdf` and `<CODE>/NN.jpg`, and keep one `Source:` line per headline, in the same order.
