# daily-learning-md

A simple plugin for markdown blogs that generates questions, hints, and a place to answer.

Motivated by spaced repetition (similar to Anki) as a form of learning over time.

## To use

1. The started .md file needs to have certain frontmatter:

```yaml
---
...
Topic: Ask me System Design questions at the senior software engineer level.
...
---
```

This topic will be used to generate questions and hints.

This project uses poetry to manage dependencies.

```bash
poetry install
```

Run the script:

```bash
poetry run python generate_md.py
```

## TODO
- Ensure that we don't generate the same question twice.
- Add answer generation. The question + hint generation of tomorrow should answer / grade my answer for today.