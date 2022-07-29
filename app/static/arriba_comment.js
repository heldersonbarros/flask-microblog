$(document).ready(function() {
	$(".arribaCommentButton").on('click', function(){
		var comment_id = $(this).attr('comment_id');

		req = $.ajax({
			url: '/arriba_comment',
			type: 'POST',
			data: {comment_id: comment_id}
		});

		req.done(function(data){
			if($("#arribaComment"+comment_id).find("svg").attr("data-prefix") == "fas"){
				$("#arribaComment"+comment_id).find("svg").attr('data-prefix', "far")
				$("#arribaComment"+comment_id).toggleClass("btn-secondary btn-danger")
				$("#arribaComment"+comment_id).find("span").html(data.count)
			}
			else{
				$("#arribaComment"+comment_id).find("svg").attr('data-prefix', "fas")
				$("#arribaComment"+comment_id).toggleClass("btn-secondary btn-danger")
				$("#arribaComment"+comment_id).find("span").html(data.count)
			}
		});
	});

});