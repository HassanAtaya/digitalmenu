#!/bin/bash
echo ">>> Saving local changes..."
git stash push -m "keep local env & run.py"

echo ">>> Pulling latest from origin main..."
git pull origin main

echo ">>> Restoring local changes..."
git stash pop

echo ">>> Running Angular build..."
cd /home/ubuntu/evoo_digitalmenu/test_evolusys/digitalmenu/angular
/usr/bin/npx --yes @angular/cli@19.2.8 build --configuration production

echo ">>> Restarting digitalmenu.service..."
sudo systemctl restart digitalmenu.service

echo ">>> Done."
