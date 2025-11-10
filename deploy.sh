#!/bin/bash

# AdSnap Studio - Quick Deployment Script

echo "🚀 AdSnap Studio Deployment Helper"
echo "===================================="
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "📦 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit - AdSnap Studio"
    git branch -M main
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

echo ""
echo "Choose deployment option:"
echo "1. Streamlit Cloud (Recommended)"
echo "2. Docker Local"
echo "3. Heroku"
echo "4. Just commit changes"
echo ""
read -p "Enter option (1-4): " option

case $option in
    1)
        echo ""
        echo "📋 Streamlit Cloud Deployment Steps:"
        echo "1. Push your code to GitHub"
        echo "2. Go to https://share.streamlit.io/"
        echo "3. Click 'New app'"
        echo "4. Select your repository"
        echo "5. Set main file: app.py"
        echo "6. Add secrets in dashboard"
        echo ""
        read -p "Enter your GitHub repository URL: " repo_url
        if [ ! -z "$repo_url" ]; then
            git remote add origin $repo_url 2>/dev/null || git remote set-url origin $repo_url
            git push -u origin main
            echo "✅ Code pushed to GitHub!"
            echo "🌐 Now deploy at: https://share.streamlit.io/"
        fi
        ;;
    2)
        echo ""
        echo "🐳 Building Docker image..."
        docker build -t adsnap-studio .
        echo "✅ Docker image built!"
        echo ""
        echo "🚀 Starting container..."
        docker run -p 8501:8501 -e BRIA_API_KEY=$BRIA_API_KEY adsnap-studio
        ;;
    3)
        echo ""
        echo "☁️ Deploying to Heroku..."
        heroku create adsnap-studio-$(date +%s)
        git push heroku main
        heroku config:set BRIA_API_KEY=$BRIA_API_KEY
        heroku open
        echo "✅ Deployed to Heroku!"
        ;;
    4)
        echo ""
        echo "💾 Committing changes..."
        git add .
        read -p "Enter commit message: " commit_msg
        git commit -m "$commit_msg"
        echo "✅ Changes committed!"
        ;;
    *)
        echo "❌ Invalid option"
        exit 1
        ;;
esac

echo ""
echo "✨ Done!"
