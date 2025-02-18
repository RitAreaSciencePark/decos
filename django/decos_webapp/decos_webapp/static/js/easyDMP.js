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
