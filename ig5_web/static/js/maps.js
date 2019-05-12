// buttom to reset the default position
function HomeControl(controlDiv, map) {
	// set buttons CSS
	controlDiv.id = 'HomeControl'
	var controlUI = document.createElement('DIV');
	controlUI.title = 'Kliknutím nastavíte mapu do východiskovej polohy'
	controlDiv.appendChild(controlUI);
	var controlText = document.createElement('DIV');
	controlText.innerHTML = 'Centrovať'
	controlUI.appendChild(controlText);

	// setup the click event listener
	google.maps.event.addDomListener(controlDiv, 'click', function() {
		map.setCenter(center);
		map.setZoom(zoom);
	});
}

// buttom to show elevation profile
function ProfileControl(controlDiv, map) {
	// set buttons CSS
	controlDiv.id = 'ProfileControl';
	var controlUI = document.createElement('DIV');
	controlUI.title = 'Kliknutím zobrazíte vertikálny profil priebehu terénu na trase';
	controlDiv.appendChild(controlUI);
	var controlText = document.createElement('DIV');
	controlText.innerHTML = 'Vertikálny profil';
	controlUI.appendChild(controlText);

	// setup the click event listener
	google.maps.event.addDomListener(controlDiv, 'click', function() {
		var chart = document.getElementById('elevation_chart');
		if(chart.style.zIndex == 0) {
			chart.style.zIndex = 10;
			chart.style.display = "block";
			controlText.innerHTML = 'Skryť profil';
			controlUI.title = 'Kliknutím zrušíte zobrazenie vertikálneho profilu priebehu terénu na trase';
		}
		else{
			chart.style.zIndex = 0;
			chart.style.display = "none";
			controlText.innerHTML = 'Vertikálny profil';
		}
	});
}


	// map initialization function
	// ***************************
function maps_initialize(){
	var routePoints = [],       // empty array which will be filled with point coordinates for path displaying
	    icon,                   // empty icon variable
	    css,                    // empty CSS class variable
	    labelContent;           // empty labelContent variable

	var myOptions = {
		zoom: zoom,
		center: center,
		mapTypeId: google.maps.MapTypeId.HYBRID
	};
	var map = new google.maps.Map(document.getElementById("map_canvas"),myOptions);

	// create the DIV to hold the control and call the HomeControl() constructor passing in this DIV
		var homeControlDiv = document.createElement('DIV'),
		    homeControl = new HomeControl(homeControlDiv, map);
		homeControlDiv.index = 1;
		map.controls[google.maps.ControlPosition.TOP_RIGHT].push(homeControlDiv);
	// variables to get current file name
	var url = window.location.pathname,
	    filename = url.substring(url.lastIndexOf('/')+1);

	if (filename.indexOf('rocnik.html') !== -1){
		// create the DIV to hold the control and call the ProfileControl() constructor passing in this DIV
		var profileControlDiv = document.createElement('DIV'),
		    profileControl = new ProfileControl(profileControlDiv, map);
		profileControlDiv.index = 1;
		map.controls[google.maps.ControlPosition.TOP_RIGHT].push(profileControlDiv);
	}


	// loop through points
	// *******************
	for (var i = 0; i < points.length; i++){
		 var point = points[i];
		 var pointLat = point.coordinates[0];
		 var pointLon = point.coordinates[1];

		 var isSchool = false;
		 var pointDescription;
		 if (point.hasOwnProperty('description')) {
			 pointDescription =  point.description;
		 } else if (point.hasOwnProperty('city')) {
			 pointDescription =  point.city;
			 isSchool = true;
		 }

		// compose the message for infowindows
		var messageBase = "<br>" + "WGS-84: " + "&nbsp N " + pointLat + "°" + "&nbsp&nbsp E " + pointLon + "°";
		var messagePrefix;
		if(pointDescription !== ""){
			messagePrefix = point.name + ": " + pointDescription;
		}
		else {
			messagePrefix = point.name
		}
		message = messagePrefix + messageBase

		// compose labelContent
		var sub;
		if(isSchool){
			labelContent = point.city;
			sub = "school";
		}
		else {
			labelContent = point.name;
			sub = point.name.substring(3,4);
		}

		switch(sub){
			// start
			case "r" :	icon = "static/img/style/maps_start.png";
						css = "labels start";
						break;
			// site
			case "s" : 	icon = "static/img/style/maps_stanovisko.png"
						css = "labels stanovisko";
						break;
		    // orientate site
			case "o" : 	icon = "static/img/style/maps_orientacne.png";
						css = "labels orientacne";
						break;
				//
			case "e" : 	icon = "static/img/style/maps_orientacne.png";
						css = "labels orientacne";
						break;
				// napr. 10. orientačné stanovisko - dvojciferne
			case " " : 	icon = "static/img/style/maps_orientacne.png";
						css = "labels orientacne";
						break;
			// finish
			case "ľ" : 	icon = "static/img/style/maps_finish.png";
						css = "labels finish";
						break;
			// schools
			case "school" :	if(point.city === "Lučenec"){
								icon = "static/img/style/maps_finish.png";
								css = "labels finish";
								break;
							}
							else {
								icon = "static/img/style/maps_start.png";
								css = "labels start";
								break;
							}
		}

		// point marker
		var marker = new MarkerWithLabel({
			position: new google.maps.LatLng (pointLat,pointLon),
			map: map,
			labelClass: css,
			labelContent: labelContent,
			labelStyle: {opacity:1},
			// title: point[0],
			title: point.name,
			html: message,
			icon: icon
		});

		// filling array with points coordinates
		// console.log(point);
		routePoints.push(new google.maps.LatLng(pointLat,pointLon));

		// just for site "kontakty.php" - creates a Lucenec centered star shape
		if (isSchool) {
			routePoints.push(new google.maps.LatLng(48.328132,19.656845));
		}

		// infowindow with its content
		var infowindow = new google.maps.InfoWindow({});
		google.maps.event.addListener(marker, 'click', function() {
			infowindow.setContent(this.html);
			infowindow.open(map, this);
		});
	}
	// loop through points end
	// ***********************


	// route parameters and display
	//*****************************
	var route = new google.maps.Polyline({
		path: routePoints,
		strokeColor: "#0093dd",
		strokeOpacity: 1.0,
		strokeWeight: 3
	});
	route.setMap(map);

	// create an ElevationService object and draw the vertical profile
	//****************************************************************
	if(!isSchool){
		elevator = new google.maps.ElevationService();
		drawProfile(routePoints);
	}
}
// map initialization function end
// *******************************


// load the Visualization API and the corechart package
// must be referenced outside of a function
google.load("visualization", "1", {packages: ["corechart"]});

function drawProfile(path) {
	// create a new chart in the elevation_chart DIV
	chart = new google.visualization.ComboChart(document.getElementById('elevation_chart'));
	// create a PathElevationRequest object using this array, ssk for 256 samples along that path
	var pathRequest = {
		'path': path,
		'samples': 256
	};
	// initiate the path request
	elevator.getElevationAlongPath(pathRequest, plotElevation);
}

// takes an array of ElevationResult objects, draws the path on the map
// and plots the elevation profile on a Visualization API chart
function plotElevation(results, status) {
	if (status == google.maps.ElevationStatus.OK) {
		elevations = results;

		// extract vipPoints - start, stanoviska, ciel
		var vipPoints = [];
		var point;
		for (var i = 0; i < points.length; i++){
			point = points[i];
			if (point.name === "Štart" || point.name === "Cieľ" || (point.name.length < 15)){
				vipPoints.push([point.coordinates[0],point.coordinates[1],point.name]);
			}
		}

		// get elevation attributes names to an array coz google keeps changing them
		var elevAttr = [];
		for(var propertyName in elevations[0].location) {
			elevAttr.push(propertyName);
		}

		var checked = [],									// will be filled when filtering vipPoints to get them to the graf
			elevX = elevAttr[0],							// elevation point lat property name
			elevY = elevAttr[1]								// elevation point lon property name
			maxHwindow = 0,									// viewWindow maximum elevation default value
			maxH = 0,										// route maximum elevation default value
			minHwindow = 5000,								// viewWindow minimum elevation default value
			minH = 5000,									// route minimum elevation default value
			annotation = null,								// graph points annotation default value
			data = new google.visualization.DataTable();	// prepare graph DataTable
		data.addColumn('string', 'Poloha');
		data.addColumn('number', 'Nadmorská výška [m n.m.]');
		data.addColumn('number', 'Stanovisko');
		data.addColumn({type: 'string', role: 'annotation'});
		for (var i = 0; i < results.length; i++) {
			var vyska = parseFloat(elevations[i].elevation.toFixed(2)),
				lat = elevations[i].location[elevX]().toFixed(5),
				lon = elevations[i].location[elevY]().toFixed(5),
			    poloha = 'N:' + lat + '° E:' + lon + '°',
				stanovisko = 0;

			for (var ii = 0; ii < vipPoints.length; ii++){
				var rozdiel = Math.abs((parseFloat(lat) - vipPoints[ii][0])) + Math.abs((parseFloat(lon) - vipPoints[ii][1]));
				if (rozdiel < 0.0005 && !(ii in checked)){
					checked.push(ii);
					stanovisko = vyska;
					annotation = vipPoints[ii][2];
				}
				else continue;
			}

			// get min & max high
			if (vyska < minH) {
				minH = vyska;
				minHwindow = vyska - 20;
			}
			if (vyska > maxH) {
				maxH = vyska;
				maxHwindow = vyska + 10;
			}

			// fill the table
			data.addRow([poloha,vyska,stanovisko, annotation]);
		}

		// draw the chart using the data within its DIV
		chart.draw(data, {
			width: $('#map_canvas').width(),
			height: 400,
			title: 'VERTIKÁLNY PROFIL PRIEBEHU TERÉNU NA TRASE V SMERE ŠTART -> CIEĽ',
			titleTextStyle: { color: '#db3041' },
			hAxis: { textPosition: 'none' },
			vAxis: { viewWindowMode: 'explicit', viewWindow: { min: minHwindow, max: maxHwindow } },
			titleY: 'Nadmorská výška [m n.m.]',
			colors: ['#0093dd'],
			legend: 'bottom',
			enableInteractivity: true,
			seriesType: "line",
			series: { 1: { type: "line", color: '#db3041', lineWidth: 2 } },
		});
	}
	// insert height info to route information
	$('ul#route-desc li:nth-child(4)').after('<li><span class="red">Nadmorská výška: </span>'+ minH + ' - ' + maxH + ' m n.m. </li>');
}
