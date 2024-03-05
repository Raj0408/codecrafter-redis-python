import argparse

class CLIArgParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="CLI for the app")
        self.parser.add_argument("--dir")
        self.parser.add_argument("--dbfilename")
        self.parser.add_argument("--port")
    def parse_args(self):
        return self.parser.parse_args()