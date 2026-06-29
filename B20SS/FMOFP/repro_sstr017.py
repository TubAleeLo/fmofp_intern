"""
Standalone reproduction for SSTR-017 — Message processing priority inversion.

WHY THIS SCRIPT EXISTS
----------------------
The bug lives in MessageQueueManager._sort_queue_by_priority:

    sorted_queue = sorted(queue_list, key=priority_comparator, reverse=True)

The priority scheme is 0 = highest, 1 = normal, 2 = lowest (per MP[1]), and
MP[1.1] requires lower-numbered priorities to be placed FIRST. Sorting with
reverse=True puts the HIGHEST number (lowest priority) first, so the queue
comes out exactly backwards — low-priority messages get processed ahead of
critical ones.

The inversion is hard to see in a normal run because the queue only gets
sorted when it already holds more than one message, and those messages have
to carry DIFFERENT priorities for the ordering to matter. Quiet queues never
reveal it.

This script drives the REAL sorting logic. It avoids constructing the full
MessageQueueManager (a singleton with live RT dependencies) by building a
minimal stand-in object that carries the one attribute the method touches
(system_queues) and then invoking the unbound real methods
_sort_queue_by_priority and _get_message_priority_value on it. The sorting
code being exercised is the actual product code, unmodified.

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

    We borrow the REAL methods from MessageQueueManager (unbound) and run them
    against this object, so the actual product sorting logic is exercised
    without constructing the full singleton and its RT dependencies.
    """

    # Bind the real methods from the product class.
    _sort_queue_by_priority = MessageQueueManager._sort_queue_by_priority
    _get_message_priority_value = MessageQueueManager._get_message_priority_value

    def __init__(self):
        self.system_queues = {}


def make_msg(label, priority):
    """A message dict shaped the way _get_message_priority_value reads it."""
    return {"label": label, "metadata": {"priority": priority}}


def main():
    harness = _QueueHarness()
    destination = "radar"

    # Enqueue in arrival order: a low-priority, then normal, then the
    # critical high-priority message arrives last.
    harness.system_queues[destination] = deque([
        make_msg("low-priority status spam", 2),
        make_msg("normal telemetry", 1),
        make_msg("CRITICAL mode-change command", 0),
    ])

    arrival = [
        (m["label"], m["metadata"]["priority"])
        for m in harness.system_queues[destination]
    ]

    print("=" * 72)
    print("SSTR-017 reproduction — message processing priority inversion")
    print("=" * 72)
    print("Priority scheme: 0 = highest, 1 = normal, 2 = lowest")
    print("Requirement (MP[1.1]): lower-numbered priority must be processed FIRST")
    print("-" * 72)
    print("Arrival order (priority):")
    for label, pri in arrival:
        print(f"    [{pri}] {label}")
    print("-" * 72)

    # Run the REAL product sorting method.
    harness._sort_queue_by_priority(destination)

    result = [
        (m["label"], m["metadata"]["priority"])
        for m in harness.system_queues[destination]
    ]
    order = [pri for _, pri in result]

    print("Dispatch order after _sort_queue_by_priority (priority):")
    for label, pri in result:
        print(f"    [{pri}] {label}")
    print("-" * 72)

    correct = order == sorted(order)            # ascending: 0,1,2
    print(f"Resulting priority sequence: {order}")
    print(f"Correct (ascending, highest first): {sorted(order)}")
    if not correct:
        first_label = result[0][0]
        print("-" * 72)
        print("RESULT: BUG CONFIRMED. The queue is sorted in DESCENDING priority")
        print(f"        order, so '{first_label}' (priority {order[0]}) is")
        print("        processed first while the CRITICAL priority-0 message is")
        print("        pushed to the back. reverse=True inverts the intended order.")
    else:
        print("RESULT: Queue sorted correctly (highest priority first).")
    print("=" * 72)


if __name__ == "__main__":
    main()
