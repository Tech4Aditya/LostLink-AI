"""
Minimal Recall@K evaluator.

Input JSONL:
{"query_id":"lost_1","candidate_ids":["found_2","found_8",...],"positive_id":"found_8"}

Usage:
python evaluate_retrieval.py data/eval/retrieval.jsonl
"""
import json, sys

def recall_at(rows, k):
    return sum(r["positive_id"] in r["candidate_ids"][:k] for r in rows) / max(len(rows), 1)

if __name__ == "__main__":
    path = sys.argv[1]
    rows = [json.loads(x) for x in open(path, encoding="utf-8") if x.strip()]
    print({"samples": len(rows), "recall@1": recall_at(rows,1), "recall@5": recall_at(rows,5), "recall@10": recall_at(rows,10)})
