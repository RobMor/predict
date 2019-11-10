import os
import argparse

import predict.config


def up(arguments):
    import predict

    # Precedence order
    config_location = arguments.config or os.environ.get("PREDICT_CONFIG") or os.path.expanduser("~/.predict/config.ini")

    config = predict.config.load_config(config_location)

    if config is None:
        config = predict.config.create_default_config()
        predict.config.write_config(config, config_location)

    config["SECURITY"]["LOGIN_REQUIRED"] = str(config.getboolean("SECURITY","LOGIN_REQUIRED") or arguments.secured)

    app = predict.configure_app(config)

    # TODO remove `debug` later
    # If debug is set to True login required is ignored, if false it is not removed
    app.run(debug=True)


def main():
    parser = argparse.ArgumentParser("predict", description="Predict: CVE Labeling Tool")

    parser.set_defaults(target=up, config=None, secured=False)

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

    arguments = parser.parse_args()

    if arguments.target is not None:
        arguments.target(arguments)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
