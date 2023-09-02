$(document).ready(function() {
  prep_modal();
});

function prep_modal()
{
  $(".modal").each(function(index, element) {

    var pages = $(element).find('.modal-split');

      if (pages.length != 0)
      {
            pages.hide();
            pages.eq(0).show();

            var form = document.getElementById("modal-form");

            var b_button = document.createElement("button");
                    b_button.setAttribute("type","button");
                        b_button.setAttribute("class","btn btn-primary");
                        b_button.setAttribute("style","display: none;");
                        b_button.innerHTML = "Back";

            var n_button = document.createElement("button");
                    n_button.setAttribute("type","button");
                        n_button.setAttribute("class","btn btn-primary");
                        n_button.innerHTML = "Next";

            var s_button = document.createElement("input");
                    s_button.setAttribute("type","submit");
                        s_button.setAttribute("class","btn btn-primary");
                        s_button.setAttribute("style","display: none;");
                        s_button.innerHTML = "Submit";

            $(element).find('.modal-footer').append(b_button).append(n_button).append(s_button);


            var page_track = 0;

            $(n_button).click(function() {

            element.blur();
            if (page_track == 0) {
                $(b_button).show();
            }

            if (page_track == pages.length - 2) {
                $(n_button).hide();
                $(s_button).show();
            }


            if (page_track < pages.length - 1) {
                page_track++;

                pages.hide();
                pages.eq(page_track).show();
            }
            });

            $(b_button).click(function() {

                if(page_track == 1)
                {
                    $(b_button).hide();
                }
                if(page_track == pages.length-1)
                {
                    $(s_button).hide();
                    $(n_button).show();
                }

                if(page_track > 0)
                {
                    page_track--;

                    pages.hide();
                    pages.eq(page_track).show();
                }
            });

            $(s_button).click(function() {
                if(pages.length > 2) {
                    var Loi = document.getElementById("Loi");
                    if (Loi.value === "") {
                        page_track = 1;
                        pages.hide();
                        pages.eq(page_track).show();
                        $(s_button).hide();
                        $(n_button).show();
                    }
                }
            });

      }

  });
}