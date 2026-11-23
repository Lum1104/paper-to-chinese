# XeLaTeX and layout troubleshooting

## First-time TeX & CJK font setup (install once, reuse later)

Check what is already installed before installing anything:

```sh
which xelatex
fc-list :lang=zh
```

If both exist, skip installation. Otherwise, install a minimal working setup (avoid `texlive-full`, which is several GB and often times out):

### 1. With root / `sudo` (Debian/Ubuntu)

```sh
apt-get update && apt-get install -y --no-install-recommends \
  texlive-xetex texlive-lang-chinese texlive-latex-extra fonts-noto-cjk
```

If a specific paper needs extra packages later, add only what is missing (e.g., `texlive-science` or `texlive-publishers`).

### 2. Without root (user-space TinyTeX)

Install TinyTeX into `~/.TinyTeX` and persist it in `PATH` so future sessions reuse it directly:

```sh
curl -fsSL "https://yihui.org/tinytex/install-bin-unix.sh" | sh
```

Add the printed `~/.TinyTeX/bin/<arch>` directory to `~/.bashrc` / `~/.profile`, then install `xecjk` (and any missing packages reported during compilation) via `tlmgr install xecjk`.

### 3. Missing CJK fonts without root

Download an open-source CJK font (such as Source Han Serif/Sans or Fandol `.otf`) into `~/.local/share/fonts` and run `fc-cache -fv` for persistent reuse. If `fc-cache` is unavailable, place the font file in the work directory and load it by path:

```tex
\setCJKmainfont[Path=./]{SourceHanSerifSC-Regular.otf}
```

### 4. Offline environment without TeX

If TeX cannot be installed at all, finish the translation with `xeCJK` configured and deliver the translated source archive so the user can compile it in Overleaf with the XeLaTeX compiler.

## Preamble & build helper

For a normal UTF-8 project, preserve the document class and use this in the preamble after the template's fonts:

```tex
\usepackage{xeCJK}
\setCJKmainfont{Noto Serif CJK SC}
\setCJKsansfont{Noto Sans CJK SC}
\setCJKmonofont{Noto Sans Mono CJK SC}
```

Check the installed font names first. Translate generated captions and reference-section headings only if needed and use the class's hooks if it overrides them. A bundled .bbl can usually be reused unchanged; run the matching BibTeX/Biber backend when it is absent or stale. Preserve a supplied proceedings disclaimer, but mark the title page as a translation, not a new publication.

Run `python3 scripts/compile.py /path/to/work-copy/main.tex` from the skill folder. The helper intentionally does not install packages, run bibliography commands, or start any network downloads. It uses the work copy as the compilation directory and stores the final pass output at `<jobname>.build.txt`. If the PDF looks clipped despite a successful compile, inspect the TeX log for overfull boxes and render the affected pages again.

### If the cloud image has no TeX format

An installed `xelatex` executable does not imply that the Kpathsea file databases or format files exist. Check `kpsewhich xelatex.ini` and `kpsewhich -format=fmt xelatex.fmt`. In a Debian-style image with a missing filename database, try a process-local override like `TEXMF="{/path/to/local-texmf,/usr/share/texmf,/usr/share/texlive/texmf-dist}"` (omit absent trees; do not use `!!` if its database is absent). If the ini is visible but the format is missing, run in a writable directory:

```sh
xetex -ini -etex -jobname=xelatex -progname=xelatex xelatex.ini
export TEXFORMATS="$PWD"
```

When xeCJK is missing or newer than the installed LaTeX kernel, use a compatible distribution package from the same TeX release. Extract its TeX tree into writable storage and include that tree in the process-local search path; don't change system TeX or user dotfiles just for one document. A fresh CTAN package can require a newer kernel. Confirm the PDF renders Chinese and Latin text before committing to a long rebuild.
