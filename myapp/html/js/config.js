$(document).ready(function() {
    // Get the current config from the server and populate the form
    $.get("/api/config", function(data) {
        $("#localization").prop('checked', data.LOCALIZATION);
        $("#plex_host").val(data.PLEX_HOST);
        $("#plex_port").val(data.PLEX_PORT);
        $("#plex_token").val(data.PLEX_TOKEN);
    });

    // When the form is submitted, send the new config to the server
    $("#config-form").submit(function(event) {
        event.preventDefault();

        const config = {
            LOCALIZATION: $("#localization").is(':checked'),
            PLEX_HOST: $("#plex_host").val(),
            PLEX_PORT: parseInt($("#plex_port").val()),
            PLEX_TOKEN: $("#plex_token").val()
        };

        $.ajax({
            url: "/api/config",
            type: 'PUT',
            data: JSON.stringify(config),
            contentType: 'application/json; charset=utf-8',
            success: function(result) {
                alert('Config updated successfully!');
            }
        });
    });
});
