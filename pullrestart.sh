#!/bin/bash

echo ">>> Saving local changes..."
git stash push -m "keep local env & run.py"

echo ">>> Pulling latest from origin main..."
git pull origin main

echo ">>> Restoring local changes..."
git stash pop

echo ">>> Restarting digitalmenu.service..."
sudo systemctl restart digitalmenu.service

echo ">>> Done."
