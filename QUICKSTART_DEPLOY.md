# 🚀 Quick Start - Deploy in 5 Minutes!

## Option 1: Streamlit Cloud (Easiest - FREE)

### Step 1: Prepare Your Code
```bash
# Make sure all files are saved
git status
```

### Step 2: Push to GitHub
```bash
# If not already initialized
git init
git add .
git commit -m "Deploy AdSnap Studio"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/adsnap-studio.git
git branch -M main
git push -u origin main
```

### Step 3: Deploy on Streamlit Cloud
1. Go to https://share.streamlit.io/
2. Sign in with GitHub
3. Click **"New app"**
4. Fill in:
   - **Repository:** `YOUR_USERNAME/adsnap-studio`
   - **Branch:** `main`
   - **Main file path:** `app.py`
5. Click **"Advanced settings"**
6. Add secrets:
   ```toml
   BRIA_API_KEY = "your_actual_api_key_here"
   ```
7. Click **"Deploy!"**

### Step 4: Wait 2-3 Minutes
Your app will be live at:
`https://YOUR_USERNAME-adsnap-studio-app-xxxxx.streamlit.app`

---

## Option 2: Run Locally (For Testing)

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "BRIA_API_KEY=your_api_key_here" > .env

# Run the app
streamlit run app.py
```

Open: http://localhost:8501

---

## Option 3: Docker (For Advanced Users)

```bash
# Build image
docker build -t adsnap-studio .

# Run container
docker run -p 8501:8501 -e BRIA_API_KEY=your_api_key_here adsnap-studio
```

Open: http://localhost:8501

---

## 🎯 What You Need

1. ✅ GitHub account (free)
2. ✅ Streamlit Cloud account (free)
3. ✅ Bria API key (get from https://bria.ai)

---

## 🆘 Troubleshooting

### "Module not found" error
```bash
pip install -r requirements.txt
```

### "API key not found" error
- Check secrets are added in Streamlit Cloud dashboard
- Make sure key name is exactly: `BRIA_API_KEY`

### App won't start
- Check logs in Streamlit Cloud dashboard
- Verify all files are committed to GitHub
- Ensure `app.py` is in root directory

---

## 📱 After Deployment

1. **Test the app** - Try all features
2. **Share the link** - Send to users
3. **Monitor usage** - Check Streamlit Cloud dashboard
4. **Update anytime** - Just push to GitHub!

---

## 🎉 That's It!

Your AdSnap Studio is now live and accessible worldwide!

**Need help?** Check [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.
