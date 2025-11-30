import textwrap

def get_mobile_menu_html(current_page, menu_items):
    """
    Generates the HTML for the mobile hamburger menu.
    
    Args:
        current_page (int): The index of the current page.
        menu_items (list): List of tuples (icon, label, page_num).
        
    Returns:
        str: The complete HTML string for the mobile menu.
    """
    
    # Build HTML using a list for cleaner construction and to avoid indentation issues
    html_parts = []
    
    # Hamburger button
    html_parts.append("""
    <button class="hamburger-btn" onclick="toggleMobileMenu()">
        <div class="hamburger-icon">
            <span></span>
            <span></span>
            <span></span>
        </div>
    </button>
    """)
    
    # Overlay
    html_parts.append('<div class="mobile-menu-overlay" onclick="toggleMobileMenu()"></div>')
    
    # Menu Start
    html_parts.append("""
    <div class="mobile-menu">
        <div class="mobile-menu-header">
            <div class="mobile-menu-logo"><i class="fas fa-layer-group"></i></div>
            <div class="mobile-menu-title">ADSNAP</div>
        </div>
        <div class="mobile-menu-items">
    """)
    
    # Menu Items
    for icon, label, page_num in menu_items:
        active_class = "active" if current_page == page_num else ""
        html_parts.append(f"""
        <a href="?page={page_num}" class="mobile-menu-item {active_class}">
            <div class="mobile-menu-item-icon">{icon}</div>
            <div class="mobile-menu-item-label">{label}</div>
        </a>
        """)
        
    # Menu Footer and End
    html_parts.append("""
        </div>
        <div class="mobile-menu-footer">
            <div class="mobile-menu-footer-text">AI-Powered Image Generation</div>
        </div>
    </div>
    """)
    
    # Script
    html_parts.append("""
    <script>
    function toggleMobileMenu() {
        const menu = document.querySelector('.mobile-menu');
        const overlay = document.querySelector('.mobile-menu-overlay');
        if (menu && overlay) {
            menu.classList.toggle('active');
            overlay.classList.toggle('active');
        }
    }
    </script>
    """)
    
    # Join all parts and dedent each part individually to be safe, 
    # but the list approach is already safer.
    # We'll use textwrap.dedent on the final joined string or per block.
    # Best approach: dedent each block before appending or just ensure no indentation in the blocks.
    
    final_html = ""
    for part in html_parts:
        final_html += textwrap.dedent(part)
        
    return final_html
