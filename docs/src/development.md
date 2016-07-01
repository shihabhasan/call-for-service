# Setting up for local development

We have provided a `Vagrantfile` to make setup easy by using 
[Vagrant](https://www.vagrantup.com). To use Vagrant, you will need the 
following installed locally:

* [Vagrant](https://www.vagrantup.com)
* [VirtualBox](https://www.virtualbox.org)
* [Ansible](https://docs.ansible.com/ansible/index.html) (On OS X, you can 
install this via Homebrew by running `brew install ansible`.)

To get started:

1. Clone this repository
2. In your terminal, `cd` into the repository's directory.
3. Enter `vagrant up`. The first time you do this it will take up to 15 minutes 
to pull down the VirtualBox image and provision the machine.
4. Once 3 is complete, run `vagrant ssh` to enter the shell of the virtual machine.

You'll notice that the repository contains the Django app. Vagrant is set to 
configure the VM to share the repository directory with your host OS. That means 
that you can develop on your computer with your preferred dev tools. However, 
you'll need to run the Django app from within the VM. Vagrant makes this easy.

The first time:

1. `cd /vagrant`
2. `sudo pip3 install -r requirements.txt` (installs all Python requirements; do this again if requirements change)
3. `python3 ./cfs/manage.py migrate --settings=cfs.settings.local` (migrates the database)
4. `npm install` (installs front-end requirements; do this again if requirements change)
5. `webpack` (compiles front-end assets; do this when assets change)

After that:

1. `python3 ./cfs/manage.py runserver_plus 0.0.0.0:8000 --settings=cfs.settings.local`.

To see whether Django is running properly, open a browser and point it to 
`localhost:8000` and you should see the app respond. The terminal where you 
have the VM open also should show that you hit the web app.

When you are done working for the day, use `ctrl-c` to quit Django in the VM. 
Type `exit` to exit the VM. Then type `vagrant halt` to gracefully shut down the 
VM.

The next day, when you're ready to work again, simply follow these instructions again.

## Front-end assets

Front-end assets are managed by [Webpack](https://webpack.github.io/). If working on
the front-end, you will need to run Webpack.

1. `cd /vagrant`
2. `webpack -w` (this puts Webpack into watch mode, so it will recompile on changes)

## One command to rule them all

In order to use the following, you will need to have another program installed that
knows how to run a Procfile. We are using "honcho," which is installed on the
Vagrant box.

Running `honcho -f Procfile.dev start` from the root directory of the project 
should start both Webpack and Django.