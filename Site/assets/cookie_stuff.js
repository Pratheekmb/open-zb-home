function getCookie(c_name) {
	var i,x,y,ARRcookies=document.cookie.split(";");
	for (i=0;i<ARRcookies.length;i++) {
		x=ARRcookies[i].substr(0,ARRcookies[i].indexOf("="));
		y=ARRcookies[i].substr(ARRcookies[i].indexOf("=")+1);
		x=x.replace(/^\s+|\s+$/g,"");
  		if (x==c_name){
			return unescape(y);
		}
  	}
}

function setCookie(c_name,value,exdays) {
	var exdate=new Date();
	exdate.setDate(exdate.getDate() + exdays);
	var c_value=escape(value) + ((exdays==null) ? "" : "; expires="+exdate.toUTCString());
	document.cookie=c_name + "=" + c_value;
}

function checkButtonCookies(myArray) {                 
	for (var i = 0; i < myArray.length; i++) {
		if (getCookie(myArray[i])=="True")
			document.getElementById(myArray[i]+"_button").click();
	}
}

function checkPasswordCookie() {
	var password=getCookie("password");
	if (password!=null && password!=""){
		document.getElementById('password').value = password;
	} else {
		setPassword();
	}
}

function setPassword() {
	pass=MD5(prompt('Please enter your password:',''));
	setCookie('password',pass,365);
	document.getElementById('password').value = pass;
}

function toggle(module) {
	panel=document.getElementById(module+"_panel");
	button=document.getElementById(module+"_button");

	if(panel.style.display == "block") {
		panel.style.display = "none";
		button.style.color= "#3CF";
		setCookie(module,false,365);	
	} else {
		panel.style.display = "block";
		button.style.color= "#0F0";
		setCookie(module,"True",365);	
	}
}