"""
Email service for sending password reset links and verification emails.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import secrets
import hashlib
from datetime import datetime, timedelta
import json

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.sender_email = os.getenv('SENDER_EMAIL', '')
        self.sender_password = os.getenv('SENDER_PASSWORD', '')
        self.reset_tokens_file = 'data/reset_tokens.json'
        self.load_tokens()
    
    def load_tokens(self):
        """Load password reset tokens from file."""
        if os.path.exists(self.reset_tokens_file):
            try:
                with open(self.reset_tokens_file, 'r') as f:
                    self.reset_tokens = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.reset_tokens = {}
        else:
            self.reset_tokens = {}
    
    def save_tokens(self):
        """Save password reset tokens to file."""
        os.makedirs(os.path.dirname(self.reset_tokens_file), exist_ok=True)
        with open(self.reset_tokens_file, 'w') as f:
            json.dump(self.reset_tokens, f, indent=2)
    
    def generate_reset_token(self, email):
        """Generate a unique password reset token."""
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        # Store token with expiration (1 hour)
        expiration = (datetime.now() + timedelta(hours=1)).isoformat()
        self.reset_tokens[token_hash] = {
            'email': email,
            'expires_at': expiration,
            'used': False
        }
        self.save_tokens()
        
        return token
    
    def verify_reset_token(self, token):
        """Verify if a reset token is valid and not expired."""
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        if token_hash not in self.reset_tokens:
            return False, None, "Invalid reset token"
        
        token_data = self.reset_tokens[token_hash]
        
        if token_data.get('used'):
            return False, None, "This reset link has already been used"
        
        expiration = datetime.fromisoformat(token_data['expires_at'])
        if datetime.now() > expiration:
            return False, None, "This reset link has expired"
        
        return True, token_data['email'], "Token is valid"
    
    def mark_token_used(self, token):
        """Mark a reset token as used."""
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        if token_hash in self.reset_tokens:
            self.reset_tokens[token_hash]['used'] = True
            self.save_tokens()
    
    def send_password_reset_email(self, to_email, reset_link):
        """Send password reset email."""
        if not self.sender_email or not self.sender_password:
            return False, "Email service not configured. Please contact administrator."
        
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = "🔐 AdSnap Studio - Password Reset Request"
            message["From"] = f"AdSnap Studio <{self.sender_email}>"
            message["To"] = to_email
            
            # HTML email body
            html = f"""
            <html>
                <body style="font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px;">
                    <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 15px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.3);">
                        <div style="text-align: center; margin-bottom: 30px;">
                            <h1 style="color: #667eea; margin: 0;">🎨 AdSnap Studio</h1>
                            <p style="color: #666; margin-top: 10px;">Password Reset Request</p>
                        </div>
                        
                        <div style="background: #f8f9fa; border-radius: 10px; padding: 20px; margin-bottom: 20px;">
                            <h2 style="color: #333; margin-top: 0;">Reset Your Password</h2>
                            <p style="color: #666; line-height: 1.6;">
                                We received a request to reset your password for your AdSnap Studio account.
                                Click the button below to create a new password.
                            </p>
                        </div>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{reset_link}" 
                               style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                      color: white; text-decoration: none; padding: 15px 40px; border-radius: 25px; 
                                      font-weight: bold; font-size: 16px; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);">
                                🔐 Reset Password
                            </a>
                        </div>
                        
                        <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 5px; margin: 20px 0;">
                            <p style="margin: 0; color: #856404; font-size: 14px;">
                                <strong>⚠️ Security Notice:</strong><br>
                                This link will expire in 1 hour and can only be used once.
                            </p>
                        </div>
                        
                        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
                            <p style="color: #999; font-size: 12px; margin: 5px 0;">
                                If you didn't request this password reset, please ignore this email.
                                Your password will remain unchanged.
                            </p>
                            <p style="color: #999; font-size: 12px; margin: 5px 0;">
                                If the button doesn't work, copy and paste this link into your browser:
                            </p>
                            <p style="color: #667eea; font-size: 12px; word-break: break-all;">
                                {reset_link}
                            </p>
                        </div>
                        
                        <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
                            <p style="color: #999; font-size: 12px; margin: 0;">
                                © 2024 AdSnap Studio - AI-Powered Image Generation & Editing
                            </p>
                        </div>
                    </div>
                </body>
            </html>
            """
            
            # Plain text version
            text = f"""
            AdSnap Studio - Password Reset Request
            
            We received a request to reset your password for your AdSnap Studio account.
            
            Click this link to reset your password:
            {reset_link}
            
            This link will expire in 1 hour and can only be used once.
            
            If you didn't request this password reset, please ignore this email.
            Your password will remain unchanged.
            
            © 2024 AdSnap Studio
            """
            
            # Attach both versions
            part1 = MIMEText(text, "plain")
            part2 = MIMEText(html, "html")
            message.attach(part1)
            message.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            return True, "Password reset email sent successfully!"
            
        except Exception as e:
            return False, f"Failed to send email: {str(e)}"
    
    def send_verification_email(self, to_email, verification_code):
        """Send email verification code."""
        if not self.sender_email or not self.sender_password:
            return False, "Email service not configured"
        
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = "✅ AdSnap Studio - Verify Your Email"
            message["From"] = f"AdSnap Studio <{self.sender_email}>"
            message["To"] = to_email
            
            html = f"""
            <html>
                <body style="font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px;">
                    <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 15px; padding: 30px;">
                        <h1 style="color: #667eea; text-align: center;">🎨 AdSnap Studio</h1>
                        <h2 style="color: #333;">Verify Your Email</h2>
                        <p style="color: #666;">Your verification code is:</p>
                        <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center; margin: 20px 0;">
                            <h1 style="color: #667eea; font-size: 36px; letter-spacing: 5px; margin: 0;">{verification_code}</h1>
                        </div>
                        <p style="color: #999; font-size: 12px;">This code will expire in 10 minutes.</p>
                    </div>
                </body>
            </html>
            """
            
            part = MIMEText(html, "html")
            message.attach(part)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            return True, "Verification email sent!"
            
        except Exception as e:
            return False, f"Failed to send email: {str(e)}"
