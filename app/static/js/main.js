$(document).ready(function(){

	/*
	$(document).on("click", ".survey_sort_wrapper ul li", function(){
		$(this).css("background-image",'url("'+"../static/img/send_rectangler_icon.png"+'")');
		$(this).css("background-repeat","no-repeat");
		$(this).css("background-position","right");
		$(this).css("color","#FF3900");
		$(this).siblings().css("background-image","none");
		$(this).siblings().css("color","#A7A7A7");
	})
	*/

	var pathname = window.location.pathname;
	console.log(pathname);
	if(pathname.indexOf("like")!=-1){
		$("#like_sort").css("background-image",'url("'+"../static/img/send_rectangler_icon.png"+'")');
		$("#like_sort").css("background-repeat","no-repeat");
		$("#like_sort").css("background-position","right");
		$("#like_sort").css("color","#FF3900");
	}

	else if(pathname.indexOf("joined_num")!=-1){
		$("#join_sort").css("background-image",'url("'+"../static/img/send_rectangler_icon.png"+'")');
		$("#join_sort").css("background-repeat","no-repeat");
		$("#join_sort").css("background-position","right");
		$("#join_sort").css("color","#FF3900");
	}

	else if(pathname.indexOf("que")!=-1){
		$("#que_sort").css("background-image",'url("'+"../static/img/send_rectangler_icon.png"+'")');
		$("#que_sort").css("background-repeat","no-repeat");
		$("#que_sort").css("background-position","right");
		$("#que_sort").css("color","#FF3900");
	}

	else{
		$("#latest_sort").css("background-image",'url("'+"../static/img/send_rectangler_icon.png"+'")');
		$("#latest_sort").css("background-repeat","no-repeat");
		$("#latest_sort").css("background-position","right");
		$("#latest_sort").css("color","#FF3900");
	}


});