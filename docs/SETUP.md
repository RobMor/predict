# Basic Setup

This section is for those simply looking to use Predict on their personal
machine. These steps will be phrased rather generally so as to apply to as many
platforms as possible.

The first thing to do is obtain the source code. You can do this via any
subversion client. The URL is [https://vis.cs.umd.edu/svn/projects/predict/prod].
You can check out this code and move on to the next step, but make sure you put
it somewhere you can find it again.

After you obtain the code, you'll need to install it. Predict uses Python 3 for
both installation and during run time. You will need to install Python 3.5 or
above to install and use Predict. 

After you have Python installed, you will need to access your command line. 
Using your command line, navigate to the code you downloaded earlier. From
within the `prod` directory you should see a file called `setup.py`. This means
that you are in the correct location to run the next command.

Now we will install Predict using Python. To do this, use the following command:

```
python3 -m pip install .
```

This installs predict on your system and you should now have access to the
`predict` command. You can test that you have successfully installed Predict by
running the following command:

```
predict -h
```

You should see something that looks like this:

```
usage: predict [-h] <command> ...

Predict: CVE Labeling Tool

optional arguments:
  -h, --help  show this help message and exit

Available commands:
  <command>
    up        Start the server
    config    Create the default configuration
```

If you see this it means that predict is properly installed and you are ready to
configure it. We can use the `predict` command to generate a default
configuration file for us like so:

```
predict config
```

This places a configuration file in our home directory under a folder named
.predict (On Linux this is `~/.predict/config.ini`, On Windows it's
`C:\Users\<your username>\.predict\config.ini`). If you want to keep your
configuration file somewhere else you can set the environment variable
`PREDICT_CONFIG` to another location. Otherwise you can always specify the
location of a configuration file when running Predict as we'll see later.

At this point you should take a moment to configure Predict for your needs. The
default configuration is compatible with most single user use cases for Predict
but do checkout CONFIGURATION.md for more information. 

Now we can actually run Predict. This is as simple as running the following
command on the command line:

```
predict
```

Now you should be able to navigate to `localhost:5000` in your browser and see 
Predict running!

# Server Setup

This section is for those trying to set Predict up as general use server, rather
than for personal use.

This guide will walk you through setting up Predict on a Debian machine using
Apache from scratch. It assumes that you have root access to the machine you are
trying to install Predict on.

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
