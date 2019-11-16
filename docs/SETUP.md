# Basic Setup Goes here

# Server Setup

This section is for those trying to set Predict up as general use server, rather
than for personal use.

This guide assumes that you are on a Debian machine and are willing to use the
Apache Web Server. It also assumes that you have root access to the machine you
are trying to install Predict on.

It is recommended that you create a dedicated user for the app. This user will
also need root access to your machine. You can create a user on Debian with

```
$ sudo adduser EnterUsernameHere
```

and grant them sudo priveleges with

```
$ sudo usermod -aG sudo EnterUsernameHere
```

Next we will switch over to that user and navigate to their home directory:

```
$ sudo su EnterUsernameHere
$ cd
```

Now we can begin the actuall installation of Predict. First you need to obtain a
version of this repository if you haven't already. We'll need subversion in
order to pull this repository. If you don't have subversion installed you can
install it on Debian with 

```
$ sudo apt-get install subversion
```

Now you can pull the code with

```
$ svn checkout https://vis.cs.umd.edu/svn/projects/predict/prod
```

This will create a directory called `prod` where all the code for Predict is
stored.

Predict uses Python 3 and needs `pip` (A package manager for Python) in order to
be installed. Most Debian installations come with Python 3 but we will need to
install `pip`:

```
$ sudo apt-get install python3-pip
```

Now we are going to install the `predict` command line tool to assist us. First
we go into the `prod` directory from earlier and install Predict using `pip`:

```
$ cd prod
$ sudo python3 -m pip install .
```

Now you should be able to run `predict` to see the command line tools help
message:

```
$ predict -h
usage: predict [-h] <command> ...

Predict: CVE Labeling Tool

optional arguments:
  -h, --help  show this help message and exit

Available commands:
  <command>
    up        Start the server
    config    Create the default configuration
```

We are going to make use of this tool to create the default configuration file.
We do this using the `predict config` subcommand which creates the default
configuration file. This configuration file defaults to being placed in your 
home directory in `~/.predict/config.ini`. You can change this default location
by setting the `PREDICT_CONFIG` environment variable or by specifying a
different location using the following command (NOTE setting the location using
the command line is not permanent and you'll need to set this environment
variable for predict to be able to find this file later).

We can create the configuration in the default location with:

```
$ predict config
```

The rest of this tutorial assumes that you are using the default config 
location. The configuration file should now be in the location you specified.
You can edit this configuration file however you see fit. Now might be
a good time to check out CONFIGURATION.md

Now we are going to install the necessary packages for apache. On Debian that
would be `apache2`:

```
$ sudo apt-get install apache2
```

Next we need to install the mod_wsgi package to allow apache to communicate with
the framework predict is running on. On Debian that package is 
`libapache2-mod-wsgi`:

```
$ sudo apt-get install libapache2-mod-wsgi-py3
```

Now we need to configure mod_wsgi. The first thing we need to do is
move the .wsgi file within the `prod` directory into some place Apache can find
it. This is generally somewhere underneath `/var/www`. We will create directory
under `/var/www` called `predict` where we will then copy the .wsgi file:

```
$ sudo mkdir /var/www/predict
$ sudo cp ~/prod/predict.wsgi /var/www/predict/
```

Next we will need to configure Apache itself to talk to mod_wsgi. To do this
we will have to edit the configuration file provided with Predict. Open
`predict.conf` with a text editor and make edits to the areas surrounded with 
exclamation marks (!). Make sure to remove the exclamation marks when finished.

Here's an example finished configuration file:

```
<VirtualHost *>
    ServerName viceroy.cs.umd.edu

    WSGIDaemonProcess predict user=predict group=predict threads=5
    WSGIScriptAlias / /var/www/predict/predict.wsgi

    <Directory /var/www/predict>
        WSGIProcessGroup predict
        WSGIApplicationGroup %{GLOBAL}
        Order deny,allow
        Allow from all
    </Directory>
</VirtualHost>
```

Now we simply move this configuration file into somewhere Apache can find it:

```
$ sudo cp ~/prod/predict.conf /etc/apache2/sites-available
```

Next we disable the default configuration and enable this configuration with
`a2dissite` and `a2ensite`:

```
$ sudo a2dissite 000-default
$ sudo a2ensite predict
```

Now all we need to do is restart Apache so it registers our configuration. On
Debian we can do that with:

```
$ sudo systemctl reload apache2
```

Now predict should be running and you should be able to navigate to it using
your browser!
