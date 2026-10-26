# Incident Triage Tree

A decision tree that classifies cybersecurity incidents by severity. Answer YES or NO until you reach a verdict.

## Run

```bash
python server.py
```

Open http://127.0.0.1:8000 (Python 3.10+, no extra packages).

## Files

- `node.py` – `TriageNode`: a question or a verdict
- `tree.py` – `DecisionTree`: insert, find, traversals, height
- `builder.py` – `TreeBuilder`: builds the default tree
- `server.py` – `ApiHandler`: serves the frontend and the API
- `static/` – HTML, CSS and JavaScript
