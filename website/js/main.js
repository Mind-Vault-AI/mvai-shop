/**
 * MindVault-AI - Main JavaScript
 * Version: 1.0.0
 *
 * Features:
 * - Preloader
 * - Navbar scroll effect
 * - Mobile navigation
 * - Template tabs
 * - Counter animation
 * - Scroll animations (AOS-like)
 * - Smooth scroll
 */

// ============================================
// DOM Ready
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    initPreloader();
    initNavbar();
    initMobileNav();
    initTemplateTabs();
    initCounterAnimation();
    initScrollAnimations();
    initSmoothScroll();
});

// ============================================
// Preloader
// ============================================
function initPreloader() {
    const preloader = document.getElementById('preloader');

    if (!preloader) return;

    // Hide preloader when page is fully loaded
    window.addEventListener('load', () => {
        setTimeout(() => {
            preloader.classList.add('loaded');

            // Remove from DOM after animation
            setTimeout(() => {
                preloader.remove();
            }, 500);
        }, 500);
    });

    // Fallback: hide after 3 seconds max
    setTimeout(() => {
        if (preloader && !preloader.classList.contains('loaded')) {
            preloader.classList.add('loaded');
        }
    }, 3000);
}

// ============================================
// Navbar Scroll Effect
// ============================================
function initNavbar() {
    const navbar = document.getElementById('navbar');

    if (!navbar) return;

    let lastScrollY = window.scrollY;
    let ticking = false;

    function updateNavbar() {
        const scrollY = window.scrollY;

        // Add/remove scrolled class
        if (scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }

        lastScrollY = scrollY;
        ticking = false;
    }

    window.addEventListener('scroll', () => {
        if (!ticking) {
            requestAnimationFrame(updateNavbar);
            ticking = true;
        }
    });

    // Initial check
    updateNavbar();
}

// ============================================
// Mobile Navigation
// ============================================
function initMobileNav() {
    const navToggle = document.getElementById('nav-toggle');
    const navMenu = document.getElementById('nav-menu');

    if (!navToggle || !navMenu) return;

    // Toggle menu
    navToggle.addEventListener('click', () => {
        navToggle.classList.toggle('active');
        navMenu.classList.toggle('active');

        // Prevent body scroll when menu is open
        document.body.style.overflow = navMenu.classList.contains('active') ? 'hidden' : '';
    });

    // Close menu when clicking a link
    const navLinks = navMenu.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            navToggle.classList.remove('active');
            navMenu.classList.remove('active');
            document.body.style.overflow = '';
        });
    });

    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
        if (!navMenu.contains(e.target) && !navToggle.contains(e.target)) {
            navToggle.classList.remove('active');
            navMenu.classList.remove('active');
            document.body.style.overflow = '';
        }
    });

    // Close menu on escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && navMenu.classList.contains('active')) {
            navToggle.classList.remove('active');
            navMenu.classList.remove('active');
            document.body.style.overflow = '';
        }
    });
}

// ============================================
// Template Tabs
// ============================================
function initTemplateTabs() {
    const tabs = document.querySelectorAll('.template-tab');
    const panels = document.querySelectorAll('.template-panel');

    if (tabs.length === 0 || panels.length === 0) return;

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetId = tab.dataset.tab;

            // Update active tab
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // Update active panel
            panels.forEach(panel => {
                panel.classList.remove('active');
                if (panel.id === targetId) {
                    panel.classList.add('active');
                }
            });
        });
    });
}

// ============================================
// Counter Animation
// ============================================
function initCounterAnimation() {
    const counters = document.querySelectorAll('[data-count]');

    if (counters.length === 0) return;

    const options = {
        root: null,
        rootMargin: '0px',
        threshold: 0.5
    };

    const animateCounter = (counter) => {
        const target = parseInt(counter.dataset.count, 10);
        const duration = 2000; // 2 seconds
        const start = 0;
        const startTime = performance.now();

        const updateCounter = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);

            // Easing function (ease-out)
            const easeOut = 1 - Math.pow(1 - progress, 3);
            const current = Math.floor(start + (target - start) * easeOut);

            counter.textContent = current + (target >= 100 ? '+' : '');

            if (progress < 1) {
                requestAnimationFrame(updateCounter);
            } else {
                counter.textContent = target + '+';
            }
        };

        requestAnimationFrame(updateCounter);
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }, options);

    counters.forEach(counter => observer.observe(counter));
}

// ============================================
// Scroll Animations (AOS-like)
// ============================================
function initScrollAnimations() {
    const elements = document.querySelectorAll('[data-aos]');

    if (elements.length === 0) return;

    const options = {
        root: null,
        rootMargin: '0px 0px -50px 0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // Get delay from data attribute
                const delay = entry.target.dataset.aosDelay || 0;

                setTimeout(() => {
                    entry.target.classList.add('aos-animate');
                }, parseInt(delay, 10));

                // Optionally unobserve after animation (one-time animation)
                // observer.unobserve(entry.target);
            }
        });
    }, options);

    elements.forEach(element => observer.observe(element));
}

// ============================================
// Smooth Scroll
// ============================================
function initSmoothScroll() {
    const links = document.querySelectorAll('a[href^="#"]');

    links.forEach(link => {
        link.addEventListener('click', (e) => {
            const href = link.getAttribute('href');

            // Skip if it's just "#"
            if (href === '#') return;

            const target = document.querySelector(href);

            if (target) {
                e.preventDefault();

                const navbarHeight = document.getElementById('navbar')?.offsetHeight || 0;
                const targetPosition = target.getBoundingClientRect().top + window.scrollY - navbarHeight - 20;

                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// ============================================
// Utility Functions
// ============================================

/**
 * Debounce function
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in ms
 * @returns {Function}
 */
function debounce(func, wait = 100) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle function
 * @param {Function} func - Function to throttle
 * @param {number} limit - Time limit in ms
 * @returns {Function}
 */
function throttle(func, limit = 100) {
    let inThrottle;
    return function executedFunction(...args) {
        if (!inThrottle) {
            func(...args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// ============================================
// Product/Bundle Selection (Placeholder)
// ============================================
document.querySelectorAll('.product-card .btn, .bundle-cta').forEach(btn => {
    btn.addEventListener('click', (e) => {
        e.preventDefault();

        // Get product info
        const card = btn.closest('.product-card') || btn.closest('.bundle-offer');
        const title = card?.querySelector('.product-title, .bundle-title')?.textContent || 'Product';

        // Placeholder: Show alert (replace with actual checkout logic)
        alert(`Product geselecteerd: ${title}\n\nCheckout integratie komt binnenkort!`);

        // TODO: Integrate with payment provider (Gumroad, Stripe, etc.)
        // window.location.href = `https://yourstore.gumroad.com/l/${productId}`;
    });
});

// ============================================
// Challenge Selection (Placeholder)
// ============================================
document.querySelectorAll('.challenge-card .btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        e.preventDefault();

        const card = btn.closest('.challenge-card');
        const title = card?.querySelector('.challenge-title')?.textContent || 'Challenge';

        // Placeholder: Show alert (replace with Telegram bot link)
        alert(`Challenge: ${title}\n\nJe wordt doorgestuurd naar de Telegram bot...`);

        // TODO: Add actual Telegram bot link
        // window.open('https://t.me/YourBotUsername', '_blank');
    });
});

// ============================================
// Telegram CTA (Placeholder)
// ============================================
document.querySelectorAll('.telegram-cta .btn, .community-cta .btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        e.preventDefault();

        // Placeholder: Show alert (replace with actual Telegram link)
        alert('Je wordt doorgestuurd naar de Telegram community...');

        // TODO: Add actual Telegram community link
        // window.open('https://t.me/YourCommunity', '_blank');
    });
});

// ============================================
// Console Branding
// ============================================
console.log(
    '%c MindVault-AI %c Digital Empire Tools ',
    'background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; padding: 8px 12px; border-radius: 4px 0 0 4px; font-weight: bold;',
    'background: #18181b; color: #a1a1aa; padding: 8px 12px; border-radius: 0 4px 4px 0;'
);
