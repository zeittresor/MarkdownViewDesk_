# MarkdownViewDesk sample

This is a small Markdown sample for testing the viewer.

## Checklist

- [x] Headings
- [x] Tables
- [x] Code blocks
- [x] Task list items
- [ ] Relative image and file links

## Code block contrast test

```python
def render_theme(name: str) -> None:
    print(f"Theme loaded: {name}")
```

```bat
install_windows.bat
run_windows.bat
```

Inline code should also be readable: `MarkdownViewDesk.exe README.md`.

## Table

| Theme | Purpose |
| --- | --- |
| Light | Neutral daytime view |
| Dark | Low-light view |
| Sepia | Warm reading view |
| Ocean | Blue-green dark view |
| Matrix | Green terminal-style view |
| Aurora | Northern-light dark view |
| Purple | Violet/purple dark view |
| Hölle | Warm red/orange dark view |

## Quote

> Markdown should be readable first and decorative second.

## Original source / updates

`github.com/zeittresor`

## Additional file formats

MarkdownViewDesk can also open:

- `sample_amigaguide.guide` for basic AmigaGuide node/link rendering
- `sample_file_id.diz` for fixed-width FILE_ID.DIZ display
