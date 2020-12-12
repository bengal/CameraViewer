#!/usr/bin/python3

import config
import viewer
import sys

import gi

c = config.read_config()
if c is None:
    print("Configuration error")
    sys.exit(1)

if len(c.cameras) == 0:
    print("No camera defined")
    sys.exit(1)

print(c)

viewer = viewer.Viewer(c)

