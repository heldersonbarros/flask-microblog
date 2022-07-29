$('.order_button').on('click', function(e) {
    console.log("teste")
    $(this).attr('href', $(this).attr('href') + "?order="+ $(this).text);
});