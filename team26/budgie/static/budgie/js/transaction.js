$(document).ready(function() {

//When loading the page, change the to_account, from_account and category field depending on the  selected transaction_type

  var tr_type = $("#id_transaction_type option:selected").text(); 
  
    if (tr_type == 'Income') {
      $("#id_to_account").show();
      $('label[for="id_to_account"]').show();
      $("#id_from_account").hide();
      $('label[for="id_from_account"]').hide();
      $("#id_category").show();
      $('label[for="id_category"]').show();

      $('#id_category')
        .empty()
        .append('<option selected="selected" value="SAL">Salary</option>')
        .append('<option value="GFT">Gift</option>') ;   
   }


    else if (tr_type == 'Expense') {
      $("#id_from_account").show();
      $('label[for="id_from_account"]').show();
      $("#id_to_account").hide();
      $('label[for="id_to_account"]').hide();
      $("#id_category").show();
      $('label[for="id_category"]').show();
         $('#id_category')
        .empty()
        .append('<option selected="selected" value="HOU">Housing</option>')
        .append('<option value="TRA">Transportation</option>') 
        .append('<option value="FOO">Food</option>')
        .append('<option value="EDU">Education</option>') 
        .append('<option value="HEA">Health</option>')
        .append('<option value="ENT">Entertainment</option>')
        .append('<option value="UTL">Utilities</option>') ;    
   
   } 
  
  else { 
      $("#id_to_account").show();
      $('label[for="id_to_account"]').show();
      $("#id_from_account").show();
      $('label[for="id_from_account"]').show();
      $("#id_category").hide();
      $('label[for="id_category"]').hide();
  }


//Behavior when changing the options: 
  $("#id_transaction_type").change(function() {
  if ($("#id_transaction_type").val() == 'CR') {
    $("#id_to_account").show();
    $('label[for="id_to_account"]').show();
    $("#id_from_account").hide();
    $('label[for="id_from_account"]').hide();
    $("#id_category").show();
    $('label[for="id_category"]').show();

    $('#id_category')
      .empty()
      .append('<option selected="selected" value="SAL">Salary</option>')
      .append('<option value="GFT">Gift</option>') ;   
   }


  else if ($("#id_transaction_type").val() == 'DR') {
    $("#id_from_account").show();
    $('label[for="id_from_account"]').show();
    $("#id_to_account").hide();
    $('label[for="id_to_account"]').hide();
    $("#id_category").show();
    $('label[for="id_category"]').show();
       $('#id_category')
      .empty()
      .append('<option selected="selected" value="HOU">Housing</option>')
      .append('<option value="TRA">Transportation</option>') 
      .append('<option value="FOO">Food</option>')
      .append('<option value="EDU">Education</option>') 
      .append('<option value="HEA">Health</option>')
      .append('<option value="ENT">Entertainment</option>')
      .append('<option value="UTL">Utilities</option>') ;    
   
   } 
  
  else { 
    $("#id_to_account").show();
    $('label[for="id_to_account"]').show();
    $("#id_from_account").show();
    $('label[for="id_from_account"]').show();
    $("#id_category").hide();
    $('label[for="id_category"]').hide();
       }
  });


});