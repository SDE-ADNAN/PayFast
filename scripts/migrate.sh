#!/bin/bash
set -e
echo "Starting Database Migration..."
alembic upgrade head
echo "Migration Completed Successfully!"
