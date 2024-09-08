document.addEventListener('DOMContentLoaded', () => {
    setupCopyToggles();
});

function setupCopyToggles() {
    document.querySelectorAll('[data-type="copy-toggle"]').forEach(el => {
        const input = el.querySelector("input");
        const iconContainer = el.querySelector("span");
        const template = el.querySelector("template").content;
        const copyIcon = iconContainer.querySelector("svg");
        const checkIcon = template.querySelector("svg").cloneNode(true);
        let timeoutId;

        el.addEventListener('mousedown', () => {
            navigator.clipboard.writeText(input.value);
            if (iconContainer.contains(copyIcon)) {          
                iconContainer.replaceChild(checkIcon, copyIcon);
            }
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => {
                iconContainer.replaceChild(copyIcon, checkIcon)
            }, 1000);
        });
    });
}
