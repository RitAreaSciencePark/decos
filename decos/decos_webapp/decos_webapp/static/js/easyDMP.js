$(document).one('submit','#refresh_form',function(e){
    e.preventDefault();
    $("#refresh_btn").prop("disabled",true);;
    setTimeout(() => {
        $('#refresh_form').submit();
    }, 1000);
});

function handleRowClick(inputId, recordId, formId) {
    $('#' + inputId).val(recordId);
    $('#' + formId).submit();
};

document.addEventListener('DOMContentLoaded', function () {
    const dropdowns = document.querySelectorAll('.dropdown');

    dropdowns.forEach(function (dropdown) {
        let timeout;

        dropdown.addEventListener('mouseenter', function () {
            clearTimeout(timeout);
            const toggle = dropdown.querySelector('[data-bs-toggle="dropdown"]');
            const instance = bootstrap.Dropdown.getOrCreateInstance(toggle);
            instance.show();
        });

        dropdown.addEventListener('mouseleave', function () {
            timeout = setTimeout(function () {
                const toggle = dropdown.querySelector('[data-bs-toggle="dropdown"]');
                const instance = bootstrap.Dropdown.getOrCreateInstance(toggle);
                instance.hide();
            }, 200); // Delay before closing (optional)
        });
    });
});

document.addEventListener('DOMContentLoaded', function () {
    // Attach event listeners to all elab buttons
    document.querySelectorAll('.elab-btn').forEach(function (button) {
        button.addEventListener('click', function (e) {
            e.preventDefault(); // prevent default form submission

            const form = button.closest('.elab-form');
            if (!form) return;

            form.submit();

            setTimeout(() => {
                const elab_url_input = document.getElementById("elab_url");
                if (elab_url_input && elab_url_input.value) {
                    window.open(elab_url_input.value, '_blank');
                }
            }, 1000);
        });
    });

    function getCSRFToken() {
        const name = 'csrftoken';
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                return decodeURIComponent(cookie.substring(name.length + 1));
            }
        }
        return '';
    }
});

document.addEventListener("DOMContentLoaded", function () {
  const scrollTo = document.body.dataset.scrollTo;
  if (scrollTo) {
    window.location.hash = scrollTo; // triggers instant jump
  }
});

// DMP Page requirements
document.addEventListener("DOMContentLoaded", function () {
  const requiredFields = [
    "experiment_title",
    "principal_investigator",
    "plan_creation_date",
    "affiliated_institutions"
  ];

  requiredFields.forEach(function (fieldName) {
    const field = document.querySelector(`[name="${fieldName}"]`);
    if (field) {
      field.setAttribute("required", "required");

      // Add a red asterisk after the label (i tag in your case)
      const label = field.previousElementSibling;
      if (label && label.tagName.toLowerCase() === 'i') {
        label.innerHTML += ' <span style="color: red;">*</span>';
      }
    }
  });
});

// Results Page - Experiment DMP selection (adapted)
document.addEventListener('DOMContentLoaded', function () {
  const table = document.querySelector('#experiment_dmp_selection');
  const hiddenInput = document.getElementById('experiment_dmp_id_hidden');
  const form = document.getElementById('experiment_dmp_selection');

  if (!table || !hiddenInput || !form) return;

  table.querySelectorAll('tbody tr').forEach(row => {
    row.addEventListener('click', () => {
      const recordId = row.dataset.recordId || row.querySelector('td')?.textContent?.trim();
      if (recordId) {
        hiddenInput.value = recordId;
        form.submit();
      }
    });
  });
});

document.addEventListener("DOMContentLoaded", function () {
  const labSelect = document.querySelector("select[name*='laboratory']");
  const fieldsToShow = ["elab_token", "jenkins_token", "minio_acces_key", "minio_secret_key"];

  function toggleSensitiveFields(show) {
    fieldsToShow.forEach(fieldName => {
      const fieldDiv = document.getElementById(`field-${fieldName}`);
      if (fieldDiv) {
        fieldDiv.style.display = show ? "block" : "none";
      }
    });
  }

  if (labSelect) {
    toggleSensitiveFields(!!labSelect.value);
    labSelect.addEventListener("change", () => {
      toggleSensitiveFields(!!labSelect.value);
    });
  }
});
