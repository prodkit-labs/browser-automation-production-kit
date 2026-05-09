# Security Policy

## Supported Versions

This project is currently in `v0.x`. Security fixes are applied to the `main`
branch and the latest tagged release when practical.

## Reporting A Vulnerability

Please do not open public issues for vulnerabilities involving:

- credential exposure
- provider API keys
- artifact leakage
- unsafe fixture handling
- access-control bypass examples

Report security concerns through GitHub private vulnerability reporting if it is
available for this repository, or contact the maintainers through the public
ProdKit Labs profile.

## Scope

This project documents production workflow patterns for browser automation and
public-data workflows. It does not provide tools for credential harvesting,
account automation, social platform abuse, or bypassing protected access.

## Artifact Safety

Artifacts may contain HTML, screenshots, logs, URLs, business data, or provider
metadata. Treat artifact directories as sensitive, especially before uploading
them to public storage, issue comments, CI artifacts, or shared workspaces.

## Provider Credentials

Provider credentials must come from environment variables or a secret manager.
Do not commit API keys, proxy credentials, session tokens, cookies, or `.env`
files.

## External Provider Adapters

Run only provider adapters you trust. The external benchmark harness imports the
adapter module named by `--adapter`, and importing a Python module executes code
in your local environment before benchmark calls are made.
