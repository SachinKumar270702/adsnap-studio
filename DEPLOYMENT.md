# 🚀 AdSnap Studio - Deployment Guide

## Deployment Options

### Option 1: Streamlit Cloud (Recommended - FREE)

#### Prerequisites
- GitHub account
- Streamlit Cloud account (free at https://streamlit.io/cloud)

#### Steps:

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit - AdSnap Studio"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/adsnap-studio.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to https://share.streamlit.io/
   - Click "New app"
   - Select your repository: `YOUR_USERNAME/adsnap-studio`
   - Set main file path: `app.py`
   - Click "Deploy"

3. **Add Secrets (API Keys)**
   - In Streamlit Cloud dashboard, go to your app settings
   - Click "Secrets" in the left sidebar
   - Add your secrets in TOML format:
     ```toml
     BRIA_API_KEY = "your_api_key_here"
     ```
   - Click "Save"

4. **Your app will be live at:**
   `https://YOUR_USERNAME-adsnap-studio-app-xxxxx.streamlit.app`

---

### Option 2: Heroku

#### Prerequisites
- Heroku account
- Heroku CLI installed

#### Steps:

1. **Create Procfile**
   ```bash
   echo "web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0" > Procfile
   ```

2. **Deploy to Heroku**
   ```bash
   heroku login
   heroku create adsnap-studio
   git push heroku main
   heroku config:set BRIA_API_KEY=your_api_key_here
   heroku open
   ```

---

### Option 3: Docker

#### Prerequisites
- Docker installed

#### Steps:

1. **Build Docker image**
   ```bash
   docker build -t adsnap-studio .
   ```

2. **Run container**
   ```bash
   docker run -p 8501:8501 -e BRIA_API_KEY=your_api_key_here adsnap-studio
   ```

3. **Access at:** `http://localhost:8501`

---

### Option 4: AWS EC2

#### Prerequisites
- AWS account
- EC2 instance (t2.micro for free tier)

#### Steps:

1. **SSH into EC2 instance**
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   ```

2. **Install dependencies**
   ```bash
   sudo apt update
   sudo apt install python3-pip
   pip3 install -r requirements.txt
   ```

3. **Run with nohup**
   ```bash
   nohup streamlit run app.py --server.port=8501 --server.address=0.0.0.0 &
   ```

4. **Configure security group** to allow port 8501

---

## Environment Variables

Make sure to set these environment variables in your deployment:

- `BRIA_API_KEY` - Your Bria API key for image generation

---

## Post-Deployment Checklist

- [ ] Test login functionality
- [ ] Verify API key is working
- [ ] Test image generation
- [ ] Test image editing features
- [ ] Check mobile responsiveness
- [ ] Monitor performance
- [ ] Set up error tracking (optional)

---

## Troubleshooting

### Issue: "Module not found"
**Solution:** Make sure all dependencies are in `requirements.txt`

### Issue: "API key not found"
**Solution:** Check that secrets are properly configured in deployment platform

### Issue: "Port already in use"
**Solution:** Change port in config or kill existing process

### Issue: "Memory limit exceeded"
**Solution:** Upgrade to a paid tier or optimize image processing

---

## Performance Tips

1. **Enable caching** for API calls
2. **Compress images** before processing
3. **Use CDN** for static assets
4. **Monitor resource usage**
5. **Set up auto-scaling** for high traffic

---

## Security Best Practices

1. ✅ Never commit `.env` or `secrets.toml` to Git
2. ✅ Use environment variables for sensitive data
3. ✅ Enable HTTPS (automatic on Streamlit Cloud)
4. ✅ Implement rate limiting for API calls
5. ✅ Regular security updates

---

## Support

For issues or questions:
- Check the [Streamlit documentation](https://docs.streamlit.io/)
- Visit [Streamlit Community Forum](https://discuss.streamlit.io/)
- Review the app logs in your deployment platform

---

## License

MIT License - Feel free to use and modify!

---

**Happy Deploying! 🚀**
