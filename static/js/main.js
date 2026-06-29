
document.addEventListener('DOMContentLoaded', function() {
    console.log('CuberX website loaded');
    
    const animateElements = document.querySelectorAll('.animate-on-scroll');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-in-up');
                observer.unobserve(entry.target);
            }
        });
    });
    
    animateElements.forEach(el => observer.observe(el));
});