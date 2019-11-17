/*
 * Replace all SVG images with inline SVG
 */
var alreadySeen = {}

$(function(){
    $('img.icon').each(function (index, element) {
        replaceImgWithSVG(element)
    });
});

function replaceImgWithSVG(img) {
    var $img = $(img);
    var imgURL = $img.attr('src');

    if (imgURL in alreadySeen) {
        replaceImgWithSVGData(alreadySeen[imgURL], $img)
        return
    }

    jQuery.get(imgURL, function(data) {
        alreadySeen[imgURL] = data
        replaceImgWithSVGData(data, $img)
    }, 'xml');
}

function replaceImgWithSVGData(svgData, $img) {
    var imgID = $img.attr('id');
    var imgClass = $img.attr('class');
    // Get the SVG tag, ignore the rest
    var $svg = jQuery(svgData).find('svg');

    // Add replaced image's ID to the new SVG
    if(typeof imgID !== 'undefined') {
        $svg = $svg.attr('id', imgID);
    }
    // Add replaced image's classes to the new SVG
    if(typeof imgClass !== 'undefined') {
        $svg = $svg.attr('class', imgClass+' replaced-svg');
    }

    // Remove any invalid XML tags as per http://validator.w3.org
    $svg = $svg.removeAttr('xmlns:a');
    
    // Check if the viewport is set, else we gonna set it if we can.
    if(!$svg.attr('viewBox') && $svg.attr('height') && $svg.attr('width')) {
        $svg.attr('viewBox', '0 0 ' + $svg.attr('height') + ' ' + $svg.attr('width'))
    }

    // Replace image with new SVG
    $img.replaceWith($svg);

}