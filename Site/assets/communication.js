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
			parseResponse(evt.data);
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
var debug = false;

	if(!debug) {
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
					parseResponse(xmlhttp.responseText);

				}
			  }
			  
			  
			xmlhttp.open("POST","https://" +  document.location.hostname + ":8880/form",true);
			xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
			xmlhttp.send("pass=" + encodeURIComponent(document.getElementById('password').value) 
						+"&cmd="+encodeURIComponent(str));
		}
	}
	else {
	
						document.getElementById('console').innerHTML = "DEBUG: "+str+"<br>" + 
														document.getElementById('console').innerHTML;
	
	}
}

function parseResponse(response) {			
	//dont display temperature in feedback, just update it.
 	if (response.indexOf("Temperature (AC Module): ") > 0) {
		document.getElementById('room_temp').innerHTML=
			'<span onclick ="toggle('+"'temp_frequency'"+' )">TEMP: <span class="panelStatus" >'+ response.substring(response.indexOf("Temperature (AC Module): ")+25 )+'</span>&degc</span>';
	document.getElementById("temperature_display_panel").style.display = "block";
	} else{
	
	document.getElementById('console').innerHTML = ">> "+response+"<br>" + 
										document.getElementById('console').innerHTML;											
	
	if (response.match("RGB & TEMP MODULE ONLINE")) {
		document.getElementById('mood_light_status').innerHTML=
			'Mood Light <span class="panelStatus">ONLINE</p>'
	}
	
	if (response.match("AC IR MODULE ONLINE")) {
		document.getElementById('AC_status').innerHTML=
			'Air Conditioner <span class="panelStatus">ONLINE</p>'
	}
	
	}
}


var temperature = {
    16 : 'CCCCCCCWWC',
    17 : 'CCCCCWWCCC',
    18 : 'CCCCCWCCWC',
    19:  'CCCWWCCCCC',
    20:  'CCCWWWWC',
    21:  'CCCWCCWCCC',
    22:  'CCCWCCCCWC',
    23:  'CWWCCCCCCC',
    24:  'CWWCCWWC',
    25:  'CWWWWCCC',
    26:  'CWWWCCWC',
    27:  'CWCCWCCCCC',
    28:  'CWCCWWWC',
    29:  'CWCCCCWCCC',
    30:  'CWCCCCCCWC',
};

var fan_cold = {
	1: "WCCCCC",
	2: "WWWC",
	3: "CCWCCC",
	4: "CCCCWC"
};

var fan_hot = {
	1: "WCCCCCC",
	2: "WCCWW",
	3: "WWWCC",
	4: "WWCCW"
};
function setACTimer() 
{

	/*if HOT:
	
	POWER = zWW   + FAN(hot)+ CCCCCCC + TEMP + END
	
	else 
		+ fan[document.getElementById('AC_fan_speed').value]
		+ 'CCCCCC'
		+ temperature[document.getElementById('AC_temperature').value]
		+ 'CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCWWC'
		+ ']'); 
	*/
	
		
	sendCmd('2[Cz'+'WCCW'
		+ fan_cold[document.getElementById('AC_fan_speed').value]
		+ 'CCCCCC'
		+ temperature[document.getElementById('AC_temperature').value]
		+ 'CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCWWC'
		+ ']');
		
		
	sendCmd('t' + (parseInt(document.getElementById('AC_timer').value)*60).toString() + '*' 
		+ '2[Cz'+'WCCW'
		+ fan_cold[document.getElementById('AC_fan_speed').value]
		+ 'CCCCCC'
		+ temperature[document.getElementById('AC_temperature').value]
		+ 'CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCWWC'
		+ ']');
		
}



function ACTogglePower()
{	
	sendCmd('2[Cz'+'WCCW'
		+ fan_cold[document.getElementById('AC_fan_speed').value]
		+ 'CCCCCC'
		+ temperature[document.getElementById('AC_temperature').value]
		+ 'CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCWWC'
		+ ']');
}

function ACChangeSettings()
{
	/*
	if HOT:
	TOGGL = iCCCW + FAN(hot)+ CCCCCCC +TEMP + END
	else:
	*/

	sendCmd('2[CiCCCCCW'
			+ fan_cold[document.getElementById('AC_fan_speed').value]
			+ 'CCCCCC'
			+ temperature[document.getElementById('AC_temperature').value]
			+ 'CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCWWC'
			+ ']');
}