import os
import argparse

import predict.config


def up(arguments):
    import predict

    # Precedence order
    config_location = arguments.config or predict.config.config_location()
    
    config = predict.config.load_config(config_location)

    if config is None:
        config = predict.config.create_default_config()
        predict.config.write_config(config, config_location)

    config["SECURITY"]["LOGIN_REQUIRED"] = str(
            config.getboolean("SECURITY", "LOGIN_REQUIRED") or arguments.secured
    )

    app = predict.configure_app(config)

    app.run()

def config(arguments):
    # Precedence order
    config_location = arguments.location or predict.config.config_location()
    config = predict.config.load_config(config_location)

    if config is None or input("Are you sure you want to overwrite the config at %s (Y/n)? " % config_location) == "Y":
        print("Writing default configuration to", config_location)
        config = predict.config.create_default_config()
        predict.config.write_config(config, config_location)


def main():
    parser = argparse.ArgumentParser(
        "predict", description="Predict: CVE Labeling Tool"
    )

    parser.set_defaults(target=up, config=None, secured=False)

    subparsers = parser.add_subparsers(
        title="Available commands", metavar="<command>", prog="predict"
    )

    # --- predict up ---
    up_parser = subparsers.add_parser(
        "up", description="Start the server", help="Start the server"
    )

    up_parser.add_argument(
        "--secured", help="start the application in secure mode", action="store_true"
    )

    up_parser.add_argument(
        "-c", "--config", dest="config", help="specify the configuration file", nargs=1
    )

    # --- predict config ---
    config_parser = subparsers.add_parser(
        "config", description="Create the default configuration", help="Create the default configuration"
    )

    config_parser.set_defaults(target=config)

    config_parser.add_argument("location", nargs="?")

    arguments = parser.parse_args()

    if arguments.target is not None:
        arguments.target(arguments)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
