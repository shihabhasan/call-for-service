## 911 CFS Analytics Backend / API Project

This is a Django app built for the CFS Analytics project.

### Development instructions

You need to have both [VirtualBox](https://www.virtualbox.org) and [Vagrant](https://www.vagrantup.com) installed to proceed. To provison the database we are using Chef, which works nicely with vagrant when you install vagrant's omnibus plugin.  Once you have vagrant installed, this plugin can be installed by running: _vagrant plugin install vagrant-omnibus_ from the command line.  All this does is to install Chef on the VM.

1. Clone this repository
2. In terminal, `cd` into the repository's directory.
3. Go [here](https://atlas.hashicorp.com) (Vagrant cloud), register a user account, and tell Clay what it is. Wait for him to add you to the rtidatascience group.
4. Enter `vagrant up cfs_backend`. The first time you do this it will take ~ 30 minutes to pull down the VirtualBox image.  
5. Once 4 is complete, run `vagrant ssh cfs_backend` to enter the shell of the virtual machine.
6. To start up the database, run `vagrant up cfs_database`.  This will use Chef to provision a postgreSQL database and forward host traffic on 5433 to the standard PostgreSQL port.
7. At this point you should be able to connect to this database pgAdmin or any other PostgreSQL client on port 5433 using as _postgres_ with a password of _1234thumbwar_

You'll notice that the repository contains the Django app. Vagrant is set to configure the VM to share the repository directory with your host OS. That means that you can develop on your computer with your preferred dev tools. However, you'll need to run the Django app from within the VM. Vagrant makes this easy.

If you are not in the VM, follow the steps above.

If you are in the VM, then do the following...

The first time:

1. `cd /vagrant`
2. `sudo pip3 install -r requirements.txt`
3. `npm install`

After that:

1. `cd /vagrant/cfsbackend` (this is the shared directory with the repository)
2. `python3 manage.py runserver 0.0.0.0:8888`

If you look in the `Vagrantfile`, you'll see that the VM forwards port `8888` to the host OS's port `8887`. To see whether Django is running properly, open a browser and point it to `127.0.0.1:8887` and you should see the app respond. The terminal where you have the VM open also should show that you hit the web app.

When you are done working for the day, use `ctrl-c` to quit Django in the VM. Type `exit` to exit the VM. Then type `vagrant halt` to gracefully shut down the VM. Check in your changes, push to the repository, etc... 

The next day, when you're ready to work again, simply follow these instructions again. 

Note: from time to time, we may update the Vagrant box. If that happens, you'll see some yellow text in the terminal, warning that you're using an outdated version of the VM. To update the box, just enter `vagrant box update` and it will pull down the new VM image.

Also note that the provisioning script for Vagrant sets `python` to be an alias for `python3` within the VM.

### Front-end assets

The front-end is managed by [webpack](http://webpack.github.io/). You have to run this in order to make the dashboard work.

1. `cd /vagrant`
2. `./node_modules/.bin/webpack`

If you expect to be changing the CSS and JS, you may want to run `webpack -w` to watch for changes.

### Notes for Windows 7 Users

* Running the VM in VirtualBox requires virtualization to be enabled in your BIOS. It may be disabled by default on RTI machines. If the VM fails to start after running `vagrant up`, try starting the VM directly via the VirtualBox GUI. An error with a message like "VT-x is disabled in the BIOS" indicates that you need to enter your machine's BIOS and enable virtualization. (The exact method for doing this will vary by motherboard.)

* The `vagrant ssh` command requires `ssh.exe` to be in your `PATH`. Because ssh is shipped with git, the easiest way to do this is to add `C:\programs\Git\bin` (or wherever you installed git) to your `PATH`. Another option is to use Putty with the connection information provided by the output of the `vagrant ssh` command. However, the private key file provided by Vagrant isn't compatible with Putty. You'll first need to open the key in puttygen and convert it to a `.ppk` file, then you can tell Putty to use that file for authenticating.

### Generating a database schema diagram

In `/working_files/datadocs` is a shell script called `update_schema_diagram.sh`. Edit/use it to create a diagram of the database. However, you will have to install [schemacrawler](http://sualeh.github.io/SchemaCrawler/) first.
