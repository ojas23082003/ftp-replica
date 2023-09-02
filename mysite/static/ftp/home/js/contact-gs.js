//This file is made by Praneeth.
//This is dedicated to contact section only.
//Please don't edit.

//Validating email
function Validate_email(email){
    var email_structure = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/;
    if(email.value.length==0 || !email_structure.test(email.value)){
        if(email.value.length==0){
            email.setAttribute("data-msg", "This field cannot be blank");
        }
        else{
            email.setAttribute("data-msg", "Please enter a valid email");
        }
        return false;
    }
    else{
        return true;
    }
}
//Validation for form before submitting
function Validate_form(form){
    // var name = form['Name'];
    // var email = form['Email'];
    // var subject = form['Subject'];
    // var message = form['Message'];
    // if(!Validate_email(email)){
    //     return false;
    // }
    // if(name.value.length<4){
    //     return false;
    // }
    // if(subject.value.length<8){
    //     return false;
    // }
    // if(message.value.length==0){
    //     return false;
    // }
    return true;
}

function success_message(text){
    // var message = document.getElementById('success');
    // message.innerHTML = text;
}

// Variable to hold request
var request;

// Bind to the submit event of our form
$("#form").submit(function(event){
    event.preventDefault();
    success_message("");
    
    if(Validate_form(this)){
        success_message("Sending...");
        // Abort any pending request
        if (request) {
            request.abort();
        }
        // setup some local variables
        var $form = $(this);
        
        // Let's select and cache all the fields
        var $inputs = $form.find("input, textarea");
        
        // Serialize the data in the form
        var serializedData = $form.serialize();
        
        // Let's disable the inputs for the duration of the Ajax request.
        // Note: we disable elements AFTER the form data has been serialized.
        // Disabled form elements will not be serialized.
        $inputs.prop("disabled", true);
    
        // Fire off the request to /form.php
        request = $.ajax({
            url: "https://script.google.com/macros/s/AKfycbwsK_B_htIvKNNxlxa4oqFbKCsfu_JlrRnQZLYllLA4O3EQgp4/exec",
            type: "post",
            data: serializedData
        });
        // Callback handler that will be called on success
        request.done(function (response, textStatus, jqXHR){
            // Log a message to the console
            // console.log("Hooray, it worked!");
            // console.log(response);
            // console.log(textStatus);
            // console.log(jqXHR);
            alert("Your message has been sent. Thank you!");
        });

        // Callback handler that will be called on failure
        request.fail(function (jqXHR, textStatus, errorThrown){
            // Log the error to the console
            console.error(
                "The following error occurred: "+
                textStatus, errorThrown
            );
            alert("Sorry! We encountered an error while sending the message!");
        });

        // Callback handler that will be called regardless
        // if the request failed or succeeded
        request.always(function () {
            // Reenable the inputs
            $inputs.prop("disabled", false);
            window.location.reload();
        });
    }
});