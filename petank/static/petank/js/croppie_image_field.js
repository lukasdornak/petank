$(function () {
    console.log(auto_cropped_path);
    $('#cropper').croppie({
        viewport: {width: 496, height: 496, type: 'squere'},
        boundary: {width: 700, height: 700},
        showZoomer: true,
        enableResize: true,
    });
    $('#id_original').bind('change', function () {
        if (this.files && this.files[0]) {
            var reader = new FileReader();
            reader.onload = function (e) {
                $('#cropper').croppie('bind', {
                    url: e.target.result
                });
            };
            reader.readAsDataURL(this.files[0]);
        }
        $('#thumbnail').css('display', 'none');
        $('#cropper').css('display', 'inline-block');
    });
    $('form').submit(function () {
        if ($('#cropper').css('display')!=='none') {
            $('#cropper').croppie('result', {}).then(function (croppedData) {
                $('#id_cropped').val(croppedData);
            });
        }
        return true;
    });
    var current_image_link = $('label[for="id_original"] ~ p > a').attr('href');
    if (current_image_link){
        $('#thumbnail > img').attr('src', auto_cropped_path?auto_cropped_path:current_image_link.split('.')[0] + '_cropped.png').on('click', function () {
            $('#cropper').css('display', 'inline-block').croppie('bind', {
                url: current_image_link + "?" + new Date().getTime()
            });
            $('#thumbnail').css('display', 'none');
        });
        $('#thumbnail').css('display', 'block');
    }
});