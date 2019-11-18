# Predict Command Line Tool

Predict comes with a basic command line tool to manage the backend of the tool.
This tool has a few useful arguments that should be noted:

## `predict`

Simply calling predict doubles as a way to call `predict up` except just calling
predict you can't include any arguments.

## `predict up`

`predict up` starts the tool. It also takes arguments specifying whether the tool
is secured or not and for the configuration location.

Here are some examples:

```
$ predict up  # start Predict unsecured, the default
$ predict up --secured  # start Predict in secured mode, requiring users to log in
$ predict up -c ~/.predict/other_config.ini  # Start predict, specifying the location of an alternative configuration file
$ predict up --config ~/.predict/other_config.ini  # You can also do it like this
```

## `predict config`

`predict config` provides tools for creating new configuration files. You can
specify where you want predict to create configuration files using the location
argument.

Here are some examples:

```
$ predict config  # Create the default configuration file in the default location
$ predict config ~/.predict/other_config.ini  # Create a default configuration file in an alternate location
```
