## 911 CFS Analytics Backend / API Project

This is a Django app built for the CFS Analytics project.

### Development instructions

You need to have both [VirtualBox](https://www.virtualbox.org) and [Vagrant](https://www.vagrantup.com) installed to proceed. To provision the database we are using Ansible, which works nicely with vagrant. You will need this installed locally: you can do so via Homebrew by running `brew install ansible`.

1. Clone this repository
2. In terminal, `cd` into the repository's directory.
3. Enter `vagrant up`. The first time you do this it will take ~ 30 minutes to pull down the VirtualBox image and provision the machine.
4. Once 3 is complete, run `vagrant ssh` to enter the shell of the virtual machine.
5. At this point you should be able to connect to the database with pgAdmin or any other PostgreSQL client on port 5433 as the user _datascientist_ with a password of _1234thumbwar_.

You'll notice that the repository contains the Django app. Vagrant is set to configure the VM to share the repository directory with your host OS. That means that you can develop on your computer with your preferred dev tools. However, you'll need to run the Django app from within the VM. Vagrant makes this easy.

If you are not in the VM, follow the steps above.

If you are in the VM, then do the following...

The first time:

1. `cd /vagrant`
2. `sudo pip3 install -r requirements.txt`
3. `npm install` (installs front-end assets; do this when assets change)
4. `webpack` (compiles front-end assets; do this when assets change)

After that:

1. `cd /vagrant/cfs` (this is the shared directory with the repository)
2. `python3 manage.py runserver_plus 0.0.0.0:8000 --settings=cfs.settings.local` to use the development server or `gunicorn cfsbackend.wsgi -b 0.0.0.0:8000 --settings=cfsbackend.settings.prod` to use what we will use in production

To see whether Django is running properly, open a browser and point it to `localhost:8887` and you should see the app respond. The terminal where you have the VM open also should show that you hit the web app.

When you are done working for the day, use `ctrl-c` to quit Django in the VM. Type `exit` to exit the VM. Then type `vagrant halt` to gracefully shut down the VM. Check in your changes, push to the repository, etc...

The next day, when you're ready to work again, simply follow these instructions again.

### Front-end assets

Front-end assets are managed by [Webpack](https://webpack.github.io/). If working on
the front-end, you will need to run Webpack.

1. `cd /vagrant`
2. `webpack -w` (this puts Webpack into watch mode, so it will recompile on changes)

### One command to rule them all

In order to use the following, you will need to have another program installed that
knows how to run a Procfile. The easiest to use is "honcho," which you can install
on a Mac via `brew install honcho` or anywhere with Python via `pip install honcho`.

Once that's done, running `honcho -f Procfile.dev start` from the root directory
of the project should start both webpack and Django.
