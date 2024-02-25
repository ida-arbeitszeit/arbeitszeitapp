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


// modals: see https://bulma.io/documentation/components/modal
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
  
    // Add a click event on buttons to open a specific modal
    (document.querySelectorAll('.js-modal-trigger') || []).forEach(($trigger) => {
      const modal = $trigger.dataset.target;
      const $target = document.getElementById(modal);
  
      $trigger.addEventListener('click', () => {
        openElement($target);
      });
    });
  
    // Add a click event on various child elements to close the parent modal
    (document.querySelectorAll('.modal-background, .modal-close, .modal-card-head .delete, .modal-card-foot .button') || []).forEach(($close) => {
      const $target = $close.closest('.modal');
  
      $close.addEventListener('click', () => {
        closeElement($target);
      });
    });
  
    // Add a keyboard event to close all modals
    document.addEventListener('keydown', (event) => {
      const e = event || window.event;
  
      if (e.keyCode === 27) { // Escape key
        closeAllElementsByClassName('.modal');
      }
    });

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

  function copyTextToClipboard(text) {
    navigator.clipboard.writeText(text);
  }

  function changeElementIconToCheckIcon(elementId) {
    let element = document.getElementById(elementId); 
    element.classList.toggle("fa-check");
  }
