function expandMenu() {
    var element = document.getElementById("navbarOnTop");
    element.classList.toggle("is-active");
}

// close notification box
document.addEventListener('DOMContentLoaded', () => {
    (document.querySelectorAll('.notification .delete') || []).forEach(($delete) => {
        const $notification = $delete.parentNode;

        $delete.addEventListener('click', () => {
            $notification.parentNode.removeChild($notification);
        });
    });
});