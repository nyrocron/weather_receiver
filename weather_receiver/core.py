# Copyright 2021 Florian Tautz

import contextlib
import logging
from datetime import datetime

import serial
import requests


SERIAL_TIMEOUT = 1

logger = logging.getLogger(__name__)


class WeatherReceiver:
    def __init__(self, port, api_url, file=None):
        self.port = port
        self.api_url = api_url
        self.file = file

    def run(self):
        with contextlib.ExitStack() as stack:
            port = stack.enter_context(serial.Serial(self.port, timeout=SERIAL_TIMEOUT))
            fp = stack.enter_context(open(self.file, "a"))

            while True:
                raw_line = port.readline()
                if len(raw_line) == 0:
                    continue
                line = datetime.utcnow().isoformat() + raw_line.decode("ascii").rstrip()
                logger.info("received " + line)
                try:
                    fp.write(line + "\n")
                    fp.flush()
                except:
                    logger.exception("failed to save measurement to file")
                try:
                    requests.post(self.api_url, data=line)
                except:
                    logger.exception("failed to submit measurement to server")


def main():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("serial_port")
    parser.add_argument("api_url")
    parser.add_argument("--file", default="weather_data.txt")
    parser.add_argument("--log", default="weather_receiver.log")
    args = parser.parse_args()

    log_format = "[%(asctime)s] <%(levelname)s> %(name)s: %(message)s"
    time_format = "%Y-%m-%d %H:%M:%S%z"

    logging.basicConfig(level=logging.DEBUG, format=log_format, datefmt=time_format)

    logfile_formatter = logging.Formatter(log_format, time_format)
    logfile_handler = logging.FileHandler(args.log)
    logfile_handler.setFormatter(logfile_formatter)
    logfile_handler.setLevel(logging.INFO)
    logging.getLogger().addHandler(logfile_handler)

    receiver = WeatherReceiver(args.serial_port, args.api_url, args.file)
    try:
        receiver.run()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
