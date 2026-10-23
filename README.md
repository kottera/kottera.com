# kottera.com

The source of [kottera.com](https://kottera.com): one page saying what
tera is, that it is a 0.x developer preview, and how to follow along. It
has no waitlist and collects nothing.

## Layout

- `docs/` is the site, exactly as served: `index.html`, `style.css`,
  `CNAME` (the custom domain) and `.nojekyll` (serve the files as they
  are, with no Jekyll build).
- `.github/workflows/ci.yml` runs `.github/scripts/check-site.py docs` on
  every pull request and every push to `main`: every page is well-formed
  HTML, and every link that stays on the site resolves to a file in
  `docs/`. It runs on GitHub-hosted runners with a read-only token.

## How the page is published

GitHub Pages serves `docs/` from the `main` branch (Settings → Pages →
Deploy from a branch, `main`, `/docs`), at the custom domain in
`docs/CNAME`. There is no build step and no deploy workflow: what is
merged to `main` is what is served. Pages is not yet turned on.

## Conventions

- **Changes land through pull requests** into `main`, merged once CI is
  green. Nothing is pushed to `main` directly.
- **The page's words are approved by Ed Funnekotter before they merge.**
  Markup and style are not words; a change of wording is.
- **Every commit is signed off** with a `Signed-off-by:` line
  (`git commit -s`), under the [Developer Certificate of
  Origin](https://developercertificate.org/).
- **No `Co-authored-by:` line**, in a commit, a pull request's title or
  description, or a squash merge's message. Pass a squash merge's
  message explicitly, because GitHub's default adds such lines.

## Licence

[Apache License 2.0](LICENSE).
