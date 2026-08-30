"""Contract test package.

Made a package (unlike ``tests/integration``) so the Schemathesis suite and
its classification unit tests can share ``classification.py`` via a normal
relative import rather than a generic top-level module name.
"""
