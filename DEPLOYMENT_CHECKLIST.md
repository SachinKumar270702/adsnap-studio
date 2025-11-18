# 🚀 Deployment Checklist

## ✅ Pre-Deployment Checks

### Code & Files
- [x] All code committed to GitHub
- [x] `.gitignore` properly configured
- [x] `.env` file NOT committed (only `.env.example`)
- [x] `requirements.txt` up to date
- [x] `.streamlit/config.toml` configured
- [x] README.md updated with latest features

### Security
- [ ] API keys stored in environment variables
- [ ] No sensitive data in code
- [ ] User data directory (`data/`) in `.gitignore`
- [ ] Email credentials secured

### Testing
- [ ] App runs locally without errors
- [ ] All features tested:
  - [ ] Login/Signup works
  - [ ] Image generation (1-4 images)
  - [ ] Image editor (all tools)
  - [ ] Lifestyle shot
  - [ ] Generative fill
  - [ ] Erase elements
- [ ] Password reset email works (if configured)

## 🌐 Streamlit Cloud Deployment

### Step 1: Prepare Repository
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

### Step 2: Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io/)
2. Click "New app"
3. Connect your GitHub account
4. Select repository: `your-username/adsnap-studio`
5. Set branch: `main`
6. Set main file: `app.py`
7. Click "Advanced settings"

### Step 3: Configure Secrets
Add these secrets in the Streamlit Cloud dashboard:

```toml
# Required
BRIA_API_KEY = "your_bria_api_key_here"

# Optional (for password reset feature)
SENDER_EMAIL = "your_email@gmail.com"
SENDER_PASSWORD = "your_gmail_app_password"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = "587"
```

### Step 4: Deploy
1. Click "Deploy"
2. Wait for deployment (2-5 minutes)
3. Your app will be live at: `https://your-app-name.streamlit.app`

## 📧 Email Setup (Optional)

If you want password reset functionality:

1. **Enable Gmail App Password**
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate app password for "Mail"
   - Copy the 16-character password

2. **Add to Streamlit Secrets**
   - Add `SENDER_EMAIL` and `SENDER_PASSWORD` to secrets
   - See `EMAIL_SETUP.md` for detailed instructions

## 🔍 Post-Deployment Checks

- [ ] App loads without errors
- [ ] Login/signup works
- [ ] Demo mode works
- [ ] Image generation works
- [ ] All editing features functional
- [ ] Images download correctly
- [ ] Mobile responsive
- [ ] No console errors

## 🐛 Troubleshooting

### App won't start
- Check logs in Streamlit Cloud dashboard
- Verify all dependencies in `requirements.txt`
- Check Python version compatibility

### API errors
- Verify `BRIA_API_KEY` is set correctly in secrets
- Check API key is valid and has credits
- Review API rate limits

### Email not working
- Verify Gmail app password is correct
- Check SMTP settings in secrets
- Ensure 2-factor authentication enabled on Gmail

### Images not displaying
- Check API response in browser console
- Verify image URLs are accessible
- Check network connectivity

## 📱 Share Your App

Once deployed, share your app URL:
```
https://your-app-name.streamlit.app
```

## 🔄 Updates

To update your deployed app:
```bash
git add .
git commit -m "Update: description of changes"
git push origin main
```

Streamlit Cloud will automatically redeploy!

## 🎉 Success!

Your AdSnap Studio is now live and ready to use!

---

**Need help?** Check:
- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [DEPLOYMENT.md](DEPLOYMENT.md) for other deployment options
- [EMAIL_SETUP.md](EMAIL_SETUP.md) for email configuration
