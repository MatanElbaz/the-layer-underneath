# AGENTS.md - rules for the wiki agent

## Roles
- The human chooses sources and asks questions. The human never edits wiki/.
- You (the agent) write and maintain everything in wiki/. You never modify raw/.

## Layout
- raw/   sources. Read-only.
- wiki/  your output. Markdown files, all lowercase-with-dashes names:
  - index.md   one line per page: `- [[page-name]] - one-sentence summary`
  - log.md     append-only history: `## [YYYY-MM-DD] ingest|query|lint | title`
  - models/    one page per model
  - concepts/  one page per technical concept
  - sources/   summary of the source files
- code/  code you write from what the wiki knows.

## Page format
Every page = frontmatter + one-line summary + a `## Facts` list (4-10 bullets) + `## Related`.
Facts must be concrete and copied exactly from the sources: parameter counts, sizes in GB,
context windows, licenses, bits per weight. A page without concrete facts is useless.
Example of a complete page (a fictional model, format only):
```
---
tags: [model]
source: raw/example.md
updated: 2026-01-01
---
# example-7b
A small fictional model used to show the page format.

## Facts
- 7B parameters, dense (not Mixture of Experts).
- The Q4 download is 4.1GB.
- License: MIT.

## Related
[[quantization]] · [[memory-requirements]]
```
Link pages with Obsidian wikilinks by file name only: [[gpt-oss-20b]].
Every fact must be traceable to a source file. Never invent facts.

## Ingest  (sources -> pages)
1. Read the sources with read_file.
2. Write exactly these 6 pages, each complete with its Facts list:
   wiki/models/gpt-oss-20b.md
   wiki/models/qwen3-coder-30b.md
   wiki/concepts/quantization.md
   wiki/concepts/mixture-of-experts.md
   wiki/concepts/memory-requirements.md
   wiki/sources/reading-list.md
3. Write wiki/index.md listing every page.
4. Append one line to wiki/log.md.
5. Reply with 3 short bullet points: what you learned.

## Query
1. Use search for exact names or numbers, or read wiki/index.md, then only the pages you need.
2. Answer in at most 5 lines and cite the page(s) like [[gpt-oss-20b]].
3. Do NOT read raw/ during a query. If the wiki has no answer, say exactly:
   "The wiki does not cover this yet."

## Lint
1. Read the new source and the relevant wiki pages.
2. For every contradiction quote BOTH sentences in full, and name both files.
3. Do not delete or overwrite the old claim. Write wiki/contradictions.md listing each
   contradiction, and add a "> [!warning] Disputed - see [[contradictions]]" line to the affected page.
4. Append one line to wiki/log.md.

## Code  (wiki -> code)
1. Search the wiki and read the pages you need. Do NOT read raw/.
2. Write the code in code/ with write_file. Every number comes from a wiki page;
   cite the page in a comment next to it, like  # [[gpt-oss-20b]]
3. Standard library only, plain ASCII. The harness runs a test after you write; if it fails,
   fix the file and write it again.
