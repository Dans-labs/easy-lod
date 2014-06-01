#!/bin/bash

echo "`date` Starting full reload of EASY metadata."
SCRIPT_DIR="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

source ../env/bin/activate
python -c "import easyrdf; easyrdf.easy_reload()"

if [ $? -ne 0 ] ; then
  echo "`date` Something went wrong."
  exit -1
fi

echo "`date` Reload complete."
