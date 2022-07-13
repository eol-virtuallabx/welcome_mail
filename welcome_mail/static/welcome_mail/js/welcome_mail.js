function set_welcome_mail_view(){
  let welcome_data = JSON.parse($('#welcome_mail_data').val());
  let iframe = document.getElementById("mce_0_ifr");
  let elmnt = iframe.contentWindow.document.getElementById("tinymce");
  if (isEmpty(welcome_data)){
    $('#is_active')[0].checked = false;
    $('#id_welcome_subject')[0].value = '';
    elmnt.innerHTML = '';
  }
  else{
    $('#is_active')[0].checked = welcome_data.is_active;
    $('#id_welcome_subject')[0].value = welcome_data.subject;
    elmnt.innerHTML = welcome_data.message;
  }
  $('#request-response').hide();
  $('.eol_send_email_hide').hide();
  $('.eol_welcome_mail_hide').show();
  $('#request-response-error')[0].innerHTML = '';
  $('#request-response')[0].innerHTML = '';
  if($('#is_active')[0].checked){
    $('.eol_welcome_mail_checkbox_hide').show();
  }
  else{
    $('.eol_welcome_mail_checkbox_hide').hide();
  }
}
function set_send_email_view(){
  let iframe = document.getElementById("mce_0_ifr");
  let elmnt = iframe.contentWindow.document.getElementById("tinymce");
  elmnt.innerHTML = '';
  $('#request-response').hide();
  $('.eol_send_email_hide').show();
  $('.eol_welcome_mail_hide').hide();
  $('.eol_welcome_mail_checkbox_hide').show();
  $('#request-response-error')[0].innerHTML = '';
  $('#request-response')[0].innerHTML = '';
}
function isEmpty(obj) {
  return Object.keys(obj).length === 0;
}
function checkbox_welcome_mail(e){
  if(e.checked){
    $('.eol_welcome_mail_checkbox_hide').show();
  }
  else{
    $('.eol_welcome_mail_checkbox_hide').hide();
  }
}
function save_welcome_mail(e){
  $('#request-response').hide();
  $('#request-response-error')[0].innerHTML = '';
  let is_active = $('#is_active')[0].checked;
  let iframe = document.getElementById("mce_0_ifr");
  let elmnt = iframe.contentWindow.document.getElementById("tinymce");
  let welcome_message = elmnt.innerHTML;
  let welcome_subject = $('#id_welcome_subject').val();
  if(elmnt.innerText == '' || elmnt.innerText == '\n' || welcome_subject == ''){
    $('#request-response-error')[0].innerHTML = 'ERROR. El asunto o el cuerpo del mensaje estan vacio';
    alert('ERROR. El asunto o el cuerpo del mensaje estan vacio');
    $('#request-response-error').show();
  }
  else{
    let data = {
      'is_active': is_active,
      'welcome_message': welcome_message,
      'welcome_subject': welcome_subject,
    }
    $.ajax({
        url: e.dataset.endpoint,
        dataType: 'json',
        type: "POST",
        data: data,
        xhrFields: {
            withCredentials: true
        },
        success: function(response){
          if(response.result == 'success'){
            $('#request-response')[0].innerHTML = 'Correo guardado Correctamente';
            $('#request-response').show();
            let new_data = {
              'is_active': is_active,
              'message': welcome_message,
              'subject': welcome_subject,
            }
            $('#welcome_mail_data')[0].value = JSON.stringify(new_data)
          }
          else{
            $('#request-response-error')[0].innerHTML = "Error inesperado ha ocurrido. Actualice la página e intente nuevamente";
            $('#request-response-error').show();
          }
        },
        error: function() {
          alert("Error inesperado ha ocurrido. Actualice la página e intente nuevamente");
          $('#request-response-error')[0].innerHTML = "Error inesperado ha ocurrido. Actualice la página e intente nuevamente";
          $('#request-response-error').show();
        }
    });
  }
}