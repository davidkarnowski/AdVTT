# Security

AdVTT reads local media and transcript files and, when asked, sends
transcript text to a model provider or audio to a speech-to-text service.
It never cuts or writes media, and `--offline` refuses every network
provider. Keys are read from the environment or a `.env` file and are never
written to any output.

## Reporting a vulnerability

Please report security issues privately through GitHub's "Report a
vulnerability" feature on this repository rather than in a public issue.
Include the version (`advtt --version`), the command line, and the input
shape that triggers the problem. Expect an acknowledgement within a week;
this is a single-maintainer project.

## Scope

In scope: anything that makes the tool read, send or write something it
should not (path handling, `.env` loading, provider adapters, the replay
store), or that lets a crafted transcript or caption file execute code.

Out of scope: the behaviour of third-party model or STT services, and
classification accuracy (report those as ordinary issues).
