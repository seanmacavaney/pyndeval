from typing import Union, Dict, Tuple, List, NamedTuple, Iterator, Iterable, Optional
from collections import abc
import _pyndeval

SUPPORTED_MEASURES = [
    'ERR-IA',
    'nERR-IA',
    'alpha-DCG',
    'alpha-nDCG',
    'P-IA',
    'strec',
    'NRBP',
    'nNRBP',
    'MAP-IA',
]

NOCUTOFF_MEASURES = {'NRBP', 'nNRBP', 'MAP-IA'}

DEFAULT_MEASURES = [
    'ERR-IA@5', 'ERR-IA@10', 'ERR-IA@20',
    'nERR-IA@5', 'nERR-IA@10', 'nERR-IA@20',
    'alpha-DCG@5', 'alpha-DCG@10', 'alpha-DCG@20',
    'alpha-nDCG@5', 'alpha-nDCG@10', 'alpha-nDCG@20',
    'NRBP',
    'nNRBP',
    'MAP-IA',
    'P-IA@5', 'P-IA@10', 'P-IA@20',
    'strec@5', 'strec@10', 'strec@20',
]


class SubtopicQrel(NamedTuple):
    query_id: str
    subtopic_id: str
    doc_id: str
    relevance: int


class ScoredDoc(NamedTuple):
    query_id: str
    doc_id: str
    score: float


QrelsType = Union[
    Iterable[SubtopicQrel],
    Iterable[Tuple[str, str, str, int]], # [(qid, subtopic, docno, rel)]
]

RunType = Union[
    Iterable[ScoredDoc],
    Iterator[Tuple[str, str, float]], # [(qid, docno, score)]}
]

MeasuresType = Optional[Iterable[str]]

class RelevanceEvaluator:
    def __init__(self, qrels: QrelsType, measures: MeasuresType = None, relevance_level: int = 1, alpha: float = 0.5, beta: float = 0.5):
        if measures is None:
            measures = DEFAULT_MEASURES
        else:
            measures = list(measures)
        self.measures_arg = []
        max_cutoff = 20
        for measure in measures:
            if '@' in measure:
                assert measure not in NOCUTOFF_MEASURES
                measure, cutoff = measure.split('@', 1)
                cutoff = int(cutoff)
                assert cutoff > 0
                max_cutoff = max(max_cutoff, cutoff)
            else:
                assert measure in NOCUTOFF_MEASURES
                cutoff = None
            self.measures_arg.append((SUPPORTED_MEASURES.index(measure), cutoff))
        assert max_cutoff <= 20, "ndeval only supports cutoffs up to 20"
        self.qrels = _coerce_qrels(qrels, max_cutoff, relevance_level, alpha, beta)
        self.measures = measures
        self.relevance_level = relevance_level
        self.alpha = alpha
        self.beta = beta

    def evaluate(self, run: RunType) -> Dict[str, Dict[str, float]]:
        result = {}
        for rec in self.evaluate_iter(run):
            result[rec['query_id']] = rec
            del rec['query_id']
        return result

    def evaluate_iter(self, run: RunType) -> Iterable[Dict[str, Union[float, str]]]:
        for qid, scoredocs in _coerce_run_iter(run):
            _pyndeval.set_global_alpha_beta(self.alpha, self.beta)
            if qid in self.qrels:
                metrics = _pyndeval.eval(self.qrels[qid], scoredocs, self.measures_arg)
                result = {'query_id': qid}
                result.update(zip(self.measures, metrics))
                yield result

    def has_multiple_subtopics(self, mode='all'):
        agg = {'all': all, 'any': any}[mode]
        return agg(q.has_multiple_subtopics() for q in self.qrels.values())


def ndeval_iter(qrels: QrelsType, run: RunType, measures: MeasuresType = None, alpha: float = 0.5, beta: float = 0.5) -> Iterable[Dict[str, Union[float, str]]]:
    ev = RelevanceEvaluator(qrels, measures, alpha=alpha, beta=beta)
    return ev.evaluate_iter(run)


def ndeval(qrels: QrelsType, run: RunType, measures: MeasuresType = None, alpha: float = 0.5, beta: float = 0.5) -> Dict[str, Dict[str, float]]:
    ev = RelevanceEvaluator(qrels, measures, alpha=alpha, beta=beta)
    return ev.evaluate(run)


def _coerce_qrels(qrels: QrelsType, max_cutoff, relevance_level, alpha, beta):
    result = {}
    subtopic_map = {}
    type_map = {}
    for subtopic in qrels:
        if hasattr(subtopic, '_fields') and _type_valid(subtopic, type_map, SubtopicQrel):
            # NamedTuple version
            query_id, subtopic_id, doc_id, relevance = subtopic.query_id, subtopic.subtopic_id, subtopic.doc_id, subtopic.relevance
        elif isinstance(subtopic, tuple) and len(subtopic) == 4:
            # [(query_id, subtopic_id, doc_id, relevance)]
            query_id, subtopic_id, doc_id, relevance = subtopic
        else:
            raise RuntimeError('unsupported qrels format')
        if query_id not in result:
            result[query_id] = []
        result[query_id].append((
            subtopic_map.setdefault(subtopic_id, len(subtopic_map)),
            doc_id,
            1 if relevance >= relevance_level else 0
        ))
    for qid in result:
        _pyndeval.set_global_alpha_beta(alpha, beta)
        result[qid] = _pyndeval.Qrels(result[qid], max_cutoff)
    return result


def _coerce_run_iter(run):
    type_map = {}
    last_qid = None
    scoredocs = None
    for rec in run:
        if hasattr(rec, '_fields') and _type_valid(rec, type_map, ScoredDoc):
            query_id, doc_id, score = rec.query_id, rec.doc_id, rec.score
        elif isinstance(rec, tuple) and len(rec) == 3:
            query_id, doc_id, score = rec
        else:
            raise RuntimeError('unsupported run format')
        if last_qid != query_id:
            if last_qid is not None:
                scoredocs = sorted(scoredocs, key=lambda x: (-x[1], x[0]))
                scoredocs = [(did, rank+1) for rank, (did, score) in enumerate(scoredocs)]
                yield last_qid, scoredocs
            last_qid = query_id
            scoredocs = []
        scoredocs.append((doc_id, score))
    if last_qid is not None:
        scoredocs = sorted(scoredocs, key=lambda x: (-x[1], x[0]))
        scoredocs = [(did, rank+1) for rank, (did, score) in enumerate(scoredocs)]
        yield last_qid, scoredocs


def _type_valid(subtopic, type_map, Type):
    t = type(subtopic)
    if t not in type_map:
        type_map[t] = set(subtopic._fields) & set(Type._fields) == len(Type._fields)
    return type_map[t]
