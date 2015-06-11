
## Definitions

A **repo** is a git repository. This is the canonical storage of source code and the only way to get code into pyPaaS or update it.

A **repo** has **branches**. You deploy an apps when you use `git push` to update a repo. You can only push to configured branches.

**branches** have **runnesr**. A **runner** does something useful with code, like starting a process, configuring nginx to serve static files, starting a process to serve as a backend for nginx and so on.

A **checkout** is used internally. It's a specific commit from a repo checked out into a working directory to be build and used to run a branch. A branch can have zero (not yet deployed, therefore not running), one (running) or two (deploy in progress) checkouts.

A **domain** bundles configuration for a nginx virtual host. **runners** inheriting from `NginxBase` (or implementing the interface) provide the contents of a `location` block each in the resulting nginx config.

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
