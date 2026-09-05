import os
import sys

_root = os.path.dirname(os.path.abspath(__file__))
for folder in [_root, os.path.join(_root, "person1"), os.path.join(_root, "person2"), os.path.join(_root, "person4_personalization")]:
    if folder not in sys.path:
        sys.path.insert(0, folder)
