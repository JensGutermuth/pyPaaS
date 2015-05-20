
## Definitions

A **repo** is a git repository. This is the canonical storage of source code and the only way to get code into pyPaaS or update it.

An **app** represents a group of processes running code from a specific branch from a repo. You deploy an apps when you use `git push` to update a repo. You can only push to branches with an associated app.

A **checkout** is used internally. It's a specific commit from a repo checked out into a working directory to be build and used to run an app. An app can have zero (not yet deployed, therefore not running), one (running) or two (deploy in progress) checkouts.
