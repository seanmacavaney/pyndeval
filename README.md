# pyndeval

A python interface to TREC's `ndeval.c`, used for computing diversity retrieval metrics.

## Getting Started

From pip:

```bash
pip install pyndeval
```

Or install from source:

```bash
git clone https://github.com/seanmacavaney/pyndeval.git
cd pyndeval
python setup.py install
```

## Usage

```python
import pyndeval
from pyndeval import SubtopicQrel, ScoredDoc

# provide qrels as a list of tuples
qrels = [
    SubtopicQrel("0", "a", "A", 1),
    SubtopicQrel("0", "b", "B", 1),
    SubtopicQrel("0", "b", "D", 1),
    SubtopicQrel("0", "c", "C", 1),
]

# provide run as a list of tuples
run = [
    ScoredDoc("0", "A", 9.3),
    ScoredDoc("0", "D", 8.4),
    ScoredDoc("0", "E", 8.1), # not in qrels
    ScoredDoc("0", "B", 7.6),
    # C not retrieved
]

pyndeval.ndeval(qrels, run)
{'0': {
  'ERR-IA@5': 0.3933,
  'ERR-IA@10': 0.3907,
  'ERR-IA@20': 0.3907,
  'nERR-IA@5': 0.8297,
  'nERR-IA@10': 0.8297,
  'nERR-IA@20': 0.8297,
  'alpha-DCG@5': 0.4052,
  'alpha-DCG@10': 0.3998,
  'alpha-DCG@20': 0.3997,
  'alpha-nDCG@5': 0.7868,
  'alpha-nDCG@10': 0.7868,
  'alpha-nDCG@20': 0.7868,
  'NRBP': 0.3906,
  'nNRBP': 0.8620,
  'MAP-IA': 0.5000,
  'P-IA@5': 0.2000,
  'P-IA@10': 0.1000,
  'P-IA@20': 0.0500,
  'strec@5': 0.6666,
  'strec@10': 0.6666,
  'strec@20': 0.6666
}}
```

## Supported measures

`pyndeval` supports the following measures:

 - `ERR-IA@k`
 - `nERR-IA@k`
 - `alpha-DCG@k`
 - `alpha-nDCG@k`
 - `P-IA@k`
 - `strec@k`
 - `NRBP`
 - `nNRBP`
 - `MAP-IA`

Measures with `@k` support values from 1-20 (upper limit from `ndeval.c`).

Measures are provided as a list of strings with the `measures=` parameter.

```python
pyndeval.ndeval(qrels, run, measures=["ERR-IA@7", "MAP-IA"])
```

## Reusing qrels

If you're running multiple times for the same set of qrels and measures, you can speed it up by
building a `RelevanceEvaluator` object, which caches the internal qrel representations.

```python
ev = pyndeval.RelevanceEvaluator(qrels)
ev.evaluate(run1)
ev.evaluate(run2)
ev.evaluate(run3)
ev.evaluate(run4)
```

## Iterable results

```python
for result in pyndeval.ndeval_iter(qrels, run):
  {"query_id": "0", ...}
for result in ev.evaluate_iter(run):
  {"query_id": "0", ...}
```
