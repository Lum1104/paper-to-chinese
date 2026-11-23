#!/usr/bin/env python3
"""Build a translated LaTeX working copy with bounded XeLaTeX passes."""
import argparse
import hashlib
from pathlib import Path
import re
import shutil
import subprocess
import sys


def state(root, name):
    paths = [root / (name + ext) for ext in ('.aux', '.toc', '.out', '.lof', '.lot')]
    paths.extend(sorted(p for p in root.rglob('*.aux') if p not in paths))
    return tuple((str(p), hashlib.sha256(p.read_bytes()).digest())
                 for p in paths if p.is_file())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('entry', type=Path, help='root .tex file in a disposable work copy')
    args = parser.parse_args()
    entry = args.entry.resolve()
    if not entry.is_file() or entry.suffix != '.tex':
        parser.error('entry must be an existing .tex file')
    engine = shutil.which('xelatex')
    if not engine:
        parser.error('xelatex not found')
    root, name = entry.parent, entry.stem
    pdf = root / (name + '.pdf')
    output = root / (name + '.build.txt')
    previous = None
    command = [engine, '-no-shell-escape', '-interaction=nonstopmode',
               '-halt-on-error', '-file-line-error', './' + entry.name]
    for _ in range(4):
        try:
            with output.open('wb') as log:
                result = subprocess.run(command, cwd=root, stdout=log,
                                        stderr=subprocess.STDOUT, timeout=120)
        except subprocess.TimeoutExpired:
            print(f'XeLaTeX timed out; see {output}', file=sys.stderr)
            return 1
        build = output.read_text(errors='replace')
        if result.returncode or not pdf.is_file() or 'Output written on' not in build:
            print(build[-2200:], file=sys.stderr)
            return 1
        current = state(root, name)
        if current == previous:
            if re.search(r'undefined references|undefined citations|Missing character:', build, re.I):
                print(f'PDF has unresolved references or missing glyphs; see {output}', file=sys.stderr)
                return 2
            print(pdf)
            return 0
        previous = current
    print(f'References did not stabilize after four passes; see {output}', file=sys.stderr)
    return 2


if __name__ == '__main__':
    sys.exit(main())
