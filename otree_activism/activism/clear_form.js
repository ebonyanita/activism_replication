// OTAI SECTION: header

// Clears any prefilled form values on page load so each decision starts blank.
// oTree re-renders a field's stored value when a page is shown again
// (browser refresh / back button / returning from a wait page); for this
// experiment every round's choice must be made fresh, so we wipe the inputs.


// OTAI SECTION: functions

function clearFormFields() {
  var form = document.querySelector('form');
  if (!form) return;
  form.setAttribute('autocomplete', 'off');
  var fields = form.querySelectorAll('input, select, textarea');
  fields.forEach(function (el) {
    var type = (el.type || '').toLowerCase();
    if (type === 'radio' || type === 'checkbox') {
      el.checked = false;
    } else if (type === 'hidden' || type === 'submit' || type === 'button') {
      // leave oTree's hidden fields and buttons untouched
    } else if (el.tagName.toLowerCase() === 'select') {
      el.selectedIndex = -1;
    } else {
      el.value = '';
    }
  });
}


// OTAI SECTION: footer

clearFormFields();
