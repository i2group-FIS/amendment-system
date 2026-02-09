#!/bin/bash

# Install dependencies
echo "Installing Node.js dependencies..."
npm install --production

# The app will be started by Azure using the startup command: npm start
echo "Deployment complete. App will start with: npm start"
