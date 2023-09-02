(function ($)
  { "use strict"

	    $(window).on('load', function () {
	      $('#preloader-active').delay(450).fadeOut('slow');
	      $('body').delay(450).css({
	        'overflow-x': 'hidden'
	      });
	    });
	    
})(jQuery);