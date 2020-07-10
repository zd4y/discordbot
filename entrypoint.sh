#!/bin/sh

sleep 3

alembic upgrade head

python -m bot