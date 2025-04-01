import logging
import logging.config
import json
import os

def setup_logging(config_path='configs/logging_config.json'):
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)

        #Extract and apply the log level if it's specified
        log_level = config.pop("log_level", "INFO").upper()

        # apply log level dynamically to root logger
        config["root"]["level"] = log_level
        for handler in config["handlers"].values():
            # we could also use log_level for all handlers, or keep per-handler levels
            handler.setdefault("level", log_level)

        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=logging.INFO)
        logging.warning("Logging config file not found. Using basic config.")

def get_logger(name):
    
    #Simply just returns a logger with the given name.
    
    return logging.getLogger(name)