{% if current_user.is_authenticated %}
$(document).ready(function() {
	var since = 0;
	setInterval(function()) {
		$.ajax("{{url_for('notification')}}?since="+since).done(function(notifications){
			for (var i = 0; i<notification.length; i++){
				// colocar para atualizar o numero de notificaticoes
				since= notifications[i].timestamp;
			}
		})
	}
}
{% endif %}
