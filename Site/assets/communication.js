var using_ws = false;

function checkWebSockets()
{

	if ("WebSocket" in window) {
	
		document.getElementById('ws_response').innerHTML = '\
		<div id="conn_status">Not Connected</div>\
		<h4 id="error" style="color:#ff0000"></h4>\
		<div id="console" class="ws_response"></div> ';

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
			$('#conn_status').html('<b>Connected</b>');
			ws.send(document.getElementById('password').value);
			ws.send('[p]');
			using_ws = true;
		}
		ws.onerror = function(evt) {
			$('#conn_status').html('<b>Error</b>');
		}
		ws.onclose = function(evt) {
			$('#conn_status').html('<b>Disconnected - Using AJAX!</b> <button type="button" onclick ="checkWebSockets()">Re-connect</button>');

			document.getElementById('AC_status').innerHTML=
				'Air Conditioner'
					
			document.getElementById('mood_light_status').innerHTML=
				'Mood Light'

			using_ws = false;
		}
	}

	else { // no websocket support
		$('error').innerHTML = "Your browser does not appear to support WebSockets";
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
		  
		/*xmlhttp.onreadystatechange=function()
		//  {
		  if (xmlhttp.readyState==4 && xmlhttp.status==200)
			{
			document.getElementById("myDiv").innerHTML=xmlhttp.responseText;
			}
		  }
		  */
		  
		xmlhttp.open("POST","https://" +  document.location.hostname + ":8880/form",true);
		xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
		xmlhttp.send("pass=" + encodeURIComponent(document.getElementById('password').value) 
					+"&cmd="+encodeURIComponent(str));
	}
}