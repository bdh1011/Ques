$(document).ready(function(){
	
});

function login(){
	$("body.intro .content").animate({
		height:"660px",
		marginTop:"-320px"

	});
	$(".login_box").css("display","block");
	$("#login_btn").remove();
	$(".login").html("이메일과 비밀번호를 입력해주세요<br><br>");

}