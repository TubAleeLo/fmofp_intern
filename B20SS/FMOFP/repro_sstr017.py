"""
Standalone reproduction for SSTR-017 — Message processing priority inversion.

WHY THIS SCRIPT EXISTS
----------------------
The bug lives in MessageQueueManager._sort_queue_by_priority:

    sorted_queue = sorted(queue_list, key=priority_comparator, reverse=True)

The priority scheme is 0 = highest, 1 = normal, 2 = lowest (per MP[1]), and
MP[1.1] requires lower-numbered priorities to be placed FIRST. Sorting with
reverse=True puts the HIGHEST number (lowest priority) first, so the queue
comes out exactly backwards.

The inversion is hard to see in a normal run because the queue only gets
sorted when it already holds more than one message, and those messages must
carry DIFFERENT priorities for ordering to matter.

HOW THIS SCRIPT WORKS
---------------------
It exercises the REAL sorting logic. It avoids constructing the full
MessageQueueManager (a singleton with live RT dependencies) by binding the
real, unbound methods (_sort_queue_by_priority, _get_message_priority_value)
onto a minimal stand-in object that carries the one attribute the method
touches (system_queues). The sorting code being run is the actual product
code, unmodified.

THOROUGHNESS
------------
Several scenarios are tested, each asserting the queue ends up in ascending
priority order (0 first). A combined verdict reports BUG CONFIRMED if ANY
scenario comes out wrong, and NO BUG only if ALL scenarios pass — so the
script correctly flips to NO BUG once reverse=True is fixed to reverse=False.

USAGE
-----
    cd B20SS
    python -m FMOFP.repro_sstr017
"""

import os
import sys
from collections import deque

# The codebase mixes "FMOFP."-prefixed and bare imports, so both B20SS/ and
# B20SS/FMOFP/ must be importable. Mirror the app's path setup.
_FMOFP_DIR = os.path.dirname(os.path.abspath(__file__))   # .../B20SS/FMOFP
_PROJECT_ROOT = os.path.dirname(_FMOFP_DIR)               # .../B20SS
for _p in (_PROJECT_ROOT, _FMOFP_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from FMOFP.MIL_STD_1553B.Remote_Terminal.RT_messaging.message_queue_manager import (
    MessageQueueManager,
)


class _QueueHarness:
    """Minimal stand-in exposing only what _sort_queue_by_priority touches.
    Borrows the REAL methods from MessageQueueManager (unbound) so the actual
    product sorting logic is exercised."""

    _sort_queue_by_priority = MessageQueueManager._sort_queue_by_priority
    _get_message_priority_value = MessageQueueManager._get_message_priority_value

    def __init__(self):
        self.system_queues = {}


def make_msg(label, priority):
    """A message dict shaped the way _get_message_priority_value reads it."""
    return {"label": label, "metadata": {"priority": priority}}


def run_scenario(name, arrival_priorities):
    """Enqueue messages with the given priorities, run the REAL sort, and
    return (passed, arrival_list, result_list)."""
    harness = _QueueHarness()
    destination = "radar"
    harness.system_queues[destination] = deque(
        make_msg(f"msg(p={p})", p) for p in arrival_priorities
    )
    harness._sort_queue_by_priority(destination)
    result = [m["metadata"]["priority"]
              for m in harness.system_queues[destination]]
    # Correct behavior: ascending priority (0 = highest, processed first),
    # preserving the same multiset of priorities.
    expected = sorted(arrival_priorities)
    passed = result == expected
    return passed, list(arrival_priorities), result, expected


def main():
    scenarios = [
        ("mixed, critical arrives last",      [2, 1, 0]),
        ("already in correct order",          [0, 1, 2]),
        ("reverse order",                     [2, 2, 1, 0]),
        ("duplicate priorities",              [1, 0, 1, 2, 0]),
        ("two high-priority among low",       [2, 0, 2, 0, 2]),
        ("single message (trivial)",          [1]),
    ]

    print("=" * 72)
    print("SSTR-017 reproduction — message processing priority inversion")
    print("=" * 72)
    print("Priority scheme: 0 = highest, 1 = normal, 2 = lowest")
    print("Requirement (MP[1.1]): lower-numbered priority processed FIRST")
    print("Correct result = ascending priority order (0 first).")
    print("-" * 72)
    print(f"{'scenario':<32} | {'arrival':>14} | {'result':>14} | ok?")
    print("-" * 72)

    failures = 0
    for name, arrival in scenarios:
        passed, arr, result, expected = run_scenario(name, arrival)
        if not passed:
            failures += 1
        ok = "PASS" if passed else "FAIL"
        print(f"{name:<32} | {str(arr):>14} | {str(result):>14} | {ok}")

    print("-" * 72)
    if failures:
        print(f"RESULT: BUG CONFIRMED. {failures} of {len(scenarios)} scenarios came out")
        print("        in DESCENDING priority order — low-priority messages ahead of")
        print("        critical ones. _sort_queue_by_priority uses reverse=True, which")
        print("        inverts the intended order (should be reverse=False).")
    else:
        print(f"RESULT: NO BUG. All {len(scenarios)} scenarios sorted in ascending")
        print("        priority order (highest priority first), as required.")
    print("=" * 72)


if __name__ == "__main__":
    main()
