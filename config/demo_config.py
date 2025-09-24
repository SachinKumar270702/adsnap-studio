"""
Demo configuration for AdSnap Studio
This file contains sample configurations and settings for demo mode.
"""

# Demo user data
DEMO_USER = {
    'username': 'demo_user',
    'full_name': 'Demo User',
    'email': 'demo@adsnap.studio',
    'created_at': '2024-01-01T00:00:00',
    'is_demo': True
}

# Sample prompts for quick testing
SAMPLE_PROMPTS = [
    "A luxury watch on a marble surface with dramatic lighting",
    "Fresh organic vegetables arranged on a rustic wooden table",
    "Modern smartphone floating in a minimalist tech environment",
    "Artisanal coffee beans scattered around a steaming cup",
    "Designer sneakers on a vibrant urban street background",
    "Elegant perfume bottle surrounded by flower petals",
    "Gourmet chocolate pieces on a dark slate surface",
    "Vintage camera with film rolls in a photographer's studio"
]

# Sample enhancement options
ENHANCEMENT_PRESETS = {
    'professional': {
        'style': 'Professional Photography',
        'lighting': 'Studio Lighting',
        'background': 'Clean White',
        'mood': 'Corporate'
    },
    'lifestyle': {
        'style': 'Lifestyle Photography',
        'lighting': 'Natural Light',
        'background': 'Real Environment',
        'mood': 'Casual'
    },
    'artistic': {
        'style': 'Artistic Photography',
        'lighting': 'Dramatic Lighting',
        'background': 'Creative Scene',
        'mood': 'Inspiring'
    },
    'minimal': {
        'style': 'Minimalist Photography',
        'lighting': 'Soft Lighting',
        'background': 'Simple Clean',
        'mood': 'Elegant'
    }
}

# Feature tour steps
FEATURE_TOUR = [
    {
        'title': 'Generate Images',
        'description': 'Create stunning visuals from text descriptions using AI',
        'icon': '🎨',
        'demo_action': 'Try generating an image with: "Modern laptop on a clean desk"'
    },
    {
        'title': 'Lifestyle Shots',
        'description': 'Transform product photos into lifestyle scenes',
        'icon': '📸',
        'demo_action': 'Upload a product image and place it in a lifestyle setting'
    },
    {
        'title': 'Background Removal',
        'description': 'Automatically remove backgrounds from your images',
        'icon': '✂️',
        'demo_action': 'Upload an image and remove its background instantly'
    },
    {
        'title': 'Add Shadows',
        'description': 'Add realistic shadows to make products look natural',
        'icon': '🌟',
        'demo_action': 'Add professional shadows to your product images'
    },
    {
        'title': 'Generative Fill',
        'description': 'Fill in missing parts of images with AI',
        'icon': '🖌️',
        'demo_action': 'Select an area and let AI fill it intelligently'
    }
]

# UI themes
UI_THEMES = {
    'default': {
        'primary_color': '#667eea',
        'secondary_color': '#764ba2',
        'accent_color': '#FF6B6B',
        'success_color': '#4ECDC4'
    },
    'dark': {
        'primary_color': '#2D3748',
        'secondary_color': '#4A5568',
        'accent_color': '#ED8936',
        'success_color': '#38B2AC'
    },
    'vibrant': {
        'primary_color': '#E53E3E',
        'secondary_color': '#D53F8C',
        'accent_color': '#DD6B20',
        'success_color': '#38A169'
    }
}

# Tips and tricks
TIPS_AND_TRICKS = [
    "💡 Use specific, descriptive prompts for better AI-generated images",
    "🎯 Try different aspect ratios to match your ad format requirements",
    "✨ Combine multiple tools for the best results - generate, then enhance!",
    "📐 Use manual placement for precise product positioning in lifestyle shots",
    "🎨 Experiment with different styles to match your brand aesthetic",
    "⚡ Enable fast mode for quicker results during experimentation",
    "🔄 Use the enhance prompt feature to improve your text descriptions",
    "📱 Preview your ads in different formats before finalizing"
]