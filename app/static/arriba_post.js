$(document).ready(function() {
	$(".arribaButton").on('click', function(){
		var post_id = $(this).attr('post_id');

		req = $.ajax({
			url: '/arriba_post',
			type: 'POST',
			data: {post_id: post_id}
		});

		req.done(function(data){
			if($("#arriba"+post_id).find("svg").attr("data-prefix") == "fas"){
				$("#arriba"+post_id).find("svg").attr('data-prefix', "far")
				$("#arriba"+post_id).toggleClass("btn-secondary btn-danger")
				$("#arriba"+post_id).find("span").html(data.count)
			}
			else{
				$("#arriba"+post_id).find("svg").attr('data-prefix', "fas")
				$("#arriba"+post_id).toggleClass("btn-secondary btn-danger")
				$("#arriba"+post_id).find("span").html(data.count)
			}
		});
	});

});
