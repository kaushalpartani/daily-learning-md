# daily-learning-md

A simple plugin for markdown blogs that generates questions, hints, and a place to answer.

Motivated by spaced repetition (similar to Anki) as a form of learning over time.

## To use

1. The starter .md file needs to have certain frontmatter:

```yaml
---
...
Topic: Ask me System Design questions at the senior software engineer level.
...
---
```

This topic will be used to generate questions and hints.

Note that the questions and hints are always appended to the end of the file. This ordering is important, as it is used to ensure that we don't generate the same question twice.

This project uses poetry to manage dependencies.

```bash
poetry install
```

Run the script:

```bash
poetry run python generate_md.py
```

## TODO
- Add answer generation. The question + hint generation of tomorrow should answer / grade my answer for today.