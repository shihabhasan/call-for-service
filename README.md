## 911 CFS Analytics Backend / API Project

This is a Django app built for the CFS Analytics project.

### Development instructions

You need to have both [VirtualBox](https://www.virtualbox.org) and [Vagrant](https://www.vagrantup.com) installed to proceed.

1. Clone this repository
2. In terminal, `cd` into the repository's directory.
3. Enter `vagrant up`. The first time you do this it will take ~ 30 minutes to pull down the VirtualBox image.
4. Once 3 is complete, run `vagrant ssh` to enter the shell of the virtual machine.

You'll notice that the repository contains the Django app. Vagrant is set to configure the VM to share the repository directory with your host OS. That means that you can develop on your computer with your preferred dev tools. However, you'll need to run the Django app from within the VM. Vagrant makes this easy.

If you are not in the VM, follow the steps above.

If you are in the VM, then do the following...

1. `cd /vagrant/cfsbackend` (this is the shared directory with the repository)
2. `python manage.py runserver 0.0.0.0:8888`

If you look in the `Vagrantfile`, you'll see that the VM forwards port `8888` to the host OS's port `8888`. To see whether Django is running properly, open a browser and point it to `127.0.0.1:8888` and you should see the app respond. The terminal where you have the VM open also should show that you hit the web app.

When you are done working for the day, use `ctrl-c` to quit Django in the VM. Type `exit` to exit the VM. Then type `vagrant halt` to gracefully shut down the VM. Check in your changes, push to the repository, etc... 

The next day, when you're ready to work again, simply follow these instructions again. 

Note: from time to time, we may update the Vagrant box. If that happens, you'll see some yellow text in the terminal, warning that you're using an outdated version of the VM. To update the box, just enter `vagrant box update` and it will pull down the new VM image.

Also note that the provisioning script for Vagrant sets `python` to be an alias for `python3` within the VM.

### Notes for Windows 7 Users

* Running the VM in VirtualBox requires virtualization to be enabled in your BIOS. It may be disabled by default on RTI machines. If the VM fails to start after running `vagrant up`, try starting the VM directly via the VirtualBox GUI. An error with a message like "VT-x is disabled in the BIOS" indicates that you need to enter your machine's BIOS and enable virtualization. (The exact method for doing this will vary by motherboard.)

* The `vagrant ssh` command requires `ssh.exe` to be in your `PATH`. Because ssh is shipped with git, the easiest way to do this is to add `C:\programs\Git\bin` (or wherever you installed git) to your `PATH`. Another option is to use Putty with the connection information provided by the output of the `vagrant ssh` command. However, the private key file provided by Vagrant isn't compatible with Putty. You'll first need to open the key in puttygen and convert it to a `.ppk` file, then you can tell Putty to use that file for authenticating.

    