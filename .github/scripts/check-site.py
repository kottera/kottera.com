#!/usr/bin/env python3
"""Check the site under a directory: every HTML page is well-formed, and
every link that does not leave the site resolves to a file in it.

Usage: check-site.py <site-directory>

Well-formed means one doctype, every element closed in order (void
elements excepted), no stray end tag, and no duplicate attribute. A link is
an href or src. One with a scheme (https:, mailto:) or a leading // leaves
the site and is not followed; a fragment-only link must name an id on its
page. Anything else is resolved against the page, or against the site's
root when it starts with /, and must name a file in the site (a directory
resolves to its index.html)."""

import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

VOID = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "source", "track", "wbr",
}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.errors = []
        self.links = []
        self.ids = set()
        self.doctypes = 0

    def where(self):
        line, col = self.getpos()
        return f"{line}:{col + 1}"

    def handle_decl(self, decl):
        if decl.lower().startswith("doctype"):
            self.doctypes += 1
            if decl.lower() != "doctype html":
                self.errors.append(f"{self.where()}: doctype is not <!DOCTYPE html>")

    def handle_starttag(self, tag, attrs):
        self.attrs(tag, attrs)
        if tag not in VOID:
            self.stack.append((tag, self.where()))

    def handle_startendtag(self, tag, attrs):
        self.attrs(tag, attrs)
        if tag not in VOID:
            self.errors.append(f"{self.where()}: <{tag}/> is not a void element")

    def handle_endtag(self, tag):
        if tag in VOID:
            self.errors.append(f"{self.where()}: </{tag}> closes a void element")
            return
        if not self.stack or self.stack[-1][0] != tag:
            open_ = f"<{self.stack[-1][0]}> from {self.stack[-1][1]}" if self.stack else "nothing"
            self.errors.append(f"{self.where()}: </{tag}> does not close the open element ({open_})")
            return
        self.stack.pop()

    def attrs(self, tag, attrs):
        seen = set()
        for name, value in attrs:
            if name in seen:
                self.errors.append(f"{self.where()}: <{tag}> repeats attribute {name}")
            seen.add(name)
            if name == "id" and value:
                self.ids.add(value)
            if name in ("href", "src"):
                self.links.append((self.where(), value or ""))


def check(root):
    errors = []
    pages = sorted(root.rglob("*.html"))
    if not pages:
        return [f"{root}: no HTML page"]
    for path in pages:
        rel = path.relative_to(root)
        page = Page()
        page.feed(path.read_text(encoding="utf-8"))
        page.close()
        errors += [f"{rel}:{e}" for e in page.errors]
        if page.doctypes != 1:
            errors.append(f"{rel}: has {page.doctypes} doctypes, not 1")
        for tag, at in page.stack:
            errors.append(f"{rel}:{at}: <{tag}> is never closed")
        for at, link in page.links:
            problem = resolve(root, path, link, page.ids)
            if problem:
                errors.append(f"{rel}:{at}: link {link!r} {problem}")
    return errors


def resolve(root, page, link, ids):
    if not link:
        return "is empty"
    parts = urlsplit(link)
    if parts.scheme or parts.netloc:
        return None
    if not parts.path:
        return None if unquote(parts.fragment) in ids else "names no id on this page"
    path = unquote(parts.path)
    base = root if path.startswith("/") else page.parent
    target = (base / path.lstrip("/")).resolve()
    if not target.is_relative_to(root.resolve()):
        return "leaves the site"
    if target.is_dir():
        target = target / "index.html"
    return None if target.is_file() else "names no file in the site"


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: check-site.py <site-directory>")
    root = Path(sys.argv[1])
    errors = check(root)
    for e in errors:
        print(e, file=sys.stderr)
    if errors:
        sys.exit(1)
    print(f"{root}: every page is well-formed and every link resolves")


if __name__ == "__main__":
    main()
