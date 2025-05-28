$(document).ready(function() {
    $('.avatar').click(function(e) {
        e.preventDefault();
        $(this).siblings('.dropdown-content').toggle();
    });

    // Close dropdown when clicking outside
    $(document).click(function(e) {
        if (!$(e.target).closest('.dropdown').length) {
            $('.dropdown-content').hide();
        }
    });
});