# H — Packaging, distribution and downstream integration
Accessed: 2026-09-01

## Status
See end of file (COMPLETE).

### Fetch plan (batch 3, logged before fetching; WebSearch assumed exhausted)
Candidates: jellyfin.org/docs/general/server/metadata/media-segments ; raw jellyfin MediaSegmentType.cs under MediaBrowser.Model/MediaSegments/ (retry) ; kodi.wiki/view/Edit_decision_list (retry) ; docs.pypi.org/trusted-publishers ; support.pocketcasts.com/knowledge-base/preselect-chapters ; podcasters.apple.com/support/5482-using-chapters-on-apple-podcasts ; github.com/mpv-player/mpv/blob/master/DOCS/edl-mpv.rst ; raw simonw/llm docs/plugins/plugin-hooks.md ; peps.python.org/pep-0751 ; scientific-python.org/specs/spec-0000 ; w3.org/community/about/process/cg-final-reports ; rfc-editor.org/about/independent ; github.com/SchemaStore/schemastore CONTRIBUTING ; github.com/kiwicom/pytest-recording ; promptfoo.dev docs ci-cd ; pypi.org/project/keyring ; aider.chat/docs/config/api-keys.html ; cli.github.com/manual/gh_auth_login ; docs.brew.sh/Homebrew-and-Python ; overcast.fm/podcasterinfo ; antennapod.org docs ; podcastaddict.com/faq ; comskip.org ; getchannels.com docs ; emby.media ; videojs.org/guides/text-tracks ; vidstack.io docs ; podlove simple chapters spec ; whisperX / faster-whisper pyproject ; m4b-tool README.

## Sources

### S1. mpv manual (master) — https://mpv.io/manual/master/
- Type: product (docs)
- Verified: fetched
- Key facts:
  - `--chapters-file=<filename>`: "Load chapters from this file, instead of using the chapter metadata found in the main file." Accepts media files (e.g. mkv) or "pseudo-formats such as ffmetadata"; OGM/XML chapter files are NOT supported directly.
  - `--sub-file` is an alias for `--sub-files-append` (list option).
  - `--chapter-seek-threshold` default 5.0 s.
  - `edl://` protocol: "Stitch together parts of multiple files and play them" (detail in DOCS/edl-mpv.rst, not fetched yet).
- Relevance to AdVTT:
  - An ffmetadata file with [CHAPTER] blocks is directly loadable by mpv with zero player changes → chapter carrier works today in mpv.
  - mpv exposes `chapter-list` to Lua scripts (see S13 chapterskip), so title-regex auto-skip is one small script away.

### S2. llm (Simon Willison) — Setup / keys docs — https://llm.datasette.io/en/stable/setup.html
- Type: product (docs)
- Verified: fetched
- Key facts:
  - Install paths documented: `pip install llm`, `pipx install llm`, `uv tool install llm`, `brew install llm`.
  - `llm keys set openai` prompts "Enter key:"; stored in `keys.json` under a per-platform user dir: macOS `~/Library/Application Support/io.datasette.llm/keys.json`, Linux `~/.config/io.datasette.llm/keys.json`; `llm keys path` prints location; `LLM_USER_PATH` overrides dir.
  - Precedence: `--key` CLI option → keys.json → env var (e.g. `OPENAI_API_KEY`).
  - `llm logs off` disables prompt/response logging.
- Relevance to AdVTT:
  - A proven, widely copied UX for multi-provider key handling in a Python LLM CLI: plain JSON file in platform user dir + env-var fallback + `--key`. No Keychain by default.
  - Same four install channels (pip/pipx/uv tool/brew) are the 2026 norm for a Python CLI.

### S3. Pocket Casts — Chapters support article — https://support.pocketcasts.com/knowledge-base/chapters/
- Type: product (docs)
- Verified: fetched
- Key facts:
  - Android: reads "MP3 chapters, Podcast Index, and Podlove" chapters; does not support M4A chapters. iOS: AAC and MP3 chapters plus Podcast Index and Podlove.
  - "Preselect Chapters" lets Plus/Patron subscribers "choose which chapters to play and skip others" — a paid feature; it is a per-episode manual deselect, not a title rule.
  - Chapter title + arrows always show on Now Playing; cannot be hidden.
  - AI-generated chapters unavailable for user-uploaded custom files (they lack Pocket Casts metadata) — implies uploaded files are supported but embedded-chapter behaviour for uploads not stated here.
- Relevance to AdVTT:
  - If AdVTT writes ID3 CHAP or JSON chapters titled e.g. "[Ad] Acme", Pocket Casts users can deselect them per episode (paid tier). No auto-skip-by-title exists.

### S4. chapterskip.lua (po5) — https://raw.githubusercontent.com/po5/chapterskip/master/chapterskip.lua
- Type: repo
- Verified: fetched
- Key facts:
  - Options: `enabled = true`, `skip_once = true`, `categories = ""` (user-defined), plus built-in categories as Lua patterns: `prologue = "^Prologue/^Intro"`, `opening = "^OP/ OP$/^Opening"`, `ending = "^ED/ ED$/^Ending"`, `preview = "Preview$"`.
  - Matching: iterates chapter titles, `if string.match(title, pattern) then return true`.
  - No SponsorBlock/yt-dlp-specific handling in the script itself; a user adds a pattern such as `sponsor=SponsorBlock` in chapterskip.conf (not verified from file; inferred from the categories mechanism).
- Relevance to AdVTT:
  - A one-line user config (`ads=^\[Ad\]`) would auto-skip AdVTT-titled chapters in mpv today. Zero code changes on the consumer side; the user must opt in — matching the "auto-skip off by default" principle.

### S5. yt-dlp `modify_chapters.py` postprocessor — https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/postprocessor/modify_chapters.py
- Type: repo
- Verified: fetched
- Key facts:
  - `DEFAULT_SPONSORBLOCK_CHAPTER_TITLE = '[SponsorBlock]: %(category_names)l'` (module-level constant).
  - Removal uses ffmpeg concat demuxer with `inpoint`/`outpoint` entries via `_make_concat_opts()` → `concat_files()`, not `-ss/-to` per cut; optional `force_keyframes()` re-encode at cut timestamps.
  - Sponsor chapters carry an internal `_categories` list of `(category_id, start, end, category_name)`.
- Relevance to AdVTT:
  - The de-facto "ad chapter" naming convention in the wild is `[SponsorBlock]: Sponsor`. AdVTT could emit a compatible prefix (`[AdVTT]: Sponsor` or even literally `[SponsorBlock]: Sponsor`) so existing regexes (`--remove-chapters`, chapterskip) fire unchanged.
  - The concat-demuxer cut approach is the proven pattern for a lossless "cut ads" mode.

### S6. yt-dlp `pyproject.toml` — https://raw.githubusercontent.com/yt-dlp/yt-dlp/master/pyproject.toml
- Type: repo
- Verified: fetched
- Key facts:
  - `requires-python = ">=3.10"`; build backend hatchling >=1.27.0.
  - Core install has essentially no hard runtime deps; `default` extra pulls brotli, certifi, pycryptodomex, requests>=2.32.2, urllib3>=2.0.2, websockets>=13.0, mutagen, yt-dlp-ejs==0.8.0. Other extras: `curl-cffi`, `secretstorage`, `build`, `static-analysis` (ruff ~0.16), `test` (pytest ~9.0), `dev`.
  - Entry point `yt-dlp = "yt_dlp:main"`.
- Relevance to AdVTT:
  - Model for "stdlib-first core, everything optional via extras" — exactly AdVTT's shape (`advtt[mlx]`, `advtt[parakeet]`, `advtt[openai]`).
  - Hatchling + Python ≥3.10 is what the largest Python media CLI ships with in 2026.

### S7. VCR.py usage docs — https://vcrpy.readthedocs.io/en/latest/usage.html
- Type: product (docs)
- Verified: fetched
- Key facts:
  - Record modes: `once` (default; replay, record if no cassette, error on new request when cassette exists), `new_episodes`, `none`, `all`.
  - Cassettes are YAML files (e.g. `fixtures/vcr_cassettes/synopsis.yaml`).
  - Mentions `pytest-recording` as a pytest plugin adding network blocking.
- Relevance to AdVTT:
  - Standard way to make LLM-API-dependent tests deterministic and zero-cost in CI; `record_mode=none` in CI guarantees no accidental spend.

### S8. Hatch "Why Hatch?" — https://github.com/pypa/hatch/blob/master/docs/why.md
- Type: product (docs)
- Verified: fetched
- Key facts:
  - Hatchling: VCS-aware sdist defaults, project-name-based wheel inclusion, single-file config (no MANIFEST.in), reproducible builds, editable installs friendly to static analysis.
  - "If building extension modules is required then it is recommended that you continue using setuptools."
  - Document does NOT claim the Packaging Guide recommends Hatchling as default (checked).
- Relevance to AdVTT:
  - Pure-Python AdVTT has no extension modules → Hatchling is appropriate; yt-dlp (S6) uses it; llm (S18) still uses setuptools, so both are acceptable.

### S9. Podcast Namespace — JSON Chapters spec v1.2 — https://github.com/Podcastindex-org/podcast-namespace/blob/main/docs/examples/chapters/jsonChapters.md
- Type: spec
- Verified: fetched
- Key facts:
  - Version 1.2 (updated 2021-04-15). Top level: `version` (string, required), `chapters` (array, required); optional `author`, `title`, `podcastName`, `description`, `fileName`, `waypoints`.
  - Chapter: `startTime` (float seconds, required); optional `title`, `img`, `url`, `endTime`, `toc` (bool), `location`.
  - `toc:false`: "should not display visibly to the user in either the table of contents or as a jump-to point … a 'silent' chapter marker for the purpose of meta-data only."
  - No ad/sponsor guidance or field anywhere in the spec.
- Relevance to AdVTT:
  - `toc:false` gives a hidden-marker slot, but it hides the chapter from the UI — which defeats "let the listener skip it". Ad chapters should probably be `toc:true` with a conventional title, and any machine-readable ad flag needs an extension field (unspecified by v1.2; JSON is open so extra keys like `advtt` are tolerated by parsers that ignore unknown keys — needs testing).
  - There is NO existing ad-chapter naming convention in the podcast namespace.

### S10. uv — Tools guide — https://docs.astral.sh/uv/guides/tools/
- Type: product (docs)
- Verified: fetched
- Key facts:
  - `uvx ruff` ≡ `uv tool run ruff` (ephemeral); `uv tool install ruff` (persistent, isolated env, all executables).
  - Extras/with: `uvx --from 'mypy[faster-cache,reports]' mypy`, `uv tool install mkdocs --with mkdocs-material`.
  - `--python 3.10` pins interpreter; `uv tool upgrade --all`.
  - "installing a tool does not make its modules available in the current environment" — isolation by design.
- Relevance to AdVTT:
  - Recommended install line: `uv tool install 'advtt[mlx]'` / `uvx advtt`; document `--python 3.12` for MLX wheels.

### S11. PyPA guide — Publishing with GitHub Actions (Trusted Publishing) — https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/
- Type: spec/docs
- Verified: fetched
- Key facts:
  - Uses `pypa/gh-action-pypi-publish@release/v1`; job needs `permissions: id-token: write` ("IMPORTANT: mandatory for trusted publishing") and `environment: name: pypi, url: https://pypi.org/p/<package-name>`; separate `testpypi` environment.
  - Long-lived `PYPI_API_TOKEN` secrets "are obsolete now"; OIDC tokens are per-deployment and expire.
- Relevance to AdVTT:
  - Release pipeline: build once, publish to TestPyPI on every tag, PyPI behind a manually-approved environment; no stored API tokens.

### S12. Jellyfin `MediaSegmentsController.cs` — https://github.com/jellyfin/jellyfin/blob/master/Jellyfin.Api/Controllers/MediaSegmentsController.cs
- Type: repo
- Verified: fetched
- Key facts:
  - `GET /MediaSegments/{itemId}` with optional query `includeSegmentTypes`; returns `QueryResult<MediaSegmentDto>`; 404 if item missing.
  - Segments are resolved through `IMediaSegmentManager` (plugins supply them via a provider interface — interface file not yet fetched, see gaps).
- Relevance to AdVTT:
  - Jellyfin clients already consume typed segments via this endpoint; a tiny plugin (or a DB-writing sidecar) that emits `Commercial` segments from AdVTT JSON would light up existing skip buttons.

### S13. mpv wiki — User Scripts — https://github.com/mpv-player/mpv/wiki/User-Scripts
- Type: repo (wiki)
- Verified: fetched
- Key facts (chapter/skip-related scripts listed): chapterskip (po5) "Automatically skip chapters based on title."; mpv_sponsorblock (po5) "Script to skip sponsored segments of YouTube videos."; skiptosilence (detuur); skipsilence (ferreum, speeds up quiet parts); chapter-make-read (dyphire) "Automatically read and load external chapter files with CHP extension"; lilskippa (AN3223); skiptofade (bossen); SmartSkip (Eisa01) "Automatically or manually skip opening, intro, outro, and preview."
- Relevance to AdVTT:
  - Two independent title-based chapter skippers (chapterskip, SmartSkip) and an external-chapter-file loader (chapter-make-read, `.chp`) already exist → chapters are the lingua franca for skipping in mpv-land.

### S14. VLC wiki — Advanced Use of VLC — https://wiki.videolan.org/Documentation:Play_HowTo/Advanced_Use_of_VLC/
- Type: product (docs)
- Verified: fetched
- Key facts:
  - Page contains nothing on chapters or external chapter files; mentions Lua playlist scripts only. GAP: no VLC documentation found (yet) for loading chapters from an external file; VLC reads embedded chapters (MKV/MP4) only, as far as fetched sources show.
- Relevance to AdVTT:
  - For VLC the only zero-change path is embedding chapters into the container (MKV/MP4/M4B) or ID3 CHAP in MP3 (VLC's MP3 CHAP support is unverified — open question).

### S15. yt-dlp `sponsorblock.py` postprocessor — https://raw.githubusercontent.com/yt-dlp/yt-dlp/master/yt_dlp/postprocessor/sponsorblock.py
- Type: repo
- Verified: fetched
- Key facts:
  - CATEGORIES: `sponsor: 'Sponsor'`, `intro: 'Intermission/Intro Animation'`, `outro: 'Endcards/Credits'`, `selfpromo: 'Unpaid/Self Promotion'`, plus preview, filler, interaction, music_offtopic, hook. POI: `poi_highlight: 'Highlight'`. NON_SKIPPABLE = POI + `chapter: 'Chapter'`.
  - API `https://sponsor.ajay.app`, endpoint `/api/skipSegments/{video_hash[:4]}` (hash-prefix privacy scheme).
- Relevance to AdVTT:
  - SponsorBlock's category vocabulary (sponsor / selfpromo / interaction / …) maps cleanly onto AdVTT's ADVERTISEMENT / PROMOTION / SPONSORSHIP; adopting SponsorBlock's ids as an interop alias costs nothing and unlocks yt-dlp/mpv regexes.

### S16. mutagen ID3 frames — CHAP / CTOC — https://mutagen.readthedocs.io/en/latest/api/id3_frames.html
- Type: product (docs)
- Verified: fetched
- Key facts:
  - `mutagen.id3.CHAP(element_id='', start_time=0, end_time=0, start_offset=0xFFFFFFFF, end_offset=0xFFFFFFFF, sub_frames={})` — times in ms; offsets 0xFFFFFFFF = "not used".
  - `mutagen.id3.CTOC(element_id='', flags=0, child_element_ids=[], sub_frames={})`; sub_frames typically hold a TIT2 title.
- Relevance to AdVTT:
  - Pure-Python ID3 CHAP/CTOC writing exists in mutagen (already a yt-dlp dependency, S6) → AdVTT can write MP3 chapters without ffmpeg.

### S17. tone (sandreas) — https://github.com/sandreas/tone
- Type: repo
- Verified: fetched
- Key facts:
  - Chapter import formats: "ChptFmtNative" (mp4v2 `chapters.txt` style `HH:MM:SS.mmm Title`) and FFMetadata; `tone tag --meta-chapters-file chapters.txt`, `--auto-import=chapters`.
  - Targets m4b primarily; multi-container tagger (mp3/m4b/flac claimed on project page; format matrix not verified here).
- Relevance to AdVTT:
  - If AdVTT emits ffmetadata or mp4chaps-style `chapters.txt`, `tone` and `m4b-tool` users can tag files without AdVTT knowing about containers.

### S18. llm `pyproject.toml` — https://raw.githubusercontent.com/simonw/llm/main/pyproject.toml
- Type: repo
- Verified: fetched
- Key facts:
  - `requires-python = ">=3.10"`; setuptools backend; script `llm = "llm.cli:cli"`.
  - Deps include click, httpx2, openai, pluggy, sqlite-utils, pydantic>=2, PyYAML, python-ulid, puremagic.
  - Test extra: pytest, pytest-asyncio, pytest-recording, httpx2-pytest; dev tools ruff, mypy, black, syrupy (snapshot testing), cogapp; `llm-echo` test plugin.
- Relevance to AdVTT:
  - Plugin architecture = pluggy + entry points (hook doc not fetched yet). Providers as plugins (`llm-anthropic`, `llm-gemini`, `llm-mlx`) keeps the core dep-free — the same pattern would keep `advtt` core stdlib-first with `advtt-mlx`, `advtt-parakeet` as separate PyPI packages or extras.
  - Test stack uses pytest-recording (VCR) + syrupy snapshots — exemplary for LLM-dependent tools.

### S19. MDN — WebVTT API — https://developer.mozilla.org/en-US/docs/Web/API/WebVTT_API
- Type: spec/docs
- Verified: fetched
- Key facts:
  - `<track kind="chapters">` and `<track kind="metadata">` are both valid; "browsers do not necessarily support all kinds of text tracks"; `srclang` required when kind is set.
  - Compatibility tables exist for VTTCue/TextTrack/VTTRegion; page excerpt did not surface `cuechange` or chapter-kind rendering specifics.
- Relevance to AdVTT:
  - Browsers parse metadata tracks but render nothing and offer no skip; native chapter-kind UI is not standard either → a WebVTT track needs an app layer (Vidstack/video.js plugin) to do anything — confirms WebVTT is a *web-player* carrier, not a zero-change one.

### S20. yt-dlp README (raw) — SponsorBlock & post-processing options — https://raw.githubusercontent.com/yt-dlp/yt-dlp/master/README.md
- Type: repo (docs)
- Verified: fetched
- Key facts:
  - `--sponsorblock-mark CATS`: categories "sponsor, intro, outro, selfpromo, preview, filler, interaction, music_offtopic, hook, poi_highlight, chapter, all and default (=all)".
  - `--sponsorblock-remove CATS`: "'default' refers to 'all,-filler' and poi_highlight, chapter are not available".
  - `--sponsorblock-chapter-title TEMPLATE`: fields start_time, end_time, category, categories, name, category_names; "Defaults to '[SponsorBlock]: %(category_names)l'".
  - `--embed-chapters`: "Add chapter markers to the video file." `--remove-chapters REGEX`: "Remove chapters whose title matches the given regular expression." `--force-keyframes-at-cuts`: slow re-encode for cleaner cuts.
  - `--use-postprocessor` supports `ModifyChapters`; stage `after_move`.
- Relevance to AdVTT:
  - yt-dlp already provides a full "mark ads as chapters → optionally cut by title regex" pipeline; AdVTT's job is to produce chapters in a title convention regex-compatible with `[SponsorBlock]: Sponsor`.

### S21. po5/mpv_sponsorblock README — https://raw.githubusercontent.com/po5/mpv_sponsorblock/master/README.md
- Type: repo
- Verified: fetched (thin)
- Key facts:
  - Requires Python 3; skips sponsored segments when you "Play a YouTube video". README excerpt did not document local_database/hash options (GAP; the script's `sponsorblock.conf` is known to have `local_database`, `categories`, `skip_categories` options but that is unverified here).
- Relevance to AdVTT:
  - mpv_sponsorblock is YouTube-id keyed; not directly reusable for local podcast audio. chapterskip (S4) is the right mpv hook.

### S22. Intro Skipper (Jellyfin plugin) — https://github.com/intro-skipper/intro-skipper
- Type: repo
- Verified: fetched
- Key facts:
  - Requires "Jellyfin 10.11.11 (or newer)" and jellyfin-ffmpeg ≥ 7.1.1-7; detects "intro/credit sequences" via audio fingerprinting.
  - "As of Jellyfin 10.10, Intro Skipper does NOT modify the UI" — segments flow through the server Media Segments API; the web skip button is native, optional File Transformation plugin for extras.
  - Commercial detection / EDL export not visible in README excerpt (wiki pages "Detection types" referenced; GAP).
- Relevance to AdVTT:
  - Confirms the 10.10+ model: plugin → Media Segments → native client skip UI. AdVTT needs only a provider plugin (or direct segment POST if an API exists) emitting `Commercial` segments.

### S23. Podcast Namespace repo README — https://github.com/Podcastindex-org/podcast-namespace
- Type: spec (repo)
- Verified: fetched
- Key facts:
  - "To be adopted as an official part of the namespace, there must be consensus around a tag's usefulness and either commitment to adoption by at least 1 host and 1 app."
  - Tags are batched into Phases; currently "Phase 8" open. "It is ALWAYS ok to delay a tag to a future Phase if there is any concern about it."
  - `<podcast:chapters>` formalized in Phase 1; spec in docs/1.0.md.
- Relevance to AdVTT:
  - Adding an ad-flag field to JSON Chapters or a new tag needs ≥1 host + ≥1 app committed — PodcastFetch could be the "app", but a hosting company is needed; realistic path is a documented *extension key* in JSON chapters first, formal proposal later.

### S24. FFmpeg `doc/metadata.texi` (FFMETADATA1) — https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/doc/metadata.texi
- Type: spec/docs
- Verified: fetched
- Key facts:
  - File starts with `;FFMETADATA1`; `key=value` lines; `[CHAPTER]` sections with optional `TIMEBASE=num/den` (default nanoseconds), required `START=` and `END=` integers, then tags like `title=`.
  - Escape `=`, `;`, `#`, `\` and newline with backslash; whitespace is significant.
  - Round trip: `ffmpeg -i INPUT -f ffmetadata FILE` / `ffmpeg -i INPUT -i FILE -map_metadata 1 -codec copy OUTPUT`.
- Relevance to AdVTT:
  - A ~10-line writer gives an output that ffmpeg (embed into MP4/MKV/M4B/MP3 with `-codec copy`), mpv (`--chapters-file`, S1) and tone (S17) all consume today. This is the single highest-leverage sidecar format.

### S25. Jellyfin docs — Media Segments — https://jellyfin.org/docs/general/server/metadata/media-segments
- Type: product (docs)
- Verified: fetched
- Key facts:
  - Media segments "first introduced in 10.10". Types listed: Intro, Outro, Commercial, Preview, Recap (no "Unknown" mentioned on this page).
  - "Clients can then decide what they want to do with the provided information" — per-type client behaviour is not specified server-side.
  - Named provider plugin: "Chapter Segments Provider" which "creates media segments based on chapters and chapter-names."
  - No mention of manually supplying segments or of EDL import on this page.
- Relevance to AdVTT:
  - **Chapter-name → Commercial segment already exists in Jellyfin**: if AdVTT embeds chapters whose titles match the Chapter Segments Provider's configured regex, Jellyfin clients get native Commercial skip with zero new code. Need to fetch that plugin's default patterns.

### S26. Jellyfin `IMediaSegmentProvider.cs` — https://github.com/jellyfin/jellyfin/blob/master/MediaBrowser.Controller/MediaSegments/IMediaSegmentProvider.cs
- Type: repo
- Verified: fetched
- Key facts:
  - `string Name { get; }`; `Task<IReadOnlyList<MediaSegmentDto>> GetMediaSegments(MediaSegmentGenerationRequest request, CancellationToken ct)` — "Enumerates all Media Segments from an Media Item."; `ValueTask<bool> Supports(BaseItem item)`; plus `CleanupExtractedData`.
- Relevance to AdVTT:
  - A provider plugin is ~3 methods; it could read an AdVTT sidecar JSON next to the media file and return `Commercial` segments. Alternative zero-code path is S25's chapter-name provider.
  - GAP: `MediaSegmentType` enum file could not be fetched at two GitHub paths (404) — the type list is taken from S25 docs instead.

### S27. PyPI docs — Trusted Publishers — https://docs.pypi.org/trusted-publishers/
- Type: spec/docs
- Verified: fetched
- Key facts:
  - OIDC exchange; PyPI mints short-lived API tokens "valid for 15 minutes"; "eliminating the need to use manually generated API tokens". GitHub Actions named as identity provider on the landing page (other providers on subpages, not fetched).
- Relevance to AdVTT:
  - Confirms S11; use a "pending publisher" (documented on subpages) so the first release is also token-free.

### S28. Pocket Casts — Preselect Chapters — https://support.pocketcasts.com/knowledge-base/preselect-chapters/
- Type: product (docs)
- Verified: fetched
- Key facts:
  - "Preselect Chapters requires a Plus and Patron account." Per-episode choice of chapters to play/skip; selections sync across devices.
  - Platforms: iOS, Android, Web, Desktop, Apple Watch, CarPlay. Not supported: Wear OS and "custom user files" (uploaded files).
  - No rule-based / by-name automation documented.
- Relevance to AdVTT:
  - Pocket Casts can skip AdVTT chapters only (a) for feed-delivered episodes, (b) on paid tier, (c) by manual per-episode tap. Sideloaded files are excluded → a PodcastFetch-hosted private feed would be needed, not sideloading.

### S29. Apple Podcasts for Creators — Using chapters — https://podcasters.apple.com/support/5482-using-chapters-on-apple-podcasts
- Type: product (docs)
- Verified: fetched
- Key facts:
  - Three sources: timestamps in episode description; `<podcast:chapters>` in RSS; "chapters in the header of an MP4 file or by modifying the ID3 tags of an MP3 or AAC file."
  - Creator-provided chapters "always" take precedence over auto-generated ones; "Automatically created chapters are available starting with iOS 26.2."
  - Navigation only: tap chapter to jump; no skip/hide behaviour documented.
- Relevance to AdVTT:
  - Apple reads ID3 CHAP and JSON chapters, so AdVTT ad chapters would *appear*; listener skips manually by tapping the next chapter. No auto-skip. Apple's own auto-chapters (iOS 26.2) are a potential competitor/complement.

### S30. llm — Plugin hooks — https://llm.datasette.io/en/stable/plugins/plugin-hooks.html
- Type: product (docs)
- Verified: fetched
- Key facts:
  - Pluggy-based; plugins register via the `llm` entry-point group with `@hookimpl`. Hooks: `register_commands(cli)`, `register_models(register, model_aliases)`, `register_embedding_models`, `register_tools`, `register_template_loaders`, `register_fragment_loaders`. Installed with `llm install <pkg>` into the tool's own env.
- Relevance to AdVTT:
  - Blueprint for `advtt` plugins: `register_transcribers` (whisper-mlx, parakeet, Gladia, OpenAI) and `register_classifiers` (OpenAI, Claude CLI, Gemini, Ollama, MLX) as separate PyPI packages, keeping the core dependency-free and letting `uv tool install advtt --with advtt-mlx` work.

### S31. PEP 751 — pylock.toml — https://peps.python.org/pep-0751/
- Type: spec
- Verified: fetched
- Key facts:
  - Status Final, accepted 2025-03-31; file `pylock.toml` or `pylock.<name>.toml`; standard lock format replacing PEP 665; tools may be "lockers" or "installers"; uv, PDM, Poetry cited as implementers/inspiration.
- Relevance to AdVTT:
  - Ship a `uv.lock` for development and optionally export `pylock.toml` for reproducible CI; end-users installing via `uv tool`/pipx do not consume lockfiles.

### S32. Scientific Python SPEC 0 — https://scientific-python.org/specs/spec-0000/
- Type: spec
- Verified: fetched
- Key facts:
  - "Support for Python versions be dropped 3 years after their initial release." Drop dates: 3.10 → 2024-10-04; 3.11 → 2025-10-25; 3.12 → 2026-10-02; 3.13 → 2027-10-07.
- Relevance to AdVTT:
  - By SPEC 0, in Sept 2026 the floor is 3.12 (3.11 dropped Oct 2025). yt-dlp and llm still say ≥3.10 (S6, S18); whisperX ≥3.10,<3.14 (S48). Recommend `requires-python = ">=3.11"` (or 3.12 if MLX wheels force it) — 3.11 gives `tomllib` in stdlib.

### S33. RFC Editor — Independent Submission Stream — https://www.rfc-editor.org/about/independent/
- Type: spec/process
- Verified: fetched
- Key facts:
  - Documents "do not require, nor do they carry, community consensus, and they are not standards or best practices." Anyone may submit an Internet-Draft; ISE (Eliot Lear) reviews for interoperability/improvement/levity; IESG conflict review per RFC 5742; Informational/Experimental categories; many drafts never pass initial review; 12-step pipeline.
- Relevance to AdVTT:
  - A viable but slow path for an "Ad-marker chapter convention" Informational RFC; realistic only after the convention is in use. Not a launch-time activity.

### S34. SchemaStore CONTRIBUTING — https://github.com/SchemaStore/schemastore/blob/master/CONTRIBUTING.md
- Type: repo (process)
- Verified: fetched
- Key facts:
  - `catalog.json` entry needs `name`, `description`, `fileMatch`, `url`; schema may be self-hosted (url to your server) or in-repo `src/schemas/json/<name>.json`; in-repo requires `$id: "https://www.schemastore.org/<name>.json"` and `$schema` draft-07; positive tests `src/test/<name>/`, negative `src/negative_test/<name>/`; `node ./cli.js check --schema-name=`.
- Relevance to AdVTT:
  - Publish `advtt.schema.json` at a stable URL under the project domain with `$id`, then register a `fileMatch` such as `*.advtt.json` / `analysis.json` in SchemaStore for editor validation. Cheap, real adoption signal.

### S35. pytest-recording — https://github.com/kiwicom/pytest-recording
- Type: repo
- Verified: fetched
- Key facts:
  - `@pytest.mark.vcr` mirrors `VCR.use_cassettes`; `--record-mode` once/none/rewrite/all — `none` is the default (blocks unintended network); `@pytest.mark.block_network` / `--block-network`, `--allowed-hosts`; `vcr_config` fixture with `filter_headers` (e.g. authorization); cassettes in `cassettes/<module>/`.
- Relevance to AdVTT:
  - Exactly the CI pattern needed: default `none` + `block_network` means CI can never spend API money; `filter_headers=["authorization","x-api-key"]` keeps keys out of committed cassettes; `rewrite` mode re-records when prompts change. Used by `llm` itself (S18).

### S36. promptfoo — GitHub Action — https://www.promptfoo.dev/docs/integrations/github-action/
- Type: product (docs)
- Verified: fetched
- Key facts:
  - `promptfoo/promptfoo-action@v1` (Node ≥22.22); caches `~/.cache/promptfoo` to reuse LLM outputs and "save money and time"; posts a PR comment with a results link. Excerpt did not show a hard fail-on-threshold flag.
- Relevance to AdVTT:
  - An eval gate for AdVTT should be *its own metrics* (`content_loss_sec ≤ 5`, `ad_recall_sec ≥ 0.70`, `boundary_err_sec ≤ 3`) run on cassettes/recorded LLM outputs in PRs, with a manual-approval workflow that re-records live against the 4 fixtures. promptfoo's caching idea transfers; its harness is optional.

### S37. keyring (PyPI) — https://pypi.org/project/keyring/
- Type: product (docs)
- Verified: fetched
- Key facts:
  - Backends: macOS Keychain, Freedesktop Secret Service (needs `secretstorage`), KWallet (needs `dbus-python`), Windows Credential Locker. CLI `keyring set/get/delete`; `PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring` or `keyring --disable`; headless Linux needs gnome-keyring-daemon + D-Bus.
- Relevance to AdVTT:
  - Offer keyring as an *optional* backend (`advtt keys set --keyring`), default to llm-style keys.json (S2) to avoid headless/CI friction; yt-dlp exposes the same optional dependency as the `secretstorage` extra (S6).

### S38. aider — API keys docs — https://aider.chat/docs/config/api-keys.html
- Type: product (docs)
- Verified: fetched
- Key facts:
  - Keys via `--openai-api-key`/`--anthropic-api-key`, generic `--api-key provider=key`; env vars (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`); `.env` file ("a great place to store your API keys"); `.aider.conf.yml` with `api-key:` list. No keychain support.
- Relevance to AdVTT:
  - Second data point (with S2) that plaintext env/.env/config is the accepted norm for LLM CLIs; Keychain is a differentiator, not an expectation.

### S39. GitHub CLI — `gh auth login` — https://cli.github.com/manual/gh_auth_login
- Type: product (docs)
- Verified: fetched
- Key facts:
  - Token "stored securely in the system credential store"; falls back to "a plain text file" if none; `--insecure-storage` forces plaintext; `GH_TOKEN` env "most suitable for 'headless' use"; `--with-token` reads stdin.
- Relevance to AdVTT:
  - The gold-standard UX: secure store by default with automatic plaintext fallback and env override. If AdVTT adopts keyring (S37), copy this fallback ladder exactly.

### S40. Overcast — Podcaster info — https://overcast.fm/podcasterinfo
- Type: product (docs)
- Verified: fetched
- Key facts:
  - Displays "MP3 and M4A chapter markers with titles, images, and/or link URLs." No JSON chapters, no hidden chapters, no skip feature documented. Recommends Forecast (Marco Arment's MP3 chapter tool).
- Relevance to AdVTT:
  - Overcast users can *see* and tap past AdVTT ID3 chapters; no automation. Overcast does not read `<podcast:chapters>` per this page → ID3 CHAP embedding matters for Overcast reach.

### S41. Emby — Intro Skip article — https://emby.media/support/articles/Intro-Skip.html
- Type: product (docs)
- Verified: fetched
- Key facts:
  - Markers documented: IntroStart/IntroEnd only; requires "Emby Server 4.7 or later and an Emby Premiere subscription"; client options: ignore / "Automatically skip intros" / "Skip Intro button" prompt. No commercial marker or manual/API marker editing documented.
- Relevance to AdVTT:
  - Emby is a poor target: paid, intro-only, no documented external marker input. GAP — Emby has an undocumented `/Items/{id}/Chapters`/markers API per community lore; not verified.

### S42. Vidstack — Text Tracks API — https://www.vidstack.io/docs/player/api/text-tracks
- Type: product (docs)
- Verified: fetched
- Key facts:
  - Custom (non-native) TextTrack implementation; events `add-cue`, `remove-cue`, `cue-change`; hooks `useChapterTitle`, `useChapterOptions` (chapters shown in slider); no built-in skip-segment feature.
- Relevance to AdVTT:
  - Any web player needs ~20 lines of `cue-change` handling to skip; nothing does it out of the box. WebVTT metadata remains a *developer* integration, not a listener one.

### S43. Podlove Simple Chapters — https://podlove.org/simple-chapters/
- Type: spec
- Verified: fetched
- Key facts:
  - Namespace `http://podlove.org/simple-chapters`; spec version 1.1; `<psc:chapter start="NPT" title="…" href image>`; NPT examples `01:35:52`, `7:48`, `35:12.250`, `37`. Start and title mandatory; no end time; no hidden flag.
- Relevance to AdVTT:
  - Third chapter dialect read by Pocket Casts/AntennaPod; trivially emitted; carries titles only (no end, no toc) → ad marker must be encoded in the title.

### S44. whisperX `pyproject.toml` — https://raw.githubusercontent.com/m-bain/whisperX/main/pyproject.toml
- Type: repo
- Verified: fetched
- Key facts:
  - v3.8.7rc1; `requires-python >=3.10,<3.14`; setuptools; hard deps torch~=2.8.0, torchaudio~=2.8.0, faster-whisper>=1.2.0, pyannote-audio>=4.0.0.
- Relevance to AdVTT:
  - Counter-example: torch as a *hard* dependency forces an upper Python bound and multi-GB installs. AdVTT must keep torch/MLX out of the core and behind extras or plugins (S6, S30).

### S45. faster-whisper `setup.py` — https://raw.githubusercontent.com/SYSTRAN/faster-whisper/master/setup.py
- Type: repo
- Verified: fetched
- Key facts:
  - `python_requires=">=3.9"`; deps via requirements.txt (ctranslate2 etc.); extras `conversion`, `dev` (black 23, flake8 6, isort 5, pytest 7); classifiers list 3.9–3.11 only; still setup.py, not PEP 621.
- Relevance to AdVTT:
  - Legacy packaging still common in STT land; not a model to follow, but shows heavy STT libs lag on Python versions → AdVTT's STT extras should be version-pinned loosely and tested per-Python.

### S46. m4b-tool README — https://raw.githubusercontent.com/sandreas/m4b-tool/master/README.md
- Type: repo
- Verified: fetched
- Key facts:
  - `chapters.txt` format `<HH:MM:SS.mmm> <title>` from mp4v2 `mp4chaps`; merge options `--max-chapter-length`, `--use-filenames-as-chapters`, `--no-chapter-reindexing`; deps ffmpeg, mp4v2 (mp4chaps, mp4art), optional fdkaac; MP3 chapter writing not documented.
- Relevance to AdVTT:
  - Emitting `chapters.txt` (mp4chaps style) covers m4b-tool, mp4chaps and tone (S17) at once — a 3-line formatter.

### S47. Podcast Namespace — `<podcast:chapters>` tag doc — https://raw.githubusercontent.com/Podcastindex-org/podcast-namespace/main/docs/tags/chapters.md
- Type: spec
- Verified: fetched
- Key facts:
  - Attributes `url` (required), `type` (required; JSON preferred `application/json+chapters`). Rationale: chapters editable post-publication; displayable "by a wider range of playback tools, including web browsers"; images on demand. Nothing about ads or visibility.
- Relevance to AdVTT:
  - A PodcastFetch-generated private feed can point `<podcast:chapters>` at an AdVTT-generated JSON per episode without touching the audio — the cleanest delivery to Pocket Casts/Apple (S3, S29).

### S48. mpv Lua scripting manual — https://raw.githubusercontent.com/mpv-player/mpv/master/DOCS/man/lua.rst
- Type: product (docs)
- Verified: fetched
- Key facts:
  - `chapter-list` "returned as tables" via `mp.get_property_native()`; `mp.observe_property(name, type, fn)` for change callbacks; hooks via `mp.add_hook` with `defer()`/`cont()`; chapters can be replaced with `mp.set_property_native("chapter-list", …)`.
- Relevance to AdVTT:
  - Confirms the mechanism chapterskip (S4) and chapter-make-read (S13) rely on; an `advtt.lua` that loads a sidecar JSON and injects `chapter-list` entries is ~40 lines if the ffmetadata route is not used.

### S49. MDN — `<track>` element — https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/track
- Type: spec/docs
- Verified: fetched
- Key facts:
  - `kind=chapters`: "Chapter titles are intended to be used when the user is navigating the media resource." `kind=metadata`: "Tracks used by scripts. Not visible to the user."
- Relevance to AdVTT:
  - Normative confirmation that a metadata track does nothing without script — the preliminary design's carrier is inert for every non-custom player.

### S50. Comskip homepage — https://www.comskip.org/
- Type: product
- Verified: fetched (thin)
- Key facts:
  - Comskip "generates a file in various possible formats containing the location of the commercials" for editors (VideoReDo, Cuttermaran), CLI cutters (mpgtx, mencoder) and players (Zoomplayer, mplayer). EDL line format not on the homepage (manual at kaashoek.com/files/manual.htm referenced).
- Relevance to AdVTT:
  - Comskip is the incumbent "commercial marker producer" for TV; its EDL output is what Kodi/Plex/Channels consume. If AdVTT can emit the same EDL (`start end 3`), it inherits that ecosystem. Format detail still to verify (Kodi wiki 403 twice).

### Fetch failures (batch 3): kodi.wiki (403 again, both URL forms); MediaBrowser.Model/MediaSegments/MediaSegmentType.cs (404); w3.org CG final reports page (404); docs.brew.sh/Homebrew-and-Python (redirect stub → Language-Runtimes-and-Packages); podcastaddict.com/faq (403); getchannels.com commercial-detection (404); antennapod.org/documentation (index only, no chapter page found); videojs.org/guides/text-tracks (308 → legacy.videojs.org); mpv edl-mpv.rst (my parameter error, retrying).

### S51. mpv EDL format — `DOCS/edl-mpv.rst` — https://raw.githubusercontent.com/mpv-player/mpv/master/DOCS/edl-mpv.rst
- Type: spec/docs
- Verified: fetched
- Key facts:
  - Header `# mpv EDL v0`; entries `<filename>,<start s>,<length s>`; same file may be listed repeatedly with different offsets ("f1.mkv,10,20 … f1.mkv,40,10") forming a virtual timeline → implicit cutting; `title=` per segment sets chapter title ("OP.mkv,0,90,title=Show Opening"); `!no_chapters`, `!new_stream`, `!track_meta`, `!global_tags`, `!delay_open` headers.
- Relevance to AdVTT:
  - A "play without ads, losslessly, without re-encoding" artefact for mpv is a 5-line `.edl` file listing the non-ad ranges of the original audio. Zero consumer changes; user opens the .edl.

### S52. Jellyfin `MediaSegmentType.cs` — https://raw.githubusercontent.com/jellyfin/jellyfin/master/src/Jellyfin.Database/Jellyfin.Database.Implementations/Enums/MediaSegmentType.cs
- Type: repo
- Verified: fetched
- Key facts:
  - Enum: `Unknown = 0` ("Default media type or custom one."), `Commercial = 1`, `Preview = 2`, `Recap = 3`, `Outro = 4`, `Intro = 5`.
- Relevance to AdVTT:
  - `Commercial = 1` is the exact target type for AdVTT segments; `Unknown = 0` exists for custom types (e.g. "Sponsorship" could be Commercial with the label in provider metadata).

### S53. jellyfin-plugin-edl (endrl) — https://github.com/endrl/jellyfin-plugin-edl
- Type: repo
- Verified: fetched
- Key facts:
  - "Convert Media Segments (Intro, Outro,...) to .edl files"; user configures "the 'Edl Action' for different segment types in plugin settings"; needs "Jellyfin 10.10 unstable" minimum and writable media libraries. Direction is segments → EDL (export), per README excerpt; import not confirmed.
- Relevance to AdVTT:
  - Shows EDL is the bridge format between the Jellyfin segment model and Kodi/comskip land; AdVTT should emit Kodi-style EDL with action 3 (commercial break) directly.

### S54. Homebrew — Language Runtimes and Packages — https://docs.brew.sh/Language-Runtimes-and-Packages
- Type: product (docs)
- Verified: fetched (end-user page; formula-author page kept redirecting)
- Key facts:
  - "Use pipx for Python command-line applications that should each have an isolated environment"; venvs instead of modifying Homebrew's Python. Formula-author specifics (virtualenv_install_with_resources) not on this page — GAP, see S60/S61 for real formulae.
- Relevance to AdVTT:
  - Homebrew's own advice for end users is pipx; a `brew` formula is a nicety, not a requirement.

### S55. video.js — Text Tracks guide (legacy docs) — https://legacy.videojs.org/guides/text-tracks
- Type: product (docs)
- Verified: fetched
- Key facts:
  - `"metadata": Tracks that have data meant for JavaScript to parse and do something with.`; tracks with `mode="hidden"` emit `cuechange`; "For chapters, default is required if you want the chapters menu to show." No built-in segment skipping.
- Relevance to AdVTT:
  - video.js renders a chapters *menu* from a `kind=chapters` VTT — so a chapters-VTT gets visible UI in video.js with no plugin; a metadata-VTT needs code. Two VTT flavours, different reach.

### S56. Comskip manual (kaashoek.com) — http://www.kaashoek.com/files/manual.htm
- Type: product (docs)
- Verified: fetched
- Key facts:
  - Output options listed: ZoomPlayer cutlist/chapters, VideoRedo cutlist, CSV frame array, and a `.txt` cutpoint file re-readable as input. EDL specifics (`output_edl`, line format) live in the tuning guide/ini, not this page — GAP: EDL line format is still only known from memory (Kodi: `start<TAB>end<TAB>action`, seconds) and not verified by a fetched source in this track (Kodi wiki 403 ×3, web.archive.org blocked by the tool).
- Relevance to AdVTT:
  - Even the incumbent commercial detector treats EDL as one of many exports; AdVTT should do the same — one core JSON, many thin exporters.

### S57. W3C Community Final Specification Agreement — https://www.w3.org/community/about/agreements/final/
- Type: legal/process
- Verified: fetched
- Key facts:
  - Agreement provides copyright licence and royalty-free patent commitments on a CG's Final Specification; invoked when the group "calls for voluntary commitments" on a Report; separate from the Recommendation Track. (The `cg-final-reports` process page itself 404'd.)
- Relevance to AdVTT:
  - A W3C CG (e.g. a "Media Segment Metadata CG") could host a spec as a Final Report with IPR clarity but no standards status — heavier than needed at launch; a GitHub-hosted spec + JSON Schema is the right first step (S34).

### S58. PyPA tutorial — Packaging Python Projects — https://packaging.python.org/en/latest/tutorials/packaging-projects/
- Type: docs
- Verified: fetched
- Key facts:
  - "this tutorial uses Hatchling by default"; `[build-system] requires = ["hatchling >= 1.26"]; build-backend = "hatchling.build"`; example `requires-python = ">=3.9"`.
- Relevance to AdVTT:
  - Official PyPA tutorial defaults to Hatchling → choosing Hatchling is the mainstream, not a niche choice (contrast S8's caution which applies only to extension modules).

### S59. pyproject.toml specification ([project] table, ex-PEP 621) — https://packaging.python.org/en/latest/specifications/pyproject-toml/
- Type: spec
- Verified: fetched
- Key facts:
  - `optional-dependencies` keys "MUST be valid values for Provides-Extra"; self-referential extras `all = ["your-project-name[gui, cli]"]` are "supported by" pip, uv, poetry, hatch, pdm, Pipenv; `[project.scripts]` → console_scripts; `[project.entry-points]` custom groups (one level deep); `dynamic` list.
- Relevance to AdVTT:
  - Extras layout: `advtt[mlx]`, `advtt[parakeet]`, `advtt[openai]`, `advtt[gemini]`, `advtt[all] = ["advtt[mlx,parakeet,openai,gemini]"]`; plugin discovery via `[project.entry-points."advtt"]` mirroring llm (S30).

### S60. pipx docs — https://pipx.pypa.io/stable/
- Type: docs
- Verified: fetched
- Key facts:
  - Isolated venv per app, entry points on PATH; `pipx install 'package[extra]'`; `pipx inject` to add plugins into the app env; `pipx run` for ephemeral use.
- Relevance to AdVTT:
  - `pipx inject advtt advtt-mlx` is the pipx analogue of `uv tool install advtt --with advtt-mlx` — document both.

### S61. FFmpeg `libavformat/mp3enc.c` — https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/libavformat/mp3enc.c
- Type: repo
- Verified: fetched
- Key facts:
  - Muxer writes ID3v2 metadata via `ff_id3v2_write_metadata` and pictures via `ff_id3v2_write_apic`; **no CHAP/CTOC chapter writing** and no `nb_chapters` iteration found in the file.
- Relevance to AdVTT:
  - `ffmpeg -i in.mp3 -i chapters.ffmeta -map_metadata 1 -c copy out.mp3` will NOT produce ID3 chapters. MP3 chapter embedding must go through mutagen (S16) (or tone/eyeD3). This is a concrete pitfall for the ffmetadata route on MP3 — ffmetadata chapters work for MP4/M4B/MKV, not MP3.

### S62. FFmpeg `doc/muxers.texi` — https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/doc/muxers.texi
- Type: docs
- Verified: fetched (truncated by tool)
- Key facts:
  - Only confirmed: matroska muxer "implements the matroska and webm container specs". Sections on mp3/mov chapter & subtitle options were beyond the truncation point — GAP; movenc.c to be checked directly (next batch).
- Relevance to AdVTT: none beyond confirming the gap.

### S63. Audiobookshelf site/guides index — https://www.audiobookshelf.org/guides/ and /docs/
- Type: product
- Verified: fetched (thin)
- Key facts:
  - Feature list: "Audiobook chapter editor w/ chapter lookup"; "Embed metadata in audio files & merge multiple audio files to a single m4b". Detailed chapter-format docs not reachable at the URLs tried.
- Relevance to AdVTT:
  - Audiobookshelf's embed tooling uses tone/ffmpeg under the hood (per project reputation; unverified here) → emitting tone-compatible `chapters.txt`/ffmetadata (S17, S46) is sufficient.

### S64. SponsorBlock wiki "Types" — https://wiki.sponsor.ajay.app/w/Types
- Type: docs
- Verified: fetch blocked ("Access Denied")
- Key facts: none obtained; category list taken from yt-dlp source instead (S15, S20).

### Fetch plan (batch 5, logged before fetching)
repo.jellyfin.org/files/plugin/manifest.json (find Chapter Segments Provider) ; raw xbmc/xbmc EdlEdit.h and Edl.cpp (EDL action enum, file format, since wiki is blocked) ; docs.brew.sh/Formula-Cookbook (Python section) ; Homebrew/homebrew-core Formula/y/yt-dlp.rb and Formula/l/llm.rb ; raw FFmpeg movenc.c (mp4 chapters + subtitle codecs) ; videolan.org/vlc/releases/3.0.0.html (ID3 chapters) ; raw.githubusercontent.com/wiki/ajayyy/SponsorBlock/Types.md ; support.plex.tv intro/credits detection ; deepwiki: AntennaPod/AntennaPod, intro-skipper/intro-skipper, po5/mpv_sponsorblock, podverse/podverse-rn.

### S65. Kodi `xbmc/cores/EdlEdit.h` — https://raw.githubusercontent.com/xbmc/xbmc/master/xbmc/cores/EdlEdit.h
- Type: repo
- Verified: fetched
- Key facts:
  - `enum class Action { CUT = 0, MUTE = 1, SCENE = 2, COMM_BREAK = 3 };` (verbatim; no doc comments).
- Relevance to AdVTT:
  - Confirms from source (wiki was blocked) that Kodi's EDL action 3 is the commercial-break type — the value AdVTT should write.

### S66. Kodi `xbmc/cores/VideoPlayer/Edl.cpp` — https://raw.githubusercontent.com/xbmc/xbmc/master/xbmc/cores/VideoPlayer/Edl.cpp
- Type: repo
- Verified: fetched
- Key facts:
  - Edits are `start`/`end` as `std::chrono::milliseconds` + `action`; parsing delegated to `CEdlParserFactory::GetEdlParsersForItem`; validation message "Not an Action::CUT, Action::MUTE, or Action::COMM_BREAK!". Parser implementations (edl/txt/Vprj/xml) live in separate files (not fetched).
- Relevance to AdVTT:
  - Kodi's EDL pipeline is format-agnostic and pluggable; the `.edl` text parser is one of several — need one more fetch of the parser dir for exact separators/time formats.

### S67. Homebrew Formula Cookbook — https://docs.brew.sh/Formula-Cookbook
- Type: docs
- Verified: fetched
- Key facts:
  - Python patterns delegated to Language-Specific Formulae page; `resource` blocks for pinned deps ("Do not rely on packages installed in the contributor's global language environment"); homebrew-core requires Acceptable Formulae criteria, stable versions, passing audits; taps for anything else.
- Relevance to AdVTT:
  - A brand-new tool will not meet core notability at launch → ship a personal tap (`brew install <user>/advtt/advtt`) first; core later.

### S68. homebrew-core `yt-dlp.rb` — https://raw.githubusercontent.com/Homebrew/homebrew-core/HEAD/Formula/y/yt-dlp.rb
- Type: repo
- Verified: fetched
- Key facts:
  - `depends_on "python@3.14"`, certifi, deno; `virtualenv_install_with_resources`; 9 resource blocks (brotli, charset-normalizer, idna, mutagen, pycryptodomex, requests, urllib3, websockets, yt-dlp-ejs); installs bash/zsh/fish completions from libexec.
- Relevance to AdVTT:
  - Concrete template for a Python-CLI formula; note Homebrew builds against Python 3.14 today, so AdVTT must be tested on 3.14 (MLX/torch extras cannot be in the formula — they would be `pipx inject`/`uv --with` add-ons).

### S69. homebrew-core `llm.rb` — https://raw.githubusercontent.com/Homebrew/homebrew-core/HEAD/Formula/l/llm.rb
- Type: repo
- Verified: fetched
- Key facts:
  - `python@3.14`, rust (build, for jiter), certifi/pydantic as formulae; `virtualenv_install_with_resources`; ~26 resource blocks; `generate_completions_from_executable(bin/"llm", shell_parameter_format: :click)`.
- Relevance to AdVTT:
  - Every runtime dependency becomes a resource block to maintain → strong incentive to keep AdVTT's core deps near zero (stdlib + maybe click).

### S70. FFmpeg `libavformat/movenc.c` — https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/libavformat/movenc.c
- Type: repo
- Verified: fetched (partial; large file)
- Key facts:
  - `movflags disable_chpl` "Disable Nero chapter atom"; `mov_create_chapter_track` declared (QuickTime chapter text track) → MP4/M4B get both chapter representations from ffmetadata input.
  - `mov_write_subtitle_tag` shows DVD_SUBTITLE and TTML (`MOV_ISMV_TTML_TAG`/`MOV_MP4_TTML_TAG`); mov_text/WebVTT handling not visible in the truncated excerpt — GAP (mov_text is known to be the MP4 default text codec; unverified here).
- Relevance to AdVTT:
  - For MP4/M4A/M4B, `ffmpeg -i a.m4a -i ads.ffmeta -map_metadata 1 -c copy out.m4b` yields chapters readable by Apple Podcasts/Overcast/Pocket Casts iOS (S3, S29, S40). MP3 needs mutagen (S61).

### S71. VLC 3.0.0 release notes — https://www.videolan.org/vlc/releases/3.0.0.html
- Type: product
- Verified: fetched
- Key facts:
  - "Rewrite of webVTT subtitles support, including CSS style support". No chapter-related items (no MP3 ID3 chapter claim found).
- Relevance to AdVTT:
  - VLC plays WebVTT *subtitles*; whether VLC exposes ID3 CHAP as chapters remains unverified (GAP); VLC has no title-based chapter skip.

### S72. Blocked/unavailable in batch 5 (documented gaps)
- SponsorBlock wiki Types page: "Access Denied" at wiki.sponsor.ajay.app and GitHub wiki redirect → category definitions taken from yt-dlp source only (S15).
- support.plex.tv (skip-commercials, intro-and-credits-detection): 403 both; web.archive.org not fetchable by the tool. Plex commercial-marker mechanics therefore **unverified** in this track (community knowledge: DVR-only comskip "Remove Commercials"; Plex Pass; no third-party marker import).
- deepwiki MCP: all four questions (AntennaPod, Intro Skipper, mpv_sponsorblock, Podverse) returned "Authentication is not allowed on the public DeepWiki endpoint" → unusable in this session.
- getchannels.com docs: 404 on two guessed paths; podcastaddict.com/faq: 403; antennapod.org chapters page: not found. Podcast Addict / AntennaPod / Channels DVR chapter-skip behaviour is **unverified**.

### Fetch plan (batch 6, logged before fetching)
sfo1.mirror.jellyfin.org plugin manifest ; github.com/xbmc/xbmc tree for EDL parsers + raw AdvancedSettings.cpp (commbreak settings) ; docs.brew.sh/Language-Specific-Formulae ; raw po5/mpv_sponsorblock/sponsorblock.lua (options) ; raw dyphire/mpv-scripts chapter-make-read.lua (external chapter formats) ; github.com/AntennaPod/AntennaPod parser tree.

### S73. Jellyfin official plugin manifest — https://sfo1.mirror.jellyfin.org/files/plugin/manifest.json
- Type: repo/product
- Verified: fetched
- Key facts:
  - No plugin in the *official* repository mentions segments, chapters, intro, EDL or commercial. "Chapter Segments Provider" (named by Jellyfin docs, S25), Intro Skipper (S22) and the EDL plugin (S53) are all third-party repos with their own manifest URLs.
- Relevance to AdVTT:
  - A Jellyfin integration for AdVTT would also be a third-party plugin repo (add-a-repository-URL install), which is normal in that ecosystem. GAP: the Chapter Segments Provider's repo URL and default title regexes were not located in this session.

### S74. Kodi `xbmc/settings/AdvancedSettings.cpp` — https://raw.githubusercontent.com/xbmc/xbmc/master/xbmc/settings/AdvancedSettings.cpp
- Type: repo
- Verified: fetched
- Key facts:
  - `<edl>` advancedsettings: `mergeshortcommbreaks` (default false), `displaycommbreaknotifications` (true), `maxcommbreaklength` (250 s, "Just over 8 * 30 second commercial break"), `mincommbreaklength` (90 s), `maxcommbreakgap` (120 s), `maxstartgap` (300 s), `commbreakautowait` (0, off), `commbreakautowind` (0, off).
- Relevance to AdVTT:
  - Kodi auto-skips COMM_BREAK edits and shows an OSD notification by default; the merge heuristics assume TV-length breaks (90–250 s) — podcast host-reads (often 30–90 s) fall below `mincommbreaklength` only if `mergeshortcommbreaks` is enabled; by default each break is used as-is. `commbreakautowait/autowind` let users tune skip timing without any AdVTT change.

### S75. Homebrew — Language-Specific Formulae (Python applications) — https://docs.brew.sh/Language-Specific-Formulae
- Type: docs
- Verified: fetched
- Key facts:
  - "Include `Language::Python::Virtualenv` and use `virtualenv_install_with_resources`"; `depends_on "python@3.y"` at core's current minor; "All Python module dependencies and their recursive dependencies that are not provided by another formula must be declared as `resource`s"; `brew update-python-resources <formula>` (with `--print-only`); `pypi_packages` stanza for resolver hints; compiled bindings need special handling.
- Relevance to AdVTT:
  - Homebrew formula = every pure-Python dep pinned as resource; heavy binary extras (MLX, torch) are effectively impossible in a formula → brew installs the *core* only; STT/LLM extras via `uv tool install --with` or `pipx inject`.

### S76. po5 `sponsorblock.lua` options — https://raw.githubusercontent.com/po5/mpv_sponsorblock/master/sponsorblock.lua
- Type: repo
- Verified: fetched
- Key facts:
  - Defaults: `categories = "sponsor,intro,outro,interaction,selfpromo,filler"`, `skip_categories = "sponsor"`, `skip_once = true`, `local_database = false`, `local_pattern = ""` (regex to pull a YouTube id from local filenames, e.g. `-([%w-_]+)%.[mw][kpe][v4b]m?$`), `sha256_length = 4`, `make_chapters = true` (segments become mpv chapters), `server_address = https://sponsor.ajay.app`, `report_views`, `auto_upvote`, `server_fallback`.
- Relevance to AdVTT:
  - Design precedent: *skip only `sponsor` by default, mark everything else as chapters* — exactly AdVTT's conservative stance. Also shows mpv users are already used to segments appearing as chapters (`make_chapters`).

### S77. dyphire `chapter-make-read.lua` — https://raw.githubusercontent.com/dyphire/mpv-scripts/main/chapter-make-read.lua
- Type: repo
- Verified: fetched
- Key facts:
  - Autoloads an external chapter file with the media's basename + `chapter_file_ext = ".chp"` (optionally from a `chapters/` subdir or a global dir); reads CHP (`00:00:40.312 OP`), OGM (`CHAPTER01=… / CHAPTER01NAME=…`) and MediaInfo formats; writes CHP and OGM; `autoload = true`.
- Relevance to AdVTT:
  - A `.chp` sidecar (identical to mp4chaps `chapters.txt`, S46) is auto-picked-up by this popular mpv script; combined with chapterskip (S4) it gives auto-skip with two community scripts and no AdVTT-specific code.

### S78. AntennaPod media parser tree — https://github.com/AntennaPod/AntennaPod/tree/develop/parser/media/src/main/java/de/danoeh/antennapod/parser/media
- Type: repo
- Verified: fetched (directory listing)
- Key facts:
  - Subpackages `id3`, `m4a`, `vorbis` plus `MediaFormatDetector.java` → AntennaPod parses embedded chapters from ID3 (MP3), M4A and Vorbis/Opus comments. Podlove/JSON chapters from the feed are handled elsewhere (not verified). No auto-skip-by-title feature found (docs page 404; deepwiki unavailable).
- Relevance to AdVTT:
  - AntennaPod (the main FOSS Android client, supports local folders) will *display* AdVTT ID3 chapters from sideloaded MP3s; skipping is manual per chapter.

### Not found / not fetched (batch 6): github.com/xbmc/xbmc/tree/master/xbmc/cores/EdlParsers → 404; raw …/VideoPlayer/Edl/EdlParser.cpp → 404 (parser file location unknown; exact .edl text grammar remains unverified from source — Kodi wiki blocked).

### S79. AntennaPod `id3/ChapterReader.java` — https://raw.githubusercontent.com/AntennaPod/AntennaPod/develop/parser/media/src/main/java/de/danoeh/antennapod/parser/media/id3/ChapterReader.java
- Type: repo
- Verified: fetched
- Key facts:
  - Parses `CHAP` frames; reads sub-frames `TIT2` (title), `WXXX` (link, URL-decoded), `APIC` (image, embedded or URL). `CTOC` is never referenced — ignored.
- Relevance to AdVTT:
  - Write CHAP with TIT2 per ad chapter; CTOC is optional for AntennaPod (write it anyway for spec compliance). A `WXXX` link could carry a machine-readable AdVTT URL/URN (e.g. `advtt:ad;kind=midroll;conf=0.91`) without disturbing display.

### S80. Kodi `EdlParsers/` — `EdlFileParser.cpp` and siblings — https://github.com/xbmc/xbmc/tree/master/xbmc/cores/VideoPlayer/Edl/EdlParsers ; https://raw.githubusercontent.com/xbmc/xbmc/master/xbmc/cores/VideoPlayer/Edl/EdlParsers/EdlFileParser.cpp
- Type: repo
- Verified: fetched
- Key facts:
  - Parsers: BeyondTVParser, ComskipParser, EdlFileParser, MultipleEpisodeEdlParser, PvrEdlParser, VideoReDoParser.
  - `.edl` grammar: `sscanf("%512s %512s %i")` — whitespace-separated `start end action`; times as decimal seconds, `HH:MM:SS.sss`, or `#frames` (needs fps); lines starting `##` are comments; two fields ⇒ scene marker; actions `0→CUT, 1→MUTE, 2→SCENE, 3→COMM_BREAK`.
- Relevance to AdVTT:
  - Definitive from source: AdVTT's `.edl` exporter is `f"{start:.3f} {end:.3f} 3"` per ad block, same basename as the media. Kodi then auto-skips with an OSD notice (S74). Comskip `.txt` is also parsed natively by Kodi.

## Synthesis

**1. Packaging (Q1).** The 2026 mainstream for a Python media/LLM CLI is: PEP 621 `pyproject.toml` (S59), Hatchling (PyPA tutorial default S58; yt-dlp S6) or setuptools (llm S18), `requires-python >= 3.10` (yt-dlp, llm, whisperX; S6, S18, S44) although SPEC 0 says the 2026 floor is 3.12 (S32) and Homebrew builds against 3.14 (S68, S69). Heavy deps are kept out of the core: yt-dlp's core has zero hard deps with a `default` extra (S6); llm pushes every provider into pluggy plugins discovered through the `llm` entry-point group (S30, S18); whisperX is the cautionary counter-example with hard `torch~=2.8` and an upper bound `<3.14` (S44). Self-referential extras (`all = ["advtt[mlx,parakeet]"]`) are supported by pip/uv/hatch/pdm (S59). Distribution channels are `pip`, `pipx install 'pkg[extra]'`/`pipx inject` (S60), `uv tool install pkg --with extra-pkg`/`uvx --from 'pkg[extra]'` (S10), and Homebrew via `virtualenv_install_with_resources` with every pure-Python dep as a pinned resource (S75, S68, S69) — which makes MLX/torch extras impossible in a formula; core acceptance needs notability, so a personal tap comes first (S67). Release via Trusted Publishing (`id-token: write`, `environment: pypi`, 15-minute OIDC-minted tokens; S11, S27). PEP 751 `pylock.toml` is Final (2025-03-31) for reproducible dev/CI installs (S31).

**2. Key/config handling (Q2).** Norm = plaintext, layered: `llm` stores `keys.json` in the platform app-support dir with `--key` → keys.json → env-var precedence and `llm logs off` for privacy (S2); aider uses flags, env vars, `.env`, YAML — no keychain (S38). `gh` is the high bar: OS credential store by default with silent plaintext fallback, `--insecure-storage`, `GH_TOKEN` for headless (S39); Python `keyring` provides macOS Keychain/Secret Service/Windows backends with a `null` backend for CI (S37) and yt-dlp exposes it as an optional `secretstorage` extra (S6). No fetched tool documents a formal "nothing leaves your machine" mode; the closest analogues are pytest-recording's `block_network` (S35) and mpv_sponsorblock's opt-in `report_views/auto_upvote` telemetry flags (S76).

**3. Downstream consumers (Q3) — what works with zero changes.**
- *mpv*: `--chapters-file=<ffmetadata>` (S1, S24); `.chp` sidecar auto-loaded by chapter-make-read (S77); title-regex auto-skip via chapterskip/SmartSkip (S4, S13); `.edl` virtual timelines give lossless "no-ad" playback (S51). Lua can rewrite `chapter-list` (S48).
- *yt-dlp*: `--sponsorblock-mark/-remove`, `--remove-chapters REGEX`, `--embed-chapters`, ModifyChapters with concat-demuxer cutting; chapter title default `[SponsorBlock]: %(category_names)l` (S5, S20).
- *ffmpeg*: FFMETADATA1 `[CHAPTER]` round-trip with `-map_metadata 1 -c copy` (S24) works for MP4/M4B/MKV (Nero chpl + chapter track, S70) but **mp3enc writes no CHAP/CTOC** (S61) → MP3 chapters need mutagen (S16), tone (S17) or eyeD3 (not verified).
- *Kodi*: `.edl` sidecar `start end 3` → COMM_BREAK, auto-skip with OSD notification by default, tunables `commbreakautowait/autowind` (S65, S66, S74, S80). Also parses comskip `.txt`, VideoReDo, BeyondTV (S80).
- *Jellyfin ≥10.10*: Media Segments API with `Commercial = 1` (S52, S12, S25); segments come from `IMediaSegmentProvider` plugins (S26); third-party "Chapter Segments Provider" turns chapter names into segments (S25) and an EDL plugin bridges segments↔EDL (S53); all outside the official manifest (S73). Emby: intro-only, Premiere-gated, no external markers (S41). Plex: unverifiable (403; S72).
- *Podcast apps*: Apple Podcasts reads ID3/MP4 chapters and `<podcast:chapters>`; navigation only (S29). Overcast: MP3/M4A chapters only, no JSON (S40). Pocket Casts: MP3/Podcast Index/Podlove chapters; "Preselect Chapters" = manual per-episode deselect, paid tier, and **not for uploaded files** (S3, S28). AntennaPod parses ID3 CHAP/TIT2/WXXX/APIC, ignores CTOC, plus M4A and Vorbis (S78, S79). None offers auto-skip-by-title. Podcast Addict, Podverse, Castamatic, Fountain, Podcast Guru: not verified (S72).
- *Web players*: `kind=metadata` tracks are "used by scripts. Not visible to the user" (S49, S19); video.js shows a chapters menu for `kind=chapters` with `default` (S55); Vidstack exposes `cue-change` and chapter titles but no skip (S42). Nothing skips out of the box.
- *Audiobook tooling*: tone reads ffmetadata and mp4chaps `chapters.txt` (S17); m4b-tool uses mp4chaps `HH:MM:SS.mmm Title` (S46); Audiobookshelf has a chapter editor/embedder (S63).

**4. Chapter delivery and naming (Q4).** The only convention in the wild is yt-dlp's `[SponsorBlock]: Sponsor` (S5, S20); the podcast namespace has no ad field or convention (S9, S47), and `toc:false` *hides* a chapter — the opposite of what a skipper needs (S9). SponsorBlock's ids (sponsor, selfpromo, interaction, …) are the closest vocabulary standard (S15). Skipping today is: automatic in Kodi (EDL) and mpv (script), regex-driven in yt-dlp, manual-tap in every podcast app, per-episode deselect in Pocket Casts Plus.

**5. Spec publication (Q5).** Podcast Namespace needs consensus plus "at least 1 host and 1 app" committed, batched into Phases (currently Phase 8) (S23). SchemaStore accepts self-hosted schemas via a `catalog.json` entry with `fileMatch` (S34). W3C CG Final Specifications carry IPR commitments but are not standards (S57); the RFC Independent Stream accepts anyone's Informational draft but many never pass ISE review (S33).

**6. Testing (Q6).** VCR.py cassettes (S7); pytest-recording with default `record_mode=none`, `block_network`, `filter_headers` (S35) — used by `llm` together with syrupy snapshots (S18); promptfoo caches LLM outputs in CI and comments on PRs (S36).

**Contradictions / tensions.** Python floor: SPEC 0 says 3.12 (S32) vs. ecosystem tools still on ≥3.10 (S6, S18). Homebrew builds on 3.14 (S68) while whisperX caps at <3.14 (S44) — heavy STT extras and Homebrew are incompatible. `toc:false` (S9) vs. skippability. ffmetadata is universal for mpv/MP4/MKV but silently fails for MP3 chapters (S24 vs S61).

**Gaps.** Kodi wiki, Plex support, SponsorBlock wiki, Podcast Addict blocked (403); deepwiki unusable; Chapter Segments Provider repo not located; VLC ID3-chapter and MP3 `mov_text`/WebVTT-in-MP4 behaviour unverified; no podcast app verified to auto-skip by chapter title.

## Implications for AdVTT

1. **Make chapters the primary carrier; demote WebVTT to "web-player export".** Every consumer that skips today does so from chapters or EDL, never from a metadata track (S1, S4, S20, S49, S55, S74, S80). Emit from one internal model: (a) `ffmetadata` (mpv `--chapters-file`, ffmpeg embed into MP4/M4B/MKV; S24, S70), (b) `.edl` `start end 3` (Kodi auto-skip; S80, S74), (c) Podcast Index JSON chapters v1.2 with `toc:true` and an `advtt` extension object (S9, S47), (d) mp4chaps/`.chp` text (tone, m4b-tool, chapter-make-read; S17, S46, S77), (e) ID3 CHAP/CTOC via mutagen for MP3 because ffmpeg cannot (S16, S61, S79), (f) WebVTT `kind=chapters` (video.js menu; S55) and the existing `kind=metadata` track for the HTML prototype.
2. **Adopt a regex-friendly title convention aligned with SponsorBlock** — e.g. `[Ad] Acme (AdVTT 0.91)` by default and `--title-style sponsorblock` producing literally `[SponsorBlock]: Sponsor` so `yt-dlp --remove-chapters '\[SponsorBlock\]'`, chapterskip and Jellyfin's Chapter Segments Provider fire unchanged (S5, S20, S4, S25). Map vocabulary to SponsorBlock ids (`sponsor`, `selfpromo`, `interaction`) as an interop alias (S15). Never use `toc:false` for skippable ads (S9).
3. **Packaging stack:** Hatchling + PEP 621, `requires-python = ">=3.11"` (tomllib; below SPEC 0's 3.12 to keep parity with yt-dlp/llm), zero hard deps in core, extras `[openai] [gemini] [mlx] [parakeet] [keyring] [all]` with self-reference, provider plugins via `[project.entry-points."advtt"]` + pluggy (S6, S18, S30, S58, S59). Distribute via PyPI Trusted Publishing with `pypi`/`testpypi` environments (S11, S27), document `uv tool install advtt --with advtt-mlx` and `pipx inject` (S10, S60), ship `uv.lock`/`pylock.toml` for dev (S31), and a personal Homebrew tap for the core only (S67, S75). Test on 3.14 because Homebrew does (S68).
4. **Keys/config:** copy `llm` (`advtt keys set openai`, `keys.json` in platform dir, `--key`, env vars; S2) with an optional `keyring` backend following `gh`'s fallback ladder (S37, S39); add `--offline`/`local-only` that refuses any network provider and print a "nothing leaves your machine" audit line listing hosts contacted — no fetched tool does this; it is a differentiator (S35, S76).
5. **Jellyfin integration path:** ship an `IMediaSegmentProvider` plugin (3 methods) that reads the AdVTT sidecar and returns `Commercial = 1` segments; interim zero-code path is embedded chapters + Chapter Segments Provider regex (S25, S26, S52, S73). Skip Emby (S41); treat Plex as unknown (S72).
6. **Podcast-app reality check:** listeners get *visible* ad chapters (Apple, Overcast, AntennaPod) and manual skip; Pocket Casts Plus gets per-episode deselect but not for uploaded files (S28) — so PodcastFetch should re-serve a private RSS with `<podcast:chapters>` (S47) rather than sideload. Don't promise auto-skip in podcast apps; do promise it in mpv/Kodi/yt-dlp/Jellyfin.
7. **Lossless "ad-free copy" mode** = mpv `.edl` (S51) and ffmpeg concat-demuxer cut with optional `force_keyframes`, exactly as yt-dlp's ModifyChapters does (S5, S20) — off by default per the false-positive asymmetry.
8. **Spec publication:** publish `advtt.schema.json` with `$id` on the project domain and register `*.advtt.json` in SchemaStore (S34); document the JSON-chapters `advtt` extension; approach Podcast Namespace only once one host and one app commit (S23). Defer W3C/IETF (S57, S33).
9. **CI:** pytest-recording cassettes with `record_mode=none` + `block_network` + `filter_headers` (S35), syrupy snapshots of the validation ladder (S18), and a manually-triggered live re-record job that recomputes `content_loss_sec/ad_recall_sec/boundary_err_sec` on the four fixtures as the merge gate (S36 for caching idea).

## Open questions / things that need an experiment
- Does VLC surface ID3 CHAP chapters for MP3 and MP4 chapters from ffmetadata-embedded files? (S14, S71 gaps)
- Do Apple Podcasts / Overcast / AntennaPod display chapters from a *sideloaded* MP3 with mutagen-written CHAP (with and without CTOC)? (S29, S40, S79)
- Do JSON-chapters parsers (Pocket Casts, Apple, Podverse) tolerate an extra `advtt` object per chapter? Does `toc:false` really hide in each? (S9, S28)
- Chapter Segments Provider: repo, default regexes, whether title → `Commercial` is configurable. (S25, S73)
- Kodi with short (30–60 s) COMM_BREAK edits: default (`mergeshortcommbreaks=false`) should skip each; verify OSD/auto-wait UX. (S74)
- Does ffmpeg's mp4 muxer accept `-c:s webvtt` for WebVTT-in-MP4 or only `mov_text`? (S70 gap)
- Plex: is there any importer for third-party commercial markers on non-DVR items? (S72, unverifiable this session)
- Does Jellyfin expose a write endpoint for segments (for a sidecar script) or is a provider plugin the only path? (S12, S26)
- Homebrew formula on Python 3.14: do all AdVTT core deps import cleanly? (S68)

## Status
COMPLETE — 2026-09-02. 80 entries (S1–S80); all six research questions addressed; gaps listed in Synthesis and S72.
