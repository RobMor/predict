## `predict config`

`predict config` provides tools for creating new configuration files. You can
specify where you want predict to create configuration files using the location
argument.

Here are some examples:

```
$ predict config  # Create the default configuration file in the default location
$ predict config ~/.predict/other_config.ini  # Create a default configuration file in an alternate location

```

## Adding users to the whitelist

Once the confinguration file has been created with the above command, specifying which users
are allowed to use the whitelist is easy. Simply naviagte to the config.ini file and locate the section labeled 
`[WHITELIST]` and set the `WHITELIST_ENABLED` option to true or false depending on whether or not you want
to enable the whitelist, or allow users to create accounts with any usernames that meet the `USERNAME_REGEX`
standard as defined in the `[AUTHENTICATION]` section of the config. 

If `WHITELIST_ENABLED` is set to `True` simply list the usernames in the whitelist below the `WHITELIST_ENABLED`
option, with each username on a seperate line like so:

```
[WHITELIST]
; This section of the configuration is for specifying which users are allowed to
; register. Aside from WHITELIST_ENABLED, each line here should be a username which conformes to the
; regex standard specified in SECURITY_INFO. Every username specified will be permitted to create an account.
WHITELIST_ENABLED = True

someuser1
someuser2
another_user

```
