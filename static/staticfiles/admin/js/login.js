document.addEventListener('DOMContentLoaded', function() {
    console.log('GSAP animation is running');
    
    if (typeof gsap !== 'undefined') {
        gsap.from('.login-container', {
           // duration: 1,
           // y: -50,
           // opacity: 0,
           // ease: 'power2.out'
        });
    } else {
        console.warn('GSAP is not loaded');
    }
});
