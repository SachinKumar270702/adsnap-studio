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
    
    # Start of the HTML - using dedent to ensure no leading whitespace
    html = textwrap.dedent("""
    <button class="hamburger-btn" onclick="toggleMobileMenu()">
        <div class="hamburger-icon">
            <span></span>
            <span></span>
            <span></span>
        </div>
    </button>

    <div class="mobile-menu-overlay" onclick="toggleMobileMenu()"></div>

    <div class="mobile-menu">
        <div class="mobile-menu-header">
            <div class="mobile-menu-logo"><i class="fas fa-layer-group"></i></div>
            <div class="mobile-menu-title">ADSNAP</div>
        </div>
        <div class="mobile-menu-items">
    """)

    # Add menu items
    for icon, label, page_num in menu_items:
        active_class = "active" if current_page == page_num else ""
        # dedent ensures these lines don't have 8 spaces of indentation
        html += textwrap.dedent(f"""
        <a href="?page={page_num}" class="mobile-menu-item {active_class}">
            <div class="mobile-menu-item-icon">{icon}</div>
            <div class="mobile-menu-item-label">{label}</div>
        </a>
        """)

    # End of the HTML
    html += textwrap.dedent("""
        </div>
        <div class="mobile-menu-footer">
            <div class="mobile-menu-footer-text">AI-Powered Image Generation</div>
        </div>
    </div>

    <script>
    function toggleMobileMenu() {
        const menu = document.querySelector('.mobile-menu');
        const overlay = document.querySelector('.mobile-menu-overlay');
        menu.classList.toggle('active');
        overlay.classList.toggle('active');
    }
    </script>
    """)
    
    return html
