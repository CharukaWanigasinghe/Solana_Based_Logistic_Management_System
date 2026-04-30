// B To B INTELLICA Logistics - Page Transition and Animation Script

document.addEventListener('DOMContentLoaded', function() {
    // Add page transition class to body
    document.body.classList.add('page-transition');

    // Handle form submissions with loading animation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"], input[type="submit"], .search-btn');
            if (submitBtn) {
                submitBtn.classList.add('loading');
                submitBtn.innerHTML = '<span class="loading-spinner"></span> Processing...';

                // Add loading overlay
                const overlay = document.createElement('div');
                overlay.className = 'loading-overlay show';
                overlay.innerHTML = '<div class="loading-spinner"></div><p>Loading...</p>';
                document.body.appendChild(overlay);

                // Remove loading state after a delay (in case of redirect)
                setTimeout(() => {
                    submitBtn.classList.remove('loading');
                    if (overlay.parentNode) {
                        overlay.parentNode.removeChild(overlay);
                    }
                }, 2000);
            }
        });
    });

    // Add click animations to buttons
    const buttons = document.querySelectorAll('button, .search-btn, .generate-btn, .excel-btn, .gps-btn');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Add ripple effect
            const ripple = document.createElement('span');
            ripple.className = 'ripple-effect';
            this.appendChild(ripple);

            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = (e.clientX - rect.left - size/2) + 'px';
            ripple.style.top = (e.clientY - rect.top - size/2) + 'px';

            setTimeout(() => {
                if (ripple.parentNode) {
                    ripple.parentNode.removeChild(ripple);
                }
            }, 600);
        });
    });

    // Smooth scroll for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add entrance animations to elements as they come into view
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);

    // Observe elements for animation
    const animateElements = document.querySelectorAll('.welcome-container, .delivery-info, .table-container, .location-info');
    animateElements.forEach(element => {
        observer.observe(element);
    });

    // Add stagger animation to table rows
    const tableRows = document.querySelectorAll('#deliveries-table tr');
    tableRows.forEach((row, index) => {
        row.style.animationDelay = `${index * 0.1}s`;
    });

    // GPS functionality with visual feedback
    const gpsButtons = document.querySelectorAll('.gps-btn');
    gpsButtons.forEach(button => {
        button.addEventListener('click', function() {
            this.innerHTML = '<span class="loading-spinner" style="width: 16px; height: 16px; display: inline-block; margin-right: 8px;"></span> Getting Location...';
            this.disabled = true;

            setTimeout(() => {
                this.innerHTML = '📍 Get Current Location';
                this.disabled = false;
            }, 3000);
        });
    });

    // Add success message for form submissions (if redirected back)
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('success') === 'true') {
        const successMsg = document.createElement('div');
        successMsg.className = 'success-message';
        successMsg.textContent = 'Operation completed successfully!';
        document.querySelector('main').prepend(successMsg);

        setTimeout(() => {
            successMsg.style.opacity = '0';
            setTimeout(() => successMsg.remove(), 500);
        }, 3000);
    }
});

// Add CSS for ripple effect and additional animations
const style = document.createElement('style');
style.textContent = `
    .ripple-effect {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.6);
        transform: scale(0);
        animation: ripple 0.6s linear;
        pointer-events: none;
    }

    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }

    .animate-in {
        animation: fadeInUp 0.8s ease-out forwards;
    }

    .loading {
        position: relative;
        color: transparent !important;
    }

    .loading::after {
        content: '';
        position: absolute;
        width: 16px;
        height: 16px;
        top: 50%;
        left: 50%;
        margin-left: -8px;
        margin-top: -8px;
        border: 2px solid #ffffff;
        border-radius: 50%;
        border-top-color: transparent;
        animation: spin 1s linear infinite;
    }

    /* Enhanced hover effects */
    .welcome-container:hover {
        transform: translateY(-5px);
        transition: transform 0.3s ease;
    }

    .delivery-info:hover {
        transform: translateY(-3px);
        transition: transform 0.3s ease;
    }

    /* Smooth transitions for all interactive elements */
    * {
        transition: border-color 0.3s ease, box-shadow 0.3s ease;
    }
`;
document.head.appendChild(style);

// Page unload animation
window.addEventListener('beforeunload', function() {
    document.body.style.opacity = '0';
    document.body.style.transform = 'translateY(-20px)';
    document.body.style.transition = 'all 0.3s ease';
});