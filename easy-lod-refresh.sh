#!/usr/bin/env bash
source ../easy-lod.env/bin/activate
python -c "import easyrdf; easyrdf.full_update()"
