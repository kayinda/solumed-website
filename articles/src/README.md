How to publish an article or news piece
=======================================

1. Copy an existing file in this folder and rename it. The file name becomes the web address,
   so use lowercase words joined by hyphens, for example `new-amr-action-plan.md`
   (address: solumedplus.com/articles/new-amr-action-plan.html).

2. Edit the header block at the top:

   ---
   title: Your headline
   date: 2026-12-01            (year-month-day; newest shows first)
   type: Article               (Article, News or Publication)
   author: Kayinda Francis
   topic: Antimicrobial resistance
   summary: One or two sentences shown on the list page and in Google results.
   draft: yes                  (optional: builds the page but keeps it off the list, feed and sitemap)
   ---

3. Write the piece below the header:
   - `## Heading` for a section, `### Sources` for the reference list at the end
   - a blank line between paragraphs
   - `- item` for bullets, `1. item` for numbered lists
   - `**bold**`, `*italic*`, `[link text](https://...)`
   - cite with [1], [2] in the text and list the sources as a numbered list under `### Sources`

4. Build and publish (from the website folder):

       python3 articles/build.py
       git add -A && git commit -m "Article: your headline" && git push

   Then run the usual `git pull` on the server if it does not pick it up within a few minutes.

Rules: your own words only (summarise and link, never copy other outlets); cite sources; no IDI or
other employer data; no em dashes. The build warns if it finds one. Files starting with `_` or `.` are ignored,
and so is this README.
