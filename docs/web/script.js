/**
 * Agent Tool Description Format (ATDF) Website Scripts
 */

// Tab functionality
function openTab(evt, tabName) {
    // Get all tab content elements and hide them
    const tabcontent = document.getElementsByClassName("tab-content");
    for (let i = 0; i < tabcontent.length; i++) {
        tabcontent[i].classList.remove("active");
    }
    
    // Remove active class from all tabs
    const tablinks = document.getElementsByClassName("tab");
    for (let i = 0; i < tablinks.length; i++) {
        tablinks[i].classList.remove("active");
    }
    
    // Show the selected tab content and mark the button as active
    document.getElementById(tabName).classList.add("active");
    evt.currentTarget.classList.add("active");
}

// Smooth scrolling for navigation links
document.addEventListener('DOMContentLoaded', function() {
    // Get all navigation links with hash
    const navLinks = document.querySelectorAll('nav a[href^="#"]');
    
    // Add click event listener to each navigation link
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Prevent default link behavior
            e.preventDefault();
            
            // Get the target element
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                // Smooth scroll to target
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// Add active class to navigation links on scroll
window.addEventListener('scroll', function() {
    // Get all sections
    const sections = document.querySelectorAll('section');
    const navLinks = document.querySelectorAll('nav a[href^="#"]');
    
    // Get current scroll position
    const scrollPosition = window.scrollY;
    
    // Check each section
    sections.forEach(section => {
        const sectionTop = section.offsetTop - 100;
        const sectionHeight = section.offsetHeight;
        const sectionId = section.getAttribute('id');
        
        if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
            // Remove active class from all links
            navLinks.forEach(link => {
                link.classList.remove('active');
            });
            
            // Add active class to current section link
            const activeLink = document.querySelector(`nav a[href="#${sectionId}"]`);
            if (activeLink) {
                activeLink.classList.add('active');
            }
        }
    });
});

// Toggle mobile navigation
function toggleMobileNav() {
    const nav = document.querySelector('nav ul');
    nav.classList.toggle('mobile-active');
}

// Initialize syntax highlighting if available
document.addEventListener('DOMContentLoaded', function() {
    if (typeof hljs !== 'undefined') {
        hljs.highlightAll();
    }
});

// Version switcher functionality
function switchVersion(version) {
    // Hide all version-specific content
    const versionContent = document.querySelectorAll('.version-content');
    versionContent.forEach(content => {
        content.style.display = 'none';
    });
    
    // Show content for selected version
    const selectedContent = document.querySelectorAll(`.${version}-content`);
    selectedContent.forEach(content => {
        content.style.display = 'block';
    });
    
    // Update active version button
    const versionButtons = document.querySelectorAll('.version-switcher button');
    versionButtons.forEach(button => {
        button.classList.remove('active');
    });
    document.querySelector(`.${version}-button`).classList.add('active');
} 