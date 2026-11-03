// Optional interface help only. No JavaScript queue or click handlers.
if (window.jQuery) {
    jQuery(function ($) {
        $('#st_data').trigger('focus');
        $('#queue .peek').hide().fadeIn(1000);
    });
}