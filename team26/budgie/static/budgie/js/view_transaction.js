$(document).ready(function(){

  if ($("#id_account_type").val() == 'All') {
    $('#id_account_numbers').empty;
    $('#id_account_numbers').prop('disabled', true );
  } 

  else {
    $('#id_account_numbers').prop('disabled', false ); 
   }


  $("#id_account_type").change(function() {
    
    if ($(this).val() == 'All') {
       $('#id_account_numbers').empty;
       $('#id_account_numbers').val('');
       $("#id_account_numbers").attr('disabled', true);
    }

    else { //if another account type  is selected besides All
       $('#id account_numbers').prop('disabled', false );
       var account_type = $("#id_account_type").val()
       var url = "/budgie/get_accounts/" + account_type
       $.get(url, function(response) {
          $("#accounts").empty();
          $("#accounts").html(response);
        });
    }

  }); 


  $("#display").click(function() {
      event.preventDefault();
  
       var account_type = $("#id_account_type").val();
       var account_number = $("#id_account_numbers").val();
       var time_options = $("#id_time_options").val();

       var url = "/budgie/get_transactions/" + account_type + "/" + account_number + "/" + time_options; 

       $.get(url, function(response) {
          $("#transactions").empty();
          $("#transactions").html(response);
      });
    
  }); 


}); //End of 

