#!/usr/bin/env python3
"""Prevent an upstream callback failure from deadlocking Mach shutdown."""
import sys
from pathlib import Path

source = Path(sys.argv[1]) / "python/mach/mach/main.py"
old = '''                context.telemetry = future.result()
                report_invocation_metrics(context.telemetry, handler.name)
                context._telemetry_init_done.set()'''
new = '''                # RECHTECK: always release shutdown wait, even when metrics fail.
                try:
                    context.telemetry = future.result()
                    report_invocation_metrics(context.telemetry, handler.name)
                finally:
                    context._telemetry_init_done.set()'''
text = source.read_text(encoding="utf-8")
if new in text:
    print("Mach shutdown fix already applied.")
elif text.count(old) == 1:
    source.write_text(text.replace(old, new), encoding="utf-8", newline="\n")
    print("Mach shutdown fix applied.")
else:
    raise SystemExit("Unexpected Mach callback source; refusing to patch.")
