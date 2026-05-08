# Cost Control

Browser automation costs usually grow through retries, browser minutes, provider calls, artifact storage, and region routing.

Control points:

- set retry budgets per job
- record bytes and artifact volume
- separate fixture, local, and provider-backed runs
- estimate cost per 1k pages
- stop jobs when block rate crosses a threshold
- compare providers with raw benchmark data
