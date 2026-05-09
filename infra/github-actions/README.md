# GitHub Actions

The benchmark workflow validates:

- linting with Ruff
- unit tests with pytest on Python 3.11, 3.12, and 3.13
- fixture-only jobs
- Crawlee fixture jobs
- Playwright browser jobs
- local and mock provider benchmarks
- generated provider and cost reports
- Docker worker image build
- uploaded benchmark artifacts from local/mock runs

External provider benchmarks are not part of default CI. They should run only
with explicit adapter paths, trusted adapter code, reviewed repository secrets,
and a documented benchmark scope.

Do not add provider credentials to public workflow files. Use repository secrets
only after provider-backed benchmarks are reviewed.
