# MarkdownViewDesk

MarkdownViewDesk is a small Windows-friendly PyQt6 GUI application for opening and reading `README.md` files, AmigaGuide `.guide` files, `FILE_ID.DIZ` descriptions and other local text documents.

## What it does

- Opens `.md`, `.markdown`, `.mdown`, `.mkd`, `.guide`, `.diz` and `.txt` files.
- Renders Markdown with a clean README-style layout.
- Shows Markdown headings and AmigaGuide nodes in an outline panel.
- Displays fenced code blocks with syntax highlighting.
- Resolves relative local image and file links from the Markdown file location.
- Supports app-wide themes: Light, Dark, Sepia, Ocean, Matrix, Purple and Hellfire / Hölle.
- Supports English and German UI text.
- Includes a source view toggle.
- Renders basic AmigaGuide `.guide` documents with node sections and internal LINK buttons.
- Displays `FILE_ID.DIZ` / `.diz` files in a fixed-width 45-column view and highlights overflow instead of rewrapping lines.
- Can be registered as a Windows `.md`, `.guide` and `.diz` file handler after building the EXE.

## Quick start from source

1. Install Python 3.10 or newer.
2. Run `install_windows.bat`.
3. Run `run_windows.bat`.
4. Open `sample_readme.md`, `sample_amigaguide.guide`, `sample_file_id.diz` or drag a supported document into the window.

## Build an EXE

Run:

```bat
build_windows_onedir.bat
```

The recommended output is:

```text
dist\MarkdownViewDesk\MarkdownViewDesk.exe
```

`build_windows_onefile_experimental.bat` is included, but Qt WebEngine applications are usually more reliable in onedir mode because the embedded browser engine has helper binaries and resources.

## Register supported document files on Windows

After building the EXE, run:

```bat
register_md_filetype_user.bat
```

This writes user-level registry keys under `HKCU\Software\Classes` for `.md`, `.markdown`, `.mdown`, `.mkd`, `.guide` and `.diz`. Windows may still ask you once to confirm the default app for a file type.

To remove the registration keys again:

```bat
unregister_md_filetype_user.bat
```

## Offline install option

On an online PC, run:

```bat
download_wheelhouse_windows.bat
```

Copy the folder to the offline PC and run:

```bat
install_from_wheelhouse_windows.bat
```

## Original source / updates

`github.com/zeittresor`

## Notes

This program disables JavaScript in the rendered document view and blocks local Markdown content from loading remote URLs directly. Clicking normal web links opens them in the system browser.

## License

GPL-3.0-or-later.

## Changelog

### v0.1.4

- Added basic AmigaGuide `.guide` support with node parsing and clickable internal `LINK` commands.
- Added `FILE_ID.DIZ` / `.diz` support with fixed-width display, 45-column boundary and overflow highlighting.
- Updated open dialog, drag/drop and Windows file registration for `.guide` and `.diz`.
- Added sample `.guide` and `.diz` files.

### v0.1.2

- Improved theme system so themes affect the whole application, not only the rendered Markdown area.
- Added Ocean, Matrix and Hellfire / Hölle themes.
- Improved code block contrast by using theme-specific Pygments styles and stronger code-block CSS overrides.
- Added English/German UI selector.
- Added visible original source / updates reference in About and README.
- Added colored console output to installer/update/build scripts.

### v0.1.1

- Fixed missing `QLineEdit` import.

### v0.1.0

- Initial Markdown viewer.
