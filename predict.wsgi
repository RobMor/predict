import predict
import predict.config

config_location = predict.config.config_location()
config = predict.config.load_config(config_location)

if config is None:
    raise Exception("Configuration File Not Found At {}".format(config_location))

application = predict.configure_app(config)
