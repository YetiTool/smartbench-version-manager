#!/bin/bash
source $1 && shift && "$@"

# Then call any function within any script via:

# ./eval_func.sh <any script> <any function> <any args>...