$(document).ready(function(){

	$(document).on("click", ".survey_sort_wrapper ul li", function(){
		$(this).css("background-image",'url("'+"../static/img/send_rectangler_icon.png"+'")');
		$(this).css("background-repeat","no-repeat");
		$(this).css("background-position","right");
		$(this).css("color","#FF3900");
		$(this).siblings().css("background-image","none");
		$(this).siblings().css("color","#A7A7A7");
	})
	
});

function sort(){

	$("#wrapper").remove();
	$("#login-wrapper").css("display","block");
	$("#fb-wrapper").css("display","block");
}