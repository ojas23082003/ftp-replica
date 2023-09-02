var temp_file
// Your main starts here
about = document.getElementById("one");
acad = document.getElementById("two");
contact = document.getElementById("three");
about.click();


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

function create_temp(upload){
    if(upload.files.length == 0){
        upload.files = temp_file;
    }
    else{
        temp_file = upload.files;
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
        color_change(cgpa, true, "This field is required");
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
        return validate_empty(contact);
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
        return true;
    }
    else{
        return validate_empty(alt_email);
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
        return validate_empty(rollno);
    }
}
function validateForm(name) {
    var form = document.forms[name];
    var final_form = document.forms["form"];
    a = document.getElementsByTagName("a");

    switch (name){
        case "form1":
            count = 0;
            if ((form["imageUpload"].files.length == 0)||(!validateName(form["imageUpload"], [".png", ".jpg", ".jpeg"]))) {
                if (form["imageUpload"].files.length == 0)
                    color_change(form["imageUpload"], true, "Please upload image");
                count++;
              }
            if (form["fullname"].value == "") {
                color_change(form["fullname"], true, "This field is required");
                count++;
              }
            if(count == 0){
                acad.click();
                final_form.elements.photo.files=form.elements.photo.files;
                final_form.elements.fullname.value=form.elements.fullname.value;
                final_form.elements.gender.value=form.elements.gender.value;
                final_form.elements.passport.value=form.elements.passport.value;

            }
            break;
        case "form2":
            count = 0;
            if (validate_roll(form["rollno"])) {
                //color_change(form["rollno"], true, "This field is required");
                count++;
              }
            if (form["dept"].value == "" && form["dept"].readOnly == false) {
                color_change(form["dept"], true, "This field is required");
                count++;
              }
            if ((form["cv"].files.length == 0)||(!validateName(form["cv"], [".pdf"]))) {
                if (form["cv"].files.length == 0){
                    color_change(form["cv"], true, "CV is not uploaded");
                }
                count++;
              }
            if (form["cgpa"].value == "") {
                color_change(form["cgpa"], true, "This field is required");
                count++;
              }
            if ((form["transcript"].files.length == 0)||(!validateName(form["transcript"], [".pdf"]))) {
                if (form["transcript"].files.length == 0){
                    color_change(form["transcript"], true, "Transcript is not uploaded");
                }
                count++;
              }
            if(count == 0){
                contact.click();
                final_form.elements.rollno.value=form.elements.rollno.value;
                final_form.elements.department.value=form.elements.department.value;
                final_form.elements.cv.files=form.elements.cv.files;
                final_form.elements.year.value=form.elements.year.value;
                final_form.elements.cgpa.value=form.elements.cgpa.value;
                final_form.elements.transcript.files=form.elements.transcript.files;
                final_form.elements.degree_type.value=form.elements.degree_type.value;

              }
            break;
        case "form3":
            count = 0;
            //enters this if contact is not valid
            if (validate_contact(form["contact"])) {
                count++;
              }
            if (validate_email(form["alt_email"])) {
                count++;
              }
            if(count == 0){
                final_form.elements.contact.value=form.elements.contact.value;
                final_form.elements.alt_email.value=form.elements.alt_email.value;
                final_form.submit();
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
            document.getElementById("year").value = 23 - parseInt(rollno.value.trim().slice(0,2));
        }
    }
}