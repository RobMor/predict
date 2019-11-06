import argparse

import predict.config

def up(arguments):
    import predict

    config = {
        #Do we want this written to the config file with whitelist and stuff?
        "LOGIN_DISABLED": not arguments.secured
        # TODO more config stuff...
    }

    app = predict.configure_app(config)

    # TODO remove `debug` later
    app.run(debug=True)


def config_set(arguments):
    import configparser


def config_remove(arguments):
    import configparser


def main():
    parser = argparse.ArgumentParser("predict", description="Predict: CVE Labeling Tool")

    parser.set_defaults(target=up, secured=False)

    subparsers = parser.add_subparsers(title="Available commands", metavar="<command>", prog="predict")

    # --- predict up ---
    up_parser = subparsers.add_parser(
        "up",
        description="Start the server",
        help="Start the server"
    )

    up_parser.add_argument("--secured", help="start the application in secure mode", action="store_true")

    up_parser.add_argument("-c", "--config", dest="config", help="specify the configuration file", nargs=1)

    # --- predict config ---
    config_parser = subparsers.add_parser(
        "config",
        description="Configure this tool",
        help="Configure this tool"
    )

    config_parser.set_defaults(target=None)

    config_subparser = config_parser.add_subparsers(title="Available commands", metavar="<command>", prog="predict")

    config_set_parser = config_subparser.add_parser(
        "set",
        description="Set a configuration entry",
        help="Set a configuration entry"
    )

    config_set_parser.set_defaults(target=config_set)

    config_remove_parser = config_subparser.add_parser(
        "remove",
        description="Remove a configuration entry",
        help="Remove a configuration entry"
    )

    config_remove_parser.set_defaults(target=config_remove)

    # --- 

    arguments = parser.parse_args()

    if arguments.target is not None:
        arguments.target(arguments)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()