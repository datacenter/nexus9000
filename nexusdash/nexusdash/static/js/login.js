/* 
 * 
 * Signin Form Button Actions 
 * 
 * 
 */

// Global Objects
var validator = {};	// Jquery Validate global object
var formRules = {};	// form rules global object
var validatorInitializedObj = {};

/* 
 * 
 * Signin Form Submission Validation & AJAX Post 
 * 
 * */
function submitForm(form) {
	// This function submitForm() gets called right after a submit button is clicked
	// Once clicked on button, show a snipper over the button to indicate user that page is loading
	var ladda_spinner = Ladda.create(document.querySelector('#' + $(form).find("button[type=submit]").attr('id')));
	ladda_spinner.start();
	ladda_spinner.setProgress(1);	// Show the spinner
	// Perform action on JSON data retrieved from Backend Server
    $.post('#', $(form).serialize(), function(data){
    	/* This function post() gets called right after the backend post() returns
    	 * the frontend with data.
    	 * 
    	 * This function will perform the task of displaying errors
    	 * reported by backend
    	 * */
    	serverErrs = data.errors;
    	if (serverErrs){
    		// If Client-Side (Front-End) jQuery Validation requirements don't match Server-Side Form Validation requirements,
    		// then Server will send Json data with errors with format: {element_attr_name:error}, e.g: {'password':'Min Length is 7'}.
    		// To fix it, make sure to sync changes by matching Client-Side HTML Element attribute name's value with Server Side Form Attribute
    		serverErrKeys = new Array();
    		serverErrKeysDisplayed = new Array();
    		var i = 0;
    		$.each(serverErrs, function (serverErrKey, serverErrVal) {
    			serverErrKeys[i] = serverErrKey;
    			i = i + 1;
	    		$.each(validator.errors(), function (j, clientErr) {
	    			idOfElem = $(clientErr).attr("for");
	    			clientNameOfElem = $("#" + idOfElem).attr("name")
	    			if (clientNameOfElem == serverErrKey) {
	    				// Display Server-Side Error Message just below the HTML Element with name=clientNameOfElem
	    				$(clientErr).removeClass("valid")
	    				// Update the error label present next to element
	    				var servererr = $(clientErr).text(serverErrVal.join("\n")).text();
	    				$(clientErr).html(servererr.replace(/\n/g, '<br />'));
	    				serverErrKeysDisplayed.push(serverErrKey);
	    				return false;	// Exit out of $.each(validator.errors()... loop
	    			}
	    		});
	    	});
    		serverErrKeysNotDisplayed = $(serverErrKeys).not(serverErrKeysDisplayed).get();
    		startTag = '<div><label class="error">';
    		endTag = '</label></div>';
    		addHtmlForGenericErrs = '';
    		$.each(serverErrKeysNotDisplayed, function (k, m) {
    			var n = $(serverErrs).attr(m).join("\n");
    			addHtmlForGenericErr = startTag + n.replace(/\n/g, '<br />') + endTag;
    			addHtmlForGenericErrs = addHtmlForGenericErrs + addHtmlForGenericErr + '\n';
    		});
    		if (this.data.indexOf('signin_submit_form') > -1) {			// If the form being submitted is a SignIn form
    			$('#signin-form > .login_error').html(addHtmlForGenericErrs);
    		}
    		else {														// Throw Exception
    			console.log('Error!! Not expected. Must refactor!!');
    			setTimeout(function() {window.location = "/500/1";}, 0);
    		}
       }
       else {
    	   // If Errors not seen in HTTP Response from Server, then
    	   if (this.data.indexOf('signin_submit_form') > -1) {
	    	   // For Signin, redirect to device's dashboard
	    	   if (data.hostname) {
	    		   setTimeout(function() {window.location = "/" + data.hostname + '/dash/';}, 0);
	    	   }
	    	   else {
	    		   setTimeout(function() {window.location = "/500/2";}, 0);
	    	   }
    	   }
       }
    	ladda_spinner.stop();
    })//End post
    return false;
}

/*
 * 
 * Define Validation Rules for signin
 * 
*/
// Overriding Valid URL to include telnet, ssh and allow hostname
//// http://stackoverflow.com/a/14277830/558397
//// Basic validation is done here. Actual validation is done in backend
jQuery.validator.methods.url = function(value, element) {
    return this.optional(element) || true;
};
jQuery.validator.addMethod("url",function(value,element) {
  return this.optional(element) 
     || /^((https|http|ssh|telnet):\/\/)?([\da-z\.-:_]+)([\/\w \.-]*)*\/?$/.test(value); 
},"Please enter a valid URL");

$(document).ready(function(){
	// Validate
	// http://bassistance.de/jquery-plugins/jquery-plugin-validation/
	// http://docs.jquery.com/Plugins/Validation/
	// http://docs.jquery.com/Plugins/Validation/validate#toptions
	
	validatorInitializedObj = { // initialize form validation on form
        // rules & other options
		rules: {
        	  // password and login are the names of element (e.i attr name)
        	  password: {
    			minlength: 3,
    			required: true
    		  },
    		  username: {
    		  		minlength: 3,
    				required: true,
    		  },
    		  url: {
    				required: true,
    				url: true
    		  }
    		},
		
		submitHandler: function(form) {
			// When submit button is clicked, this function gets called
			submitForm(form);
			},
			
		highlight: function(element) {
			// Display Error
			$(element).closest('.control-group').removeClass('has-success').addClass('has-error');
			this.toHide.remove();
		},
			
		success: function(label) {
			// Display Success
			label
			.closest('.control-group').removeClass('has-error').addClass('has-success');
			},
				
		// http://icanmakethiswork.blogspot.co.uk/2013/08/using-bootstrap-tooltips-to-display.html
		showErrors: function(errorMap, errorList) {
			// Clean up any tooltips for valid elements
			$.each(this.validElements(), function (index, element) {
				var $element = $(element);
				$element.data("title", ""); // Clear the title - there is no error associated anymore
				$element.tooltip("destroy");
			});
			
			// Create new tooltips for invalid elements
			$.each(errorList, function (index, error) {
				var $element = $(error.element);
				$element.tooltip("destroy"); // Destroy any pre-existing tooltip so we can repopulate with new tooltip content
				$element.data("title", error.message);
				$element.tooltip({placement: 'right'}); // Create a new tooltip based on the error messsage we just set in the title
			});
			this.defaultShowErrors();
		},
			
		errorPlacement: function(label, element) {
			label.insertAfter(element); // default error placement
			label.text('');				// Remove any text from label
			$(label).attr('style',"display: block;");	// Remove any existing style and default to display: block
		},
		
	  };
    validator = $("#signin-form").validate(validatorInitializedObj);
    
}); // end document.ready