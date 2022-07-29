$(document).ready(function() {
    pathname = new URL(document.location).pathname
    pathname_split = pathname.split("/")
    $("input[name=options]").on("change", function(){
        parameter = $("input[name='options']:checked").attr("order")
        if (pathname_split[1] == "tops"){
            url = "http://127.0.0.1:5000/tops"
        } else{
            url = "http://127.0.0.1:5000" + pathname
        }

        document.location = url + "?order=" + parameter
    })
})