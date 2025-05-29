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

            fetch(form.action, {
                method: 'POST',
                body: new FormData(form),
                headers: {
                    'X-CSRFToken': getCSRFToken()
                }
            }).then(response => {
                setTimeout(() => {
                    window.location.href = 'https://prp-electronic-lab.areasciencepark.it/experiments.php';
                }, 1000); // 1s delay
            });
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
