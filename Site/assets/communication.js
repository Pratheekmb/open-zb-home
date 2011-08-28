var using_ws = false;

function checkWebSockets(use_ws)
{

	if (use_ws && ("WebSocket" in window)) {
	
		document.getElementById('feedback').innerHTML = '\
		<div id="conn_status">Not Connected</div>\
		<h4 id="error" style="color:#ff0000"></h4>\
		<div id="console" class="feedback"></div> ';

		ws = new WebSocket("wss://" +  document.location.hostname + ":8881/ws");
		ws.onmessage = function(evt) {                
			document.getElementById('console').innerHTML = ">> "+evt.data+"<br>" + 
			document.getElementById('console').innerHTML;
			
			if (evt.data.match("AC IR MODULE ONLINE")) {
				document.getElementById('AC_status').innerHTML=
					'Air Conditioner <span class="panelStatus">ONLINE</span>'
			}
			
			if (evt.data.match("RGB & TEMP MODULE ONLINE")) {
				document.getElementById('mood_light_status').innerHTML=
					'Mood Light <p class="panelStatus">ONLINE</p>'
			}
			
		}
		
		ws.onopen = function(evt) {
			$('#conn_status').html('<b style="color:#006000">Connected</b><button type="button" onclick ="ws.close()">Disconnect</button>');
			ws.send(document.getElementById('password').value); /*Authenticate */
			ws.send('[p]');	/* 'ping' request. Online modules should declare presence */
			using_ws = true;
		}
		ws.onerror = function(evt) {
			$('#conn_status').html('<b>Error</b>');
		}
		ws.onclose = function(evt) {
			checkWebSockets(false);
			
			document.getElementById('AC_status').innerHTML=
				'Air Conditioner'
					
			document.getElementById('mood_light_status').innerHTML=
				'Mood Light'

			using_ws = false;
		}
	}

	else { // no websocket support
		using_ws = false;
		document.getElementById('feedback').innerHTML = '\
		<div id="conn_status"><b style="color:#550000">Using AJAX</b></div>\
		<div id="console" class="feedback"></div> ';

 		if ("WebSocket" in window) 
			$('#conn_status').html('<b style="color:#550000">Using AJAX</b> <button type="button" onclick ="checkWebSockets(true)">Re-connect</button>');
	}		
}

	
function sendCmd(str) {

	if (using_ws != false) {
		ws.send(str)
	} else {
		var xmlhttp;
		if (window.XMLHttpRequest)
		  {// code for IE7+, Firefox, Chrome, Opera, Safari
		  xmlhttp=new XMLHttpRequest();
		  }
		else
		  {// code for IE6, IE5
		  xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
		  }
		  
		xmlhttp.onreadystatechange=function()
		  {
		  if (xmlhttp.readyState==4 && xmlhttp.status==200)
			{
				document.getElementById('console').innerHTML = ">> "+xmlhttp.responseText+"<br>" + 
													document.getElementById('console').innerHTML;
			}
		  }
		  
		  
		xmlhttp.open("POST","https://" +  document.location.hostname + ":8880/form",true);
		xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
		xmlhttp.send("pass=" + encodeURIComponent(document.getElementById('password').value) 
					+"&cmd="+encodeURIComponent(str));
	}
}