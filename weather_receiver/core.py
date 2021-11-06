# Copyright 2021 Florian Tautz
import contextlib

import serial
import requests

SERIAL_TIMEOUT = 1


class WeatherReceiver:
    def __init__(self, port, api_url, file=None):
        self.port = port
        self.api_url = api_url
        self.file = file

    def run(self):
        with contextlib.ExitStack() as stack:
            port = stack.enter_context(serial.Serial(self.port, timeout=SERIAL_TIMEOUT))
            fp = stack.enter_context(open(self.file, "ab"))

            while True:
                raw_line = port.readline()
                if len(raw_line) == 0:
                    continue
                fp.write(raw_line)
                requests.post(self.api_url, data=raw_line)


def main():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("serial_port")
    parser.add_argument("api_url")
    parser.add_argument("--file")
    args = parser.parse_args()

    receiver = WeatherReceiver(args.serial_port, args.api_url, args.file)
    receiver.run()


if __name__ == '__main__':
    main()
