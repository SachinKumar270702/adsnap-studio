
# Global CSS and Styles

GLOBAL_CSS = """<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
/* Critical: Hide any CSS that appears as text */
.stMarkdown style,
.stMarkdown link {
    display: none !important;
}

:root {
    --primary-color: #6366f1;
    --secondary-color: #38bdf8;
    --background-color: #09090b;
    --card-bg: rgba(30, 41, 59, 0.7);
    --card-border: rgba(255, 255, 255, 0.1);
    --text-color: #f8fafc;
    --text-secondary: #94a3b8;
    --accent-glow: 0 0 20px rgba(99, 102, 241, 0.5);
    --glass-border: 1px solid rgba(255, 255, 255, 0.08);
    --glass-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
}

/* Animated Mesh Gradient Background */
.stApp {
    background-color: var(--background-color);
    background-image: 
        radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.15) 0px, transparent 50%),
        radial-gradient(at 100% 0%, rgba(56, 189, 248, 0.15) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(168, 85, 247, 0.15) 0px, transparent 50%),
        radial-gradient(at 0% 100%, rgba(236, 72, 153, 0.15) 0px, transparent 50%);
    background-attachment: fixed;
    color: var(--text-color);
    font-family: 'Inter', sans-serif;
}

/* Glassmorphism Classes */
.glass-card {
    background: var(--card-bg);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: var(--glass-border);
    box-shadow: var(--glass-shadow);
    border-radius: 16px;
}

.glass-panel {
    background: rgba(15, 23, 42, 0.6);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-bottom: var(--glass-border);
}

/* Keyframe Animations */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translate3d(0, 20px, 0);
    }
    to {
        opacity: 1;
        transform: translate3d(0, 0, 0);
    }
}

@keyframes float {
    0% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
    100% { transform: translateY(0px); }
}

@keyframes shimmer {
    0% { background-position: -1000px 0; }
    100% { background-position: 1000px 0; }
}

/* Animation Classes */
.animate-fade-in {
    animation: fadeInUp 0.6s ease-out forwards;
}

.animate-float {
    animation: float 6s ease-in-out infinite;
}

.stagger-1 { animation-delay: 0.1s; }
.stagger-2 { animation-delay: 0.2s; }
.stagger-3 { animation-delay: 0.3s; }

/* Custom Scrollbar */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}
::-webkit-scrollbar-track {
    background: rgba(30, 41, 59, 0.5); 
}
::-webkit-scrollbar-thumb {
    background: rgba(71, 85, 105, 0.8); 
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: rgba(100, 116, 139, 1); 
}

/* Header Styling */
.header-container {
    padding: 60px 20px 40px 20px;
    margin-bottom: 40px;
    text-align: center;
    position: relative;
    z-index: 10;
}
.logo-title-wrapper {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 25px;
    margin-bottom: 15px;
}
.logo-emoji {
    font-size: 4.5rem;
    line-height: 1;
    display: block;
    filter: drop-shadow(0 0 30px rgba(99, 102, 241, 0.4));
    animation: float 6s ease-in-out infinite;
}
.main-title {
    margin: 0;
    font-size: 4rem;
    font-weight: 900;
    letter-spacing: -2px;
    line-height: 1.1;
    background: linear-gradient(135deg, #ffffff 0%, #94a3b8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    filter: drop-shadow(0 4px 10px rgba(0,0,0,0.3));
}

.subtitle {
    margin: 16px 0 0 0;
    background: linear-gradient(90deg, #6366f1 0%, #38bdf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 1.2rem;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
}

/* Mobile Responsive Header */
@media only screen and (max-width: 768px) {
    .header-container {
        padding: 30px 10px 15px 10px;
        margin: -60px -20px 0 -20px;
    }
    .logo-title-wrapper {
        flex-direction: column;
        gap: 15px;
    }
    .logo-emoji {
        font-size: 3rem;
    }
    .main-title {
        font-size: 2.5rem;
    }
    .subtitle {
        font-size: 0.9rem;
    }
}
</style>
"""

# Separate header HTML - to be used only where needed
HEADER_HTML = """
<div class="header-container">
    <div class="logo-title-wrapper">
        <div style="background: transparent; padding: 0; display: flex; align-items: center; justify-content: center;">
            <span class="logo-emoji"><i class="fas fa-layer-group"></i></span>
        </div>
        <div>
            <h1 class="main-title">ADSNAP STUDIO</h1>
            <p class="subtitle">AI-Powered Image Generation & Editing</p>
        </div>
    </div>
</div>
"""

INTERACTIVE_UI_CSS = """<style>
/* Enhanced buttons */
.stButton > button {
    background: linear-gradient(135deg, var(--primary-color), #4f46e5);
    border: none;
    border-radius: 12px;
    padding: 0.75rem 1.5rem;
    font-weight: 600;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    color: white !important;
    letter-spacing: 0.5px;
}

.stButton > button:hover {
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 10px 15px -3px rgba(99, 102, 241, 0.4);
    opacity: 1;
}

/* Primary button style */
.primary-button > button {
    background: linear-gradient(135deg, var(--secondary-color), var(--primary-color)) !important;
}

/* Enhanced cards (Glassmorphism + 3D Hover) */
.feature-card {
    background: var(--card-bg);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: var(--glass-border);
    border-radius: 16px;
    padding: 2rem;
    margin: 1rem 0;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    position: relative;
    overflow: hidden;
    transform-style: preserve-3d;
}

.feature-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    opacity: 0;
    transition: opacity 0.3s;
}

.feature-card:hover {
    transform: translateY(-8px) scale(1.01);
    border-color: rgba(99, 102, 241, 0.3);
    box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.5), 0 0 20px rgba(99, 102, 241, 0.2);
}

.feature-card:hover::before {
    opacity: 1;
}

/* Progress bars */
.progress-container {
    background: rgba(30, 41, 59, 0.5);
    border: var(--glass-border);
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
    backdrop-filter: blur(8px);
}

.progress-bar {
    background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
    height: 8px;
    border-radius: 4px;
    transition: width 0.5s ease;
    box-shadow: 0 0 10px rgba(99, 102, 241, 0.3);
}

/* Animated icons */
.rotating-icon {
    animation: rotate 3s linear infinite;
    color: var(--secondary-color);
}

@keyframes rotate {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

.pulse-icon {
    animation: pulse 2s ease-in-out infinite;
    color: var(--primary-color);
    filter: drop-shadow(0 0 10px rgba(99, 102, 241, 0.4));
}

@keyframes pulse {
    0% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.1); opacity: 0.8; }
    100% { transform: scale(1); opacity: 1; }
}

/* Enhanced metrics */
.metric-card {
    background: var(--card-bg);
    backdrop-filter: blur(12px);
    border: var(--glass-border);
    padding: 1.5rem;
    border-radius: 16px;
    text-align: center;
    margin: 0.5rem;
    transition: all 0.3s ease;
}

.metric-card:hover {
    border-color: var(--secondary-color);
    box-shadow: 0 0 20px rgba(56, 189, 248, 0.3);
    transform: translateY(-4px);
}

.metric-value {
    font-size: 2.5rem;
    font-weight: 800;
    margin-bottom: 0.5rem;
    background: linear-gradient(135deg, #fff 0%, #94a3b8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.metric-label {
    font-size: 0.875rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 600;
}

/* Image gallery */
.image-gallery {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin: 1.5rem 0;
}

.image-item {
    position: relative;
    border-radius: 16px;
    overflow: hidden;
    transition: all 0.4s ease;
    cursor: pointer;
    border: var(--glass-border);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.image-item:hover {
    transform: scale(1.03) translateY(-4px);
    border-color: var(--primary-color);
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2), 0 0 20px rgba(99, 102, 241, 0.3);
}

/* Loading animations */
.loading-spinner {
    border: 3px solid rgba(255, 255, 255, 0.1);
    border-radius: 50%;
    border-top: 3px solid var(--primary-color);
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
    margin: 0 auto;
    box-shadow: 0 0 15px rgba(99, 102, 241, 0.2);
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Notification styles */
.notification {
    padding: 1rem;
    border-radius: 12px;
    margin: 1rem 0;
    border-left: 4px solid;
    animation: slideIn 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    background: var(--card-bg);
    backdrop-filter: blur(12px);
    border: var(--glass-border);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

@keyframes slideIn {
    from { transform: translateX(-20px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}

/* Sidebar enhancements */
.sidebar-section {
    background: rgba(255, 255, 255, 0.03);
    border-radius: 12px;
    padding: 1.25rem;
    margin: 0.75rem 0;
    border: 1px solid transparent;
    transition: all 0.3s ease;
}

.sidebar-section:hover {
    background: rgba(255, 255, 255, 0.05);
    border-color: rgba(255, 255, 255, 0.1);
    transform: translateX(4px);
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: rgba(30, 41, 59, 0.3);
    padding: 8px;
    border-radius: 16px;
    border: var(--glass-border);
}

.stTabs [data-baseweb="tab"] {
    background-color: transparent;
    border-radius: 12px;
    padding: 0.5rem 1.5rem;
    color: var(--text-secondary);
    border: 1px solid transparent;
    transition: all 0.3s ease;
}

.stTabs [aria-selected="true"] {
    background-color: rgba(99, 102, 241, 0.1);
    color: var(--primary-color);
    border-color: rgba(99, 102, 241, 0.2);
    box-shadow: 0 0 15px rgba(99, 102, 241, 0.1);
}
</style>
"""
