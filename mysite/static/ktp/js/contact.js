$('#contact').on("submit", e => {
    e.preventDefault();

    $.ajax({
        url: "https://script.google.com/macros/s/AKfycbwcHbMrzxTGzhQ9Y-y7LtnsYkNyHQ4HvyOVao2xWMeuwviJzwZy8BvpEbGiqbo0J0M/exec",
        type: "post",
        data: jQuery('#contact').serialize(),
        success: res => {
            window.location.reload();
        }
    });
});


// gooogle sheet: https://docs.google.com/spreadsheets/d/1h7mOKp2Npj4uryKWaNXkK8hdDpiMGrYC_B4RGfk0U3I/edit?usp=sharing