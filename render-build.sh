#!/usr/bin/env bash
set -o errexit  # Exit on error

# Install system-level dependencies
apt-get update
apt-get install -y build-essential libpq-dev
