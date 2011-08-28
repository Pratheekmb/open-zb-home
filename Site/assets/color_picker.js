(function() {
	var Event = YAHOO.util.Event, picker;
 
	Event.onDOMReady(function() {
			YAHOO.log("Creating Color Picker.", "info", "example");
			picker = new YAHOO.widget.ColorPicker("light_color_picker", {
				showhsvcontrols: false,
				showrgbcontrols: false,
				showhsvcontrols: false,
				showhexcontrols: true,
				showhexsummary: false,
					images: {
						PICKER_THUMB: "assets/picker_thumb.png",
						HUE_THUMB: "assets/hue_thumb.png"
					}
				});
			YAHOO.log("Finished creating Color Picker.", "info", "example");
			
			//a listener for logging RGB color changes;
			//this will only be visible if logger is enabled:
			var onRgbChange = function(o) {
			document.getElementById('light_color_picker').style.cssText = 'box-shadow: 0 0 20px 5px #'+picker.get("hex");/*
			document.getElementById('light_color_picker').style.cssText1 = '-box-shadow: 0 0 20px 5px #'+picker.get("hex");
			document.getElementById('light_color_picker').style.cssText2 = '-webkit-shadow: 0 0 20px 5px #'+picker.get("hex");*/

				sendCmd("4![c"+picker.get("hex")+"]");
			}
			
			//subscribe to the rgbChange event;
			picker.on("rgbChange", throttle(onRgbChange,20));
			
			//use setValue to reset the value to white:
			Event.on("reset", "click", function(e) {
				picker.setValue([255, 255, 255], false); //false here means that rgbChange
														 //wil fire; true would silence it
			});
			
		});
})();
	

function throttle(func, wait) {
	var timeout;
	return function() {
		var context = this, args = arguments;
			if (!timeout) {
				// the first time the event fires, we setup a timer, which 
				// is used as a guard to block subsequent calls; once the 
				// timer's handler fires, we reset it and create a new one
				timeout = setTimeout(function() {
				timeout = null;
				func.apply(context, args);
			}, wait);
		}
	}
}