function readURL(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function(e) {
            $('#imagePreview').css('background-image', 'url('+e.target.result +')');
            $('#imagePreview').hide();
            $('#imagePreview').fadeIn(650);
        }
        reader.readAsDataURL(input.files[0]);
    }
}
$("#imageUpload").change(function() {
    readURL(this);
});


// When the user clicks on div, open the popup for transcript
function myFunction() {
  var popup = document.getElementById("myPopup");
  popup.classList.toggle("show");
}

// Returns true if the given extension matches filename extension
function validateName(input, extensions){
    var i = input.files[0].name.lastIndexOf('.');
    var ext = input.files[0].name.slice(i).toLowerCase();
    if (extensions.includes(ext)){
        return true;
    }
    else{
        color_change(input, true, "This file type is not allowed");
        return false;
    }
}



//Previous button listener
function previous(to){
    switch(to){
        case 'one':
            about.click();
            break;
        case 'two':
            acad.click();
            break;
    }
}


function validate_cgpa(cgpa){
    // cgpa validation
    var val = parseFloat(cgpa.value);
    if(val > 10){
        window.alert('CGPA cannot be greater than 10!');
        cgpa.value = 10;
    }
    else if(val < 0){
        window.alert('CGPA cannot be less than 0!');
        cgpa.value = 0;
    }
    else if(cgpa.value.trim(" ")==""){
        //color_change(cgpa, true, "This field is required");
    }
    else{
        color_change(cgpa, false)
    }
}

//mobile number validation
function validate_contact(contact){
    var number = contact.value;
    //Valid for any number with one trailing zero or
    //starts with 6/7/8/9 and has 10 digits
    var structure = /^[0]?[6789]\d{9}$/;
    if (number.trim(" ")!="" && !structure.test(number))
    {  
        //contact.value = "";
        //contact.placeholder="";
        color_change(contact, true, "Your Mobile Number Is Not Valid");
        return true;
    }
    else{
        return false;
    }
}

//email validation
function validate_email(alt_email){
    var email = alt_email.value;
    //Valid for any number with one trailing zero or
    //starts with 6/7/8/9 and has 10 digits
    var structure = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;
    if (email.trim(" ")!="" && !structure.test(email))
    {  
        //contact.value = "";
        //contact.placeholder="";
        color_change(alt_email, true, "Please enter a valid email address");
        email = "";
        return true;
    }
    else{
        return false;
    }
}

//returns true if not valid
function validate_roll(rollno){
    rollno.value = rollno.value.trim(" ");
    roll = rollno.value;

    var structure = /^\d{2}\w{2}\d..\d{2}$/;
    if (roll!="" && !structure.test(roll)){
        rollno.value="";
        rollno.placeholder="";
        color_change(rollno, true, "Invalid roll number");
        return true
    }
    else{
        validate_empty(rollno);
    }
}
function validateForm(name) {
    var form1 = document.forms["form1"];
    var form2 = document.forms["form2"];
    var form3 = document.forms["form3"];
    var final_form = document.forms["form"];

    switch (name){
        case "form1":
            acad.click();
            break;
        case "form2":
            count = 0;
            if (validate_roll(form2["rollno"])) {
                //color_change(form["rollno"], true, "This field is required");
                count++;
              }
            if (form2["dept"].value == "" && form2["dept"].readOnly == false) {
                color_change(form2["dept"], true, "This field is required");
                count++;
              }
            if (form2["cv"] && ((form2["cv"].files.length == 0)||(!validateName(form2["cv"], [".pdf"])))) {
                if (form2["cv"] && form2["cv"].files.length == 0){
                    color_change(form2["cv"], true, "CV is not uploaded");
                }
                count++;
              }
            if (form2["cgpa"].value == "") {
                color_change(form2["cgpa"], true, "This field is required");
                count++;
              }
            if (form2["transcript"] &&(( form2["transcript"].files.length == 0)||(!validateName(form2["transcript"], [".pdf"])))) {
                if (form2["transcript"] && form2["transcript"].files.length == 0){
                    color_change(form2["transcript"], true, "Transcript is not uploaded");
                }
                count++;
              }
            if(count == 0){
                contact.click();
              }
            break;
        case "form3":
            count = 0;
            //enters this if contact is not valid
              if(form1["imageUpload"].files.length != 0){
                if (!validateName(form1["imageUpload"], [".png", ".jpg", ".jpeg"])) {
                    count++;
                  }
              }
            if(form2["cv"] && form2["cv"].files.length != 0){
                if (!validateName(form2["cv"], [".pdf"])) {
                    count++;
                  }
              }
            if(form2["transcript"] && form2["transcript"].files.length != 0){
                if (!validateName(form2["transcript"], [".pdf"])) {
                count++;
               }
            }
            
            if (validate_contact(form3["contact"])) {
                count++;
              }
            if (validate_email(form3["alt_email"])) {
                count++;
              }
            if(count == 0){
                if(form1.elements.image.files.length!=0){
                    final_form.elements.photo.files=form1.elements.image.files;
                }
                if(form1.elements.fullname.value){
                    final_form.elements.fullname.value=form1.elements.fullname.value;
                }
                if(form1.elements.gender.value){
                    final_form.elements.gender.value=form1.elements.gender.value;
                }
                if(form1.elements.passport.value){
                    final_form.elements.passport.value=form1.elements.passport.value;
                }
                if(form2.elements.rollno.value){
                    final_form.elements.rollno.value=form2.elements.rollno.value;
                }
                if(form2.elements.department.value){
                    final_form.elements.department.value=form2.elements.department.value;
                }
                if(form2.elements.cv && form2.elements.cv.files) {
                    final_form.elements.cv.files = form2.elements.cv.files;
                }
                if(form2.elements.year.value){
                    final_form.elements.year.value=form2.elements.year.value;
                }
                if(form2.elements.cgpa.value){
                    final_form.elements.cgpa.value=form2.elements.cgpa.value;
                }
                if(form2.elements.transcript && form2.elements.transcript.files) {
                    final_form.elements.transcript.files = form2.elements.transcript.files;
                }
                if(form3.elements.contact.value){
                    final_form.elements.contact.value=form3.elements.contact.value;
                }
                if(form3.elements.alt_email.value){
                    final_form.elements.alt_email.value=form3.elements.alt_email.value;
                }
                //if(confirm("Empty fields won't be updated")){
                    final_form.submit();
                //}
                //else{
                //    break;
                //}
              }
            else{
                alert("One or more input fields are not valid.")
            }
              break;
        default:
            break;

    }
  }


// Dependencies
function validate_empty(field){
    if (field.value.trim()==""){
        color_change(field, true, "This field is required");
        return true;
    }
    else{
        color_change(field, false);
        return false;
    }
}
function color_change(field, error, message=""){
    if(error){
        field.style.backgroundColor="rgba(255, 0, 0, 0.1)";
        field.style.border="1px solid red";
    }
    else{
        field.style.backgroundColor="#f8f8f8";
        field.style="border:focus{1px solid orange}";
    }
    document.getElementById(field.id+"_req").innerHTML = message;
}

// Updating year and department according to roll number
function autoupdate(rollno){
    var dept_field = document.getElementById("dept");
    var deps = {
        'AE': 'Aerospace Engineering',
        'AG': 'Agricultural and Food Engineering',
        'AR': 'Architecture and Regional Planning',
        'BT': 'Biotechnology',
        'CH': 'Chemical Engineering',
        'CY': 'Chemistry',
        'CE': 'Civil Engineering',
        'CS': 'Computer Science and Engineering',
        'EE': 'Electrical Engineering',
        'EC': 'Electronics and Electrical Communication Engg.',
        'EX': 'Exploration Geophysics',
        'GG': 'Geology and Geophysics',
        'HS': 'Humanities and Social Sciences',
        'IM': 'Industrial and Systems Engineering',
        'IE': 'Instrumentation Engineering',
        'QE': 'Quality Engg Design and Manufacturing(Industrial Electronics Vertical)',
        'QM': 'Quality Engg Design and Manufacturing(Mechanical Engineering Vertical)',
        'MF': 'Manufacturing Science and Engg',
        'MA': 'Mathematics',
        'ME': 'Mechanical Engineering',
        'MT': 'Metallurgical and Materials Engineering',
        'MI': 'Mining Engineering',
        'NA': 'Ocean Engg and Naval Architecture',
        'PH': 'Physics'
    };
    if(validate_empty(rollno)){
        dept_field.readOnly = true;
        dept_field.value = "";
        document.getElementById("year").value = "";
    }
    else{
        var dept = deps[rollno.value.trim().slice(2, 4).toUpperCase()];
        if(dept!=undefined && rollno.value.length>=4){
            dept_field.readOnly = true;
            dept_field.value = dept;
            color_change(dept_field, false)
        }
        else if(rollno.value.length>=4){
            dept_field.readOnly = false;
            dept_field.value = "";
        }
        if(rollno.value.length>=2){
            document.getElementById("year").value = 21 - parseInt(rollno.value.trim().slice(0,2));
        }
    }
}

// Your main starts here
about = document.getElementById("one");
acad = document.getElementById("two");
contact = document.getElementById("three");
about.click();