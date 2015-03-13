$(document).ready(function(){

var data_length = $( "#accounts td" ).length;

for (var i = 0; i < data_length; i++ ) {
	var account_balance = $('#account_balance_'+i).text();

	var goal_balance = $('#goal_balance_'+i).text();

	account_balance = parseInt(account_balance.substr(1));

	goal_balance = parseInt(goal_balance.substr(1)); 
	
	//When the balance in the account is greater than the balance expected in the goal
    if (account_balance >= goal_balance)  {
    	$('#goal_balance_'+i).css("font-weight","bold");
        $('#account_balance_'+i).css("font-weight","bold");
        $('#account_balance_'+i).css("color", "green");
        $('#goal_balance_'+i).css("color", "green");
    	
    }

    //When the balance in the account is less than the balance expected in the goal
   if (account_balance < goal_balance)  {
    	$('#account_balance_'+i).css("color", "red");
    	$('#goal_balance_'+i).css("color", "red");
        $('#goal_balance_'+i).css("font-weight","bold");
        $('#account_balance_'+i).css("font-weight","bold");
    	

    }
}



}); //End of 
