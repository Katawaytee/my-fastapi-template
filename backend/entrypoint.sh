#!/bin/bash
set -e

echo "Running pre-start tasks..."


echo "Pre-start tasks complete. Starting the application..."

exec "$@"