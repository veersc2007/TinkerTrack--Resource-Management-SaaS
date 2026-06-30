#!/usr/bin/env pwsh
# GitHub CI/CD Setup Script for Windows PowerShell

Write-Host "🚀 TinkerTrack GitHub CI/CD Setup" -ForegroundColor Green
Write-Host ""

# Step 1: Configure git
Write-Host "Step 1: Configuring git..." -ForegroundColor Cyan
git config --global user.name "Aditya Veer"
git config --global user.email "aditya@tinkertrack.com"

# Step 2: Initialize repo
Write-Host "Step 2: Initializing git repository..." -ForegroundColor Cyan
git init
git add .
git commit -m "Initial commit: Dockerized TinkerTrack API with CI/CD"

# Step 3: Create main branch
Write-Host "Step 3: Creating main branch..." -ForegroundColor Cyan
git branch -M main

# Display next steps
Write-Host ""
Write-Host "✅ Git repository initialized!" -ForegroundColor Green
Write-Host ""
Write-Host "⏳ MANUAL STEPS REQUIRED:" -ForegroundColor Yellow
Write-Host ""

Write-Host "1️⃣  Create GitHub Repository" -ForegroundColor Blue
Write-Host "   1. Go to: https://github.com/new" -ForegroundColor White
Write-Host "   2. Repository name: tinkertrack" -ForegroundColor White
Write-Host "   3. Description: Smart Shared Resource Management System" -ForegroundColor White
Write-Host "   4. Choose Public or Private" -ForegroundColor White
Write-Host "   5. Click 'Create repository'" -ForegroundColor White
Write-Host ""

Write-Host "2️⃣  Add Remote and Push Code" -ForegroundColor Blue
Write-Host "   Run these commands:" -ForegroundColor White
Write-Host "   git remote add origin https://github.com/veersc2007/tinkertrack.git" -ForegroundColor Yellow
Write-Host "   git push -u origin main" -ForegroundColor Yellow
Write-Host ""

Write-Host "3️⃣  Get Docker Hub Personal Access Token" -ForegroundColor Blue
Write-Host "   1. Go to: https://hub.docker.com/settings/security" -ForegroundColor White
Write-Host "   2. Click 'New Access Token'" -ForegroundColor White
Write-Host "   3. Name: github-ci" -ForegroundColor White
Write-Host "   4. Select 'Read & Write' permissions" -ForegroundColor White
Write-Host "   5. Click 'Generate'" -ForegroundColor White
Write-Host "   6. Copy the token (save it, you'll need it next)" -ForegroundColor White
Write-Host ""

Write-Host "4️⃣  Add GitHub Secrets" -ForegroundColor Blue
Write-Host "   1. Go to: https://github.com/veersc2007/tinkertrack/settings/secrets/actions" -ForegroundColor White
Write-Host "   2. Click 'New repository secret'" -ForegroundColor White
Write-Host ""
Write-Host "   Add Secret 1:" -ForegroundColor White
Write-Host "   Name: DOCKER_USERNAME" -ForegroundColor Yellow
Write-Host "   Value: veersc2007" -ForegroundColor Yellow
Write-Host "   Click 'Add secret'" -ForegroundColor White
Write-Host ""
Write-Host "   Add Secret 2:" -ForegroundColor White
Write-Host "   Name: DOCKER_PASSWORD" -ForegroundColor Yellow
Write-Host "   Value: (Paste the Docker Hub token from step 3)" -ForegroundColor Yellow
Write-Host "   Click 'Add secret'" -ForegroundColor White
Write-Host ""

Write-Host "5️⃣  Verify Setup" -ForegroundColor Blue
Write-Host "   1. Go to: https://github.com/veersc2007/tinkertrack/actions" -ForegroundColor White
Write-Host "   2. You should see the workflow running automatically!" -ForegroundColor White
Write-Host "   3. Watch it build and push to Docker Hub" -ForegroundColor White
Write-Host ""

Write-Host "✅ Done! Your CI/CD is now live!" -ForegroundColor Green
Write-Host ""
