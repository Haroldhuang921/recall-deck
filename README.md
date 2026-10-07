# Recall Deck website

Served by GitHub Pages at <https://haroldhuang921.github.io/recall-deck/>.

- `privacy/index.html` is the app's privacy policy. It is generated from `PRIVACY.md` in the app project, so edit that file and rebuild:

  ```bash
  python3 tools/build_privacy.py path/to/RecallDeck/PRIVACY.md
  ```

- `index.html` is a small home page. `style.css` is shared by both pages.
