// static/js/navigation.js
export function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const tabPanes = document.querySelectorAll('.tab-pane');

    // Initialize: set the initially active tab as visible
    const initialActive = document.querySelector('.tab-pane.active');
    if (initialActive) {
        initialActive.classList.add('tab-visible');
    }

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const targetTab = item.getAttribute('data-tab');

            // Prevent re-clicking the same tab
            if (item.classList.contains('active')) return;

            const currentActive = document.querySelector('.tab-pane.active');
            const targetPane = document.getElementById(targetTab);

            // Fade out current tab
            if (currentActive) {
                currentActive.classList.remove('tab-visible');
            }

            // Update nav active state
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');

            // After a short delay, switch tabs and fade in the new one
            setTimeout(() => {
                if (currentActive) {
                    currentActive.classList.remove('active');
                }
                if (targetPane) {
                    targetPane.classList.add('active');
                    // Trigger reflow so the transition picks up
                    void targetPane.offsetWidth;
                    requestAnimationFrame(() => {
                        targetPane.classList.add('tab-visible');
                    });
                }
            }, 180);
        });
    });
}