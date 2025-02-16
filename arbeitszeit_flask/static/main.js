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

// toggle password visibility
document.addEventListener('DOMContentLoaded', () => {
  $eye = document.getElementById("eye");
  $eyeSlashed = document.getElementById("eye-slashed");
  $pwInput = document.getElementById("password");
  $eyeRepeat = document.getElementById("eye-repeat");
  $eyeSlashedRepeat = document.getElementById("eye-slashed-repeat");
  $pwInputRepeated = document.getElementById("repeat_password");
    $eye.addEventListener('click', () => {
      $eye.classList.add("is-hidden")
      $eyeSlashed.classList.remove("is-hidden")
      $pwInput.type = 'text'
    });
    $eyeSlashed.addEventListener('click', () => {
      $eyeSlashed.classList.add("is-hidden")
      $eye.classList.remove("is-hidden")
      $pwInput.type = 'password'
    });
    $eyeRepeat.addEventListener('click', () => {
      $eyeRepeat.classList.add("is-hidden")
      $eyeSlashedRepeat.classList.remove("is-hidden")
      $pwInputRepeated.type = 'text'
    });
    $eyeSlashedRepeat.addEventListener('click', () => {
      $eyeSlashedRepeat.classList.add("is-hidden")
      $eyeRepeat.classList.remove("is-hidden")
      $pwInputRepeated.type = 'password'
    });
  });
