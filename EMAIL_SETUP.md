# 📧 Email Service Setup Guide

## Password Reset Feature

Your AdSnap Studio now has a password reset feature that sends reset links via email!

---

## 🔧 Setup Instructions

### Step 1: Get Gmail App Password

1. Go to your Google Account: https://myaccount.google.com/
2. Click on **Security**
3. Enable **2-Step Verification** (if not already enabled)
4. Go to **App passwords**
5. Select app: **Mail**
6. Select device: **Other** (enter "AdSnap Studio")
7. Click **Generate**
8. Copy the 16-character password

### Step 2: Add to Streamlit Cloud Secrets

1. Go to your Streamlit Cloud dashboard
2. Click on your app
3. Click **Settings** → **Secrets**
4. Add these secrets:

```toml
# Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = "587"
SENDER_EMAIL = "your.email@gmail.com"
SENDER_PASSWORD = "your-16-char-app-password"
```

5. Click **Save**

### Step 3: For Local Development

Add to your `.env` file:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your.email@gmail.com
SENDER_PASSWORD=your-16-char-app-password
```

---

## 🎯 How It Works

### User Flow:

1. **User clicks "Forgot Password?"** on login page
2. **Enters their email address**
3. **Receives email** with reset link
4. **Clicks link** in email
5. **Sets new password**
6. **Logs in** with new password

### Security Features:

- ✅ Reset tokens expire after 1 hour
- ✅ Tokens can only be used once
- ✅ Tokens are hashed for security
- ✅ Email verification required
- ✅ No password exposure

---

## 📧 Email Template

Users will receive a beautiful HTML email with:
- 🎨 Branded design matching AdSnap Studio
- 🔐 Secure reset button
- ⏰ Expiration notice
- 🔗 Fallback link if button doesn't work
- ⚠️ Security warnings

---

## 🧪 Testing

### Test Locally:

1. Set up `.env` with your Gmail credentials
2. Run the app: `streamlit run app.py`
3. Click "Forgot Password?"
4. Enter your email
5. Check your inbox!

### Test on Streamlit Cloud:

1. Add secrets to Streamlit Cloud
2. Deploy your app
3. Test the password reset flow

---

## 🔒 Security Best Practices

1. **Never commit** `.env` file to Git
2. **Use App Passwords** not your actual Gmail password
3. **Rotate passwords** regularly
4. **Monitor** email sending for abuse
5. **Rate limit** reset requests (future enhancement)

---

## 🚨 Troubleshooting

### "Email service not configured"
- Check that all environment variables are set
- Verify SENDER_EMAIL and SENDER_PASSWORD are correct

### "Failed to send email"
- Check Gmail App Password is correct
- Ensure 2-Step Verification is enabled
- Check SMTP settings (server and port)

### "Invalid reset token"
- Token may have expired (1 hour limit)
- Token may have already been used
- Request a new reset link

### "SMTP Authentication Error"
- Verify you're using an App Password, not your regular password
- Check that 2-Step Verification is enabled
- Try generating a new App Password

---

## 🎨 Customization

### Change Email Template:

Edit `components/email_service.py`:
- Modify HTML in `send_password_reset_email()` method
- Update colors, text, and styling
- Add your logo or branding

### Change Token Expiration:

In `email_service.py`, line ~35:
```python
expiration = (datetime.now() + timedelta(hours=1)).isoformat()
# Change hours=1 to your preferred duration
```

---

## 📊 Features

✅ **Implemented:**
- Password reset via email
- Secure token generation
- Token expiration (1 hour)
- One-time use tokens
- Beautiful HTML emails
- Mobile-responsive design

🔜 **Future Enhancements:**
- Rate limiting
- Email verification on signup
- Two-factor authentication
- Password strength meter
- Account recovery options

---

## 🎉 You're All Set!

Once you add the email credentials to your secrets, the password reset feature will work automatically!

**Test it out:**
1. Click "Forgot Password?" on login
2. Enter your email
3. Check your inbox
4. Reset your password!

---

**Need help?** Check the troubleshooting section or review the code in `components/email_service.py`
