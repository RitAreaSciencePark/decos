$(document).one('submit','#refresh_form',function(e){
    e.preventDefault();
    $("#refresh_btn").prop("disabled",true);;
    setTimeout(() => {
        $('#refresh_form').submit();
    }, 1000);
});

<<<<<<< HEAD
=======
function handleRowClick(inputId, recordId, formId) {
    $('#' + inputId).val(recordId);
    $('#' + formId).submit();
};
>>>>>>> 7ba91e444ffe63cfd5e63a511123d609b24f16f1
