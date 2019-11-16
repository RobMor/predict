import predict
import predict.config

config = predict.config.load_config(predict.config.config_location())
application = predict.configure_app(config)
