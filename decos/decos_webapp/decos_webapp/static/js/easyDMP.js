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

