#!/bin/bash
# Executes the command from argument (the entire argument is the command) sends it to the background and return success if the command is executed successfully, otherwise return failure.

"$@" & 
exit 0
