#!/bin/bash
# GitHub CI/CD Setup Script

echo "🚀 TinkerTrack GitHub CI/CD Setup"
echo ""

# Step 1: Configure git
echo "Step 1: Configuring git..."
git config --global user.name "Aditya Veer"
git config --global user.email "aditya@tinkertrack.com"

# Step 2: Initialize repo
echo "Step 2: Initializing git repository..."
git init
git add .
git commit -m "Initial commit: Dockerized TinkerTrack API with CI/CD"

# Step 3: Create main branch
echo "Step 3: Creating main branch..."
git branch -M main

# Display next steps
echo ""
echo "✅ Git repository initialized!"
echo ""
echo "⏳ Next steps (MANUAL - you need to do these):"
echo ""
echo "1️⃣ Create GitHub repository:"
echo "   Go to https://github.com/new"
echo "   Repository name: tinkertrack"
echo "   Description: Smart Shared Resource Management System"
echo "   Public/Private: Your choice"
echo "   Click 'Create repository'"
echo ""
echo "2️⃣ Add remote and push code:"
echo "   git remote add origin https://github.com/veersc2007/tinkertrack.git"
echo "   git push -u origin main"
echo ""
echo "3️⃣ Add GitHub Secrets:"
echo "   Go to: https://github.com/veersc2007/tinkertrack/settings/secrets/actions"
echo "   Click 'New repository secret'"
echo ""
echo "   Secret 1:"
echo "   Name: DOCKER_USERNAME"
echo "   Value: veersc2007"
echo ""
echo "   Secret 2:"
echo "   Name: DOCKER_PASSWORD"
echo "   Value: (Get from https://hub.docker.com/settings/security)"
echo "     - Click 'New Access Token'"
echo "     - Name: github-ci"
echo "     - Permissions: Read, Write"
echo "     - Copy token and paste here"
echo ""
echo "4️⃣ Verify:"
echo "   Go to https://github.com/veersc2007/tinkertrack/actions"
echo "   Watch the workflow run automatically!"
echo ""
