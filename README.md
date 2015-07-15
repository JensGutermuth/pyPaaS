[![Code Issues](http://www.quantifiedcode.com/api/v1/project/f78ad9da5ea04bbdbe5cf527efe2331e/badge.svg)](http://www.quantifiedcode.com/app/project/f78ad9da5ea04bbdbe5cf527efe2331e)

## Installation

pyPaaS has a few dependencies we need to install first:

```
root@host$ apt-get install python-virtualenv python3.4-dev libyaml-dev daemontools daemontools-run
```


pyPaaS needs a normal user to work. This will be the user you use to `git push` to. Let's create one:

```
root@host:~$ adduser --disabled-password deploy
Adding user `deploy' ...
Adding new group `deploy' (1002) ...
Adding new user `deploy' (1002) with group `deploy' ...
The home directory `/home/deploy' already exists.  Not copying from `/etc/skel'.
Changing the user information for deploy
Enter the new value, or press ENTER for the default
    Full Name []: pyPaaS
    Room Number []:
    Work Phone []:
    Home Phone []:
    Other []:
Is the information correct? [Y/n] Y
```

We can now grab the code and configure a virtualenv!

```
root@host:~$ su deploy
deploy@host:/root$ cd ~
deploy@host:~$ # For production usage:
deploy@host:~$ git clone git@code.fintura.work:fintura-it/pyPaaS.git
deploy@host:~$ # For development:
deploy@host:~$ ln -s <WHEREEVER YOUR CHECKOUT IS> pyPaaS
deploy@host:~$ virtualenv --python=python3.4 venv
Running virtualenv with interpreter /usr/bin/python3.4
Using base prefix '/usr'
New python executable in venv/bin/python3.4
Also creating executable in venv/bin/python
Installing setuptools, pip...done.
deploy@host:~$ venv/bin/pip install -e pyPaaS/
```

To run stuff we need to configure daemontools

```
root@host:~$ mkdir /etc/service/pyPaaS
root@host:~$ cp ~deploy/pyPaaS/daemontools-run /etc/service/pyPaaS/run.new
root@host:~$ chmod 755 /etc/service/pyPaaS/run.new
root@host:~$ mv /etc/service/pyPaaS/run.new /etc/service/pyPaaS/run
```

That's it :).

## Quickstart

Without configuration pyPaas will do nothing. You can put your configuration either in `~deploy/config` or `/etc/pypaas`. We'll use the first option here.

First off we need to create a main configuration file named `pypaas.yml`. pyPaas uses the first directory of the ones listed above with a `pypaas.yml` file as it's configuration directory. Like all pyPaaS configuration it uses YAML syntax.

```yaml
# ~deploy/config/pypaas.yml
---
ports: # required. Port range to use for nginx upstreams (and possibly more in the future)
  min: 61500
  max: 61800
```

Let's add a repository next! Configurations for repositories goes into the `repo` subdirectory. Each file describes a repository with the same name minus the `.yml`.

```
# ~deploy/config/repo/node-js-sample.yml
---
branches: # required
    master: # you can have multiple branches per repo. Just add another key
        runners: # required. Each branch is "run" somehow. You can have as many runners as you want. The names are used to refer to them in the domain config (see further down).
            node:
                type: NginxBackend # required. NginxBackend is a upstream for nginx
                cmd: npm start # required
                process_count: 4 # optional, defaults to 1
            static:
                type: NginxStatic # let's serve static files with nginx
                subdirectory: public # optional, defaults to the root of the checkout
            background_worker:
                type: SimpleProcess # just start processes
                cmd: node # required. Not very meaningful in this case.
        env: # optional. Environment variables are used with custom_cmds, running processes in runners, during build, ...
            NODE_ENV: production
            # PORT is set by NginxBackend automatically to one in the range defined in the main configuration and differs per instance
        hooks: # optional. Specify any additional commands to run during the deploy process.
            # Currently implemented: before_build, after_build, maintenance
            # Values can a strings or a list of strings for multiple commands executed serially.
            before_build: 'echo "Nothing is build - just a fresh checkout is there. Verify signed tags?"'  # can be a string
            after_build: 'echo "All builders are done. Build assets maybe?"'
            maintenance:
            - 'echo "do backup"'
            - 'echo "run migrations"'
        custom_cmds: # optional. Specify commands to run via "ssh deploy@host custom_cmds <repo> <branch> <cmd>"
            npm_list: npm list
```

With that done, let's wire the repository up to a domain. You can have one repository serve any number of domains and vice versa. Like with the repositories the filename is the domain name.

```
# ~deploy/config/domains/node-js-sample.example.com.yml
---
locations: # required. Every key corresponds so a location block in the nginx config.
    "/":
        upstream: # required.
            repo: node-js-sample # required.
            branch: master # required.
            runner: node # required.
    "/public":
        upstream:
            repo: node-js-sample
            branch: master
            runner: static
ssl: false # optional, defaults to false.
# Expects if true:
# - a certificate at /etc/ssl/private/httpd/{domain}/{domain}.crt
# - the private key at /etc/ssl/private/httpd/{domain}/{domain}.key
# - a file with trusted CAs to verify OCSP responses at /etc/ssl/private/httpd/{domain}/trusted_chain.crt
```

Now all that's left to do before your first deploy is adding ssh public keys. pyPaaS expects them in `~deploy/.ssh/authorized_keys.d/`. The `~deploy/.ssh/authorized_keys` is generated by running `~deploy/venv/bin/pypaas rebuild_authorized_keys` as `deploy`.

Let's deploy the node.js sample app:

```
you@your-machine:~$ git clone https://github.com/heroku/node-js-sample
you@your-machine:~$ cd node-js-sample
you@your-machine:~$ git push deploy@host:node-js-sample
```

Now watch it build and start this application and that's it :).

## Terms used

A **repo** is a git repository. This is the canonical storage of source code and the only way to get code into pyPaaS or update it.

A **repo** has **branches**. You deploy an apps when you use `git push` to update a repo. You can only push to configured branches.

**branches** have **runners**. A **runner** does something useful with code, like starting a process, configuring nginx to serve static files, starting a process to serve as a backend for nginx and so on.

A **checkout** is used internally. It's a specific commit from a repo checked out into a working directory to be build and used to run a branch. A branch can have zero (not yet deployed, therefore not running), one (running) or two (deploy in progress) checkouts.

A **domain** bundles configuration for a nginx virtual host. **runners** inheriting from `NginxBase` (or implementing the interface) provide the contents of a `location` block each in the resulting nginx config.
