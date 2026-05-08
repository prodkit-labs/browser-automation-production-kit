# Deployment

The first production path is a self-hosted worker with scheduled runs, artifact storage, and raw benchmark output.

Minimum deployment checklist:

- environment variables configured from `.env.example`
- artifact directory or object storage configured
- scheduled job runner selected
- logs retained
- failed runs preserve request metadata and HTML
- provider credentials scoped to the job

Managed providers can be added when local execution no longer meets reliability, region, or maintenance needs.
