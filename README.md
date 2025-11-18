# 🎨 AdSnap Studio

A powerful Streamlit app for generating professional product ads using Bria AI's advanced image generation and manipulation APIs.

## 🌟 Features

### 🎨 Image Generation
- Generate 1-4 HD images simultaneously from text prompts
- Multiple aspect ratios (1:1, 16:9, 9:16, 4:3, 3:4)
- Style options (Realistic, Artistic, Cartoon, Sketch, etc.)
- AI-powered prompt enhancement
- Smart collage display for multiple images

### ✨ Unified Image Editor
- Upload once, apply any editing feature
- Create professional packshots
- Add natural or drop shadows
- Generative fill for masked areas
- Automatic foreground removal
- Background removal with transparency

### 🖼️ Product Photography
- Professional lifestyle shots
- Custom background colors
- Shadow effects with adjustable intensity
- Force background removal option

### 🔐 Authentication & User Management
- Secure login/signup system
- Password reset via email (Gmail SMTP)
- Demo mode for quick testing
- Persistent sessions across page refreshes
- User profile management

### 📊 Dashboard & Analytics
- Interactive dashboard with quick actions
- Activity tracking and usage statistics
- Feature tour for new users
- Real-time metrics



1. Clone the repository:
```bash
git clone https://github.com/yourusername/adsnap-studio.git
cd adsnap-studio
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory (copy from `.env.example`):
```bash
# Bria AI API
BRIA_API_KEY=your_bria_api_key_here

# Email Configuration (optional, for password reset)
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_gmail_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

4. Run the app:
```bash
streamlit run app.py
```

## 💡 Usage

### Quick Start
1. **Login** - Use demo mode or create an account
2. **Choose a feature** from the navigation tabs:
   - 🎨 **Generate Image** - Create images from text prompts
   - ✨ **Image Editor** - Upload and edit images with all tools
   - 🖼️ **Lifestyle Shot** - Professional product photography
   - 🎨 **Generative Fill** - Fill masked areas with AI
   - 🎨 **Erase Elements** - Remove objects automatically

### Generate Multiple Images
1. Go to "Generate Image" tab
2. Enter your prompt (or enhance it with AI)
3. Select number of images (1-4)
4. Choose aspect ratio and style
5. Click "Generate Images"
6. View results in smart collage layout
7. Download individual images

### Edit Images
1. Go to "Image Editor" tab
2. Upload your image
3. Select editing feature from dropdown
4. Adjust settings
5. Click the action button
6. Download result

## 🔧 Configuration

The app supports various configuration options through the UI:

- **Prompt Enhancement**: Improve your text prompts with AI
- **Background Removal**: Remove backgrounds with custom colors
- **Shadow Effects**: Add realistic shadows with adjustable intensity
- **Lifestyle Shots**: Place products in context using text or reference images
- **CTA Text**: Add optional call-to-action text overlays

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Bria AI](https://bria.ai) for their powerful image generation APIs
- [Streamlit](https://streamlit.io) for the amazing web framework 

## 🚀 D
eployment

### Streamlit Cloud (Recommended)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io/)
   - Click "New app"
   - Select your repository
   - Set main file: `app.py`
   - Add secrets in dashboard:
     ```toml
     BRIA_API_KEY = "your_api_key_here"
     ```
   - Click "Deploy"

3. **Your app will be live!** 🎉

For more deployment options (Docker, Heroku, AWS), see [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 📦 Files Created for Deployment

- ✅ `requirements.txt` - Python dependencies
- ✅ `.streamlit/config.toml` - Streamlit configuration
- ✅ `Dockerfile` - Docker containerization
- ✅ `Procfile` - Heroku deployment
- ✅ `packages.txt` - System dependencies
- ✅ `.gitignore` - Git ignore rules
- ✅ `DEPLOYMENT.md` - Detailed deployment guide

---

## 🎨 New Features

### Authentication System
- Secure login/signup
- Demo mode for testing
- Persistent sessions
- User profiles

### Interactive Dashboard
- Real-time statistics
- Activity tracking
- Quick action buttons
- Daily tips

### Beautiful UI
- Animated gradient backgrounds
- Glass morphism design
- Smooth transitions
- Mobile responsive

---

## 🔒 Security Notes

- Never commit `.env` or `secrets.toml` files
- Use environment variables for API keys
- Enable HTTPS in production
- Regular security updates

---

**Ready to deploy? Follow the steps above! 🚀**
