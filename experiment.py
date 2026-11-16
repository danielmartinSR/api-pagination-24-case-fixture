#!/usr/bin/env python3
"""Generate a deterministic 24-case API pagination client fixture.
This is synthetic protocol logic, not a test of any live API/provider.
"""
import csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CASES = []
patterns = [
    ("nonempty_new_cursor", ["a", "b"], "c{n}", [], ["b", "x{n}"], True),
    ("empty_page_new_cursor", [], "c{n}", [], ["x{n}", "y{n}"], True),
    ("no_continuation", ["a{n}"], None, [], [], False),
    ("repeated_cursor", ["a{n}"], "seen", ["seen"], ["a{n}", "z{n}"], False),
    ("previously_seen_cursor", ["a{n}"], "old{n}", ["old{n}"], ["q{n}"], False),
    ("empty_next_page_new_cursor", ["a{n}"], "c{n}", [], [], True),
]
for group, (name, current, nxt, seen, next_items, expected) in enumerate(patterns):
    for variant in range(4):
        n = variant + 1
        current_items = [x.format(n=n) for x in current]
        next_items_case = [x.format(n=n) for x in next_items]
        next_cursor = nxt.format(n=n) if nxt else None
        seen_case = [x.format(n=n) for x in seen]
        # The current cursor is already visited; the fixture asks whether to request next_cursor.
        if name == "repeated_cursor":
            next_cursor = "seen"
        if name == "previously_seen_cursor":
            next_cursor = f"old{n}"
        expected_action = "continue" if expected and next_cursor not in seen_case else "stop"
        CASES.append({
            "case_id": f"P{group+1}{variant+1}",
            "scenario": name,
            "current_cursor": f"page{group+1}-{n}",
            "next_cursor": next_cursor,
            "seen_cursors": seen_case,
            "current_item_ids": current_items,
            "next_page_item_ids": next_items_case,
            "expected_action": expected_action,
            "expected_unique_items": len(set(current_items + (next_items_case if expected_action == "continue" else []))),
        })

POLICIES = ["empty-page-stop", "blind-follow", "cursor-cycle-guard", "cycle-guard-plus-dedupe"]
rows=[]
for c in CASES:
    has_items=bool(c["current_item_ids"])
    next_cursor=c["next_cursor"]
    unseen=next_cursor is not None and next_cursor not in c["seen_cursors"]
    decisions={
        "empty-page-stop": "continue" if has_items and unseen else "stop",
        "blind-follow": "continue" if next_cursor is not None else "stop",
        "cursor-cycle-guard": "continue" if unseen else "stop",
        "cycle-guard-plus-dedupe": "continue" if unseen else "stop",
    }
    for policy in POLICIES:
        continue_page=decisions[policy] == "continue"
        items=c["current_item_ids"] + (c["next_page_item_ids"] if continue_page else [])
        if policy == "cycle-guard-plus-dedupe":
            items=list(dict.fromkeys(items))
        rows.append({
            "case_id":c["case_id"], "scenario":c["scenario"], "policy":policy,
            "expected_action":c["expected_action"], "actual_action":decisions[policy],
            "action_correct":decisions[policy] == c["expected_action"],
            "expected_unique_items":c["expected_unique_items"],
            "returned_item_rows":len(items), "unique_item_ids":len(set(items)),
            "duplicate_rows":len(items)-len(set(items)),
        })
summary={}
for policy in POLICIES:
    pr=[r for r in rows if r["policy"]==policy]
    summary[policy]={
        "cases":len(pr),
        "action_errors":sum(not r["action_correct"] for r in pr),
        "action_accuracy_pct":round(100*sum(r["action_correct"] for r in pr)/len(pr),1),
        "duplicate_rows_returned":sum(r["duplicate_rows"] for r in pr),
        "expected_unique_items":sum(r["expected_unique_items"] for r in pr),
        "returned_item_rows":sum(r["returned_item_rows"] for r in pr),
    }
with (ROOT/"cases.json").open("w") as f: json.dump(CASES,f,indent=2)
with (ROOT/"results.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
with (ROOT/"summary.json").open("w") as f: json.dump({"case_count":len(CASES),"policy_summary":summary,"scope":"constructed deterministic client fixture; no live API/provider calls"},f,indent=2)
print(json.dumps({"case_count":len(CASES),"policy_summary":summary},indent=2))
