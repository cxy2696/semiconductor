/* Front-end enhancement layer for responsive UX */
(function () {
    function setDeviceClass() {
        const width = window.innerWidth || document.documentElement.clientWidth || 0;
        const body = document.body;
        if (!body) return;
        body.classList.remove('device-mobile', 'device-tablet', 'device-desktop');
        if (width < 768) body.classList.add('device-mobile');
        else if (width < 1100) body.classList.add('device-tablet');
        else body.classList.add('device-desktop');
    }

    function setViewportHeightVar() {
        const vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
    }

    function enhanceToolbarScroll() {
        const primary = document.getElementById('toolbar_primary');
        if (!primary) return;
        if (window.innerWidth > 900) {
            primary.style.overflowX = '';
            primary.style.paddingBottom = '';
            return;
        }
        primary.style.overflowX = 'auto';
        primary.style.paddingBottom = '4px';
    }

    function improveTouchTargets() {
        if (window.innerWidth > 768) return;
        document.querySelectorAll('button, select, input').forEach(el => {
            const current = Number(window.getComputedStyle(el).minHeight.replace('px', '')) || 0;
            if (current < 38) {
                el.style.minHeight = '38px';
            }
        });
    }

    function onResize() {
        setDeviceClass();
        setViewportHeightVar();
        enhanceToolbarScroll();
        improveTouchTargets();
    }

    function bootstrap() {
        onResize();
        window.addEventListener('resize', onResize, { passive: true });
        window.addEventListener('orientationchange', onResize, { passive: true });
    }

    window.SemiconductorFrontendApp = { bootstrap };
})();
