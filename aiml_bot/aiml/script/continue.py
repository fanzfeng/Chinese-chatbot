# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, "../")
import shelve

from aiml.constants import *
import aiml
import copy

# use any dict like obj here
db = copy.deepcopy(dict(shelve.open("session.db", "c")))
# The Kernel object is the public interface to
# the AIML interpreter.

k = aiml.Kernel(sessionStore=db)

# load from a saved brain
k.loadBrain("brain.sav")

# Loop forever, reading user input from the command
# line and printing responses.
while True:
    if PY3:
        print(k.respond(input("> ")))
    else:
        print(k.respond(raw_input("> ")))
    # db.sync()
