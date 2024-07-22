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


document.addEventListener('DOMContentLoaded', () => {
    // Functions to open and close an element
    function openElement($el) {
      $el.classList.add('is-active');
    }

    function closeElement($el) {
      $el.classList.remove('is-active');
    }
  
    function closeAllElementsByClassName($className) {
      (document.querySelectorAll($className) || []).forEach(($elem) => {
        closeElement($elem);
      });
    }

    document.addEventListener('click', function() {
      closeAllElementsByClassName('.dropdown');
    });

    (document.querySelectorAll('.dropdown') || []).forEach(($dropdown) => {
      $dropdown.addEventListener('click', function(event) {
        event.stopPropagation();
        $isOpen = $dropdown.classList.contains('is-active')
        closeAllElementsByClassName('.dropdown')
        if (!$isOpen) {
          openElement($dropdown);
        }
      });
    });

  });
