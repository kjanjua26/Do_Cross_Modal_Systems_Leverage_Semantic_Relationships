$(function() {
    $("#customFile").on("change", function() {
        //get the file name
        var fileName = $(this).val().replace(/^.*[\\\/]/, '');
        //replace the "Choose a file" label
        $(this).next('.custom-file-label').html(fileName);
    });
});


$(function() {
    $("#caption").click(function(e){
        e.preventDefault(); //prevent reload

        var fd = new FormData($('form')[0]);

        $('#loading-image1').show();
        $('#error1').hide();

        $('#info').hide();
        $('#info').empty();

        $.ajax({
            url: '/caption',
            type: 'POST',
            data: fd,
            contentType: false,
            cache: false,
            processData:false,
            success: function(response){
                
                if('captions' in response) {
                    
                    response['captions'].forEach(caption => {
                        var element = '<dl class="row"><dt class="col-8">'+caption['caption']+'</dt><dd class="col-2">'+caption['probability']+'</dd></dl>';
                        $("#info").append(element);
                    });

                    $('#info').show();
                }
                else {
                    $('#error1').html("An unknown error has occured in processing. Please try again.");
                    $('#error1').show();
                }

                $('#loading-image1').hide();

            },
            error: function(jqXHR, textStatus, errorThrown){
                
                $("#error1").html("An unknown error has occured in processing. Please try again.");
                $("#error1").show();

                $('#loading-image1').hide();

                console.log(textStatus);
                console.log(errorThrown);
            }
        });
    });
});


$(function() {
    $("#retrieve").click(function(e){
        e.preventDefault(); //prevent reload

        var fd = new FormData($('form')[1]);

        $('#loading-image2').show();
        $('#error2').hide();

        $('#images').hide();

        $.ajax({
            url: '/retrieve',
            type: 'POST',
            data: fd,
            contentType: false,
            cache: false,
            processData:false,
            success: function(response){
                
                if('paths' in response) {
                    
                    count = 0
                    response['paths'].forEach(path => {

                        id = "#image"+count;

                        var image = $('<img></img>');
                        image.attr('src', "http://52.152.139.121:5000/"+path);
                        $('.thumbnail').eq(count).empty().append(image);
                        count++;

                    });

                    $('#images').show();
                    $('#loading-image2').hide();
                }
                else {
                    $('#error2').html("An unknown error has occured in processing. Please try again.");
                    $('#error2').show();
                    $('#loading-image2').hide();
                }
            },
            error: function(jqXHR, textStatus, errorThrown){
                
                $("#error2").html("An unknown error has occured in processing. Please try again.");
                $("#error2").show();

                $('#loading-image2').hide();

                console.log(textStatus);
                console.log(errorThrown);
            }
        });
    });
});