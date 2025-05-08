function formatCoordinates(feature) {
  let lat = feature.geometry.coordinates[0];
  let lon = feature.geometry.coordinates[1];
  return `N ${lat}° &nbsp; E ${lon}°`;
}

function makePopupContent(feature) {
  let coordinates = formatCoordinates(feature);
  let popupContent = coordinates;

  if (feature.properties.name != "" && feature.properties.description != "") {
    popupContent = `${coordinates}<br>${feature.properties.name}: ${feature.properties.description}`;
  }

  return popupContent;
}

function onEachFeature(feature, layer) {
  if (feature.geometry.type == "Point") {
    let popupContent = makePopupContent(feature);
    layer.bindPopup(popupContent);
  }
}

function onEachSchoolFeature(feature, layer) {
  if (feature.geometry.type == "Point") {
    let coordinates = formatCoordinates(feature);
    let popupContent = `${coordinates}<br>${feature.properties.name}, ${feature.properties.city}`;
    layer.bindPopup(popupContent);
  }
}

function makeMarkerIcon(icon, markerColor) {
  return L.AwesomeMarkers.icon({
    icon: icon,
    iconColor: "white", // Adds 'icon-white' class, see style.css.
    markerColor: markerColor,
    prefix: "fa",
  });
}

function pointToLayer(feature, latlng) {
  let markerColor;
  let icon;
  let opacity = 1;

  if (feature.properties.type === "site") {
    markerColor = "darkblue";
    icon = "circle-dot";
  } else if (feature.properties.type === "start") {
    markerColor = "red";
    icon = "play";
  } else if (feature.properties.type === "finish") {
    markerColor = "red";
    icon = "stop";
  } else {
    markerColor = "lightgray";
    icon = "";
    opacity = 0.7;
  }

  let markerIcon = makeMarkerIcon(icon, markerColor);
  return L.marker(latlng, { icon: markerIcon, opacity: opacity });
}

function schoolPointToLayer(feature, latlng) {
  let markerColor = "darkblue";
  let icon = "circle-dot";

  if (feature.properties.city === "Lučenec") {
    markerColor = "red";
  }

  let markerIcon = makeMarkerIcon(icon, markerColor);
  return L.marker(latlng, { icon: markerIcon });
}

function excludePoints(feature) {
  return feature.geometry.type != "Point";
}

function excludeHelperPoints(feature) {
  if (feature.geometry.type == "Point") {
    if (feature.properties.type == "helper") {
      return false;
    }
    return true;
  }
  return false;
}

function includeHelperPoints(feature) {
  return !excludeHelperPoints(feature);
}

//
// Layers --------------------------------------------------------------------
//

let osm = L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
});

//
// Maps ----------------------------------------------------------------------
//
function renderRouteMap(center, zoom, data) {
  let routeGeojson = L.geoJson(data, {
    style: {
      color: "#0093dd",
      weight: 5,
    },
    filter: excludePoints,
  });

  let sitesGeojson = L.geoJson(data, {
    onEachFeature: onEachFeature,
    pointToLayer: pointToLayer,
    filter: excludeHelperPoints,
  });

  let helperPointsGeojson = L.geoJson(data, {
    onEachFeature: onEachFeature,
    pointToLayer: pointToLayer,
    filter: includeHelperPoints,
  });

  let baseMaps = {
    OpenStreetMap: osm,
  };
  let overlayMaps = {
    "Orientačné body": L.layerGroup([helperPointsGeojson]),
  };

  let map = L.map("map", {
    center: center,
    zoom: zoom,
    layers: [osm, routeGeojson, sitesGeojson],
  });
  map.addControl(L.control.layers(baseMaps, overlayMaps));
  map.addControl(L.control.scale({ position: "bottomright", imperial: false }));
}

function renderSchoolsMap(center, zoom, data) {
  let geojson = L.geoJson(data, {
    onEachFeature: onEachSchoolFeature,
    pointToLayer: schoolPointToLayer,
    style: {
      color: "#0093dd",
      weight: 3,
    },
  });

  let map = L.map("map", {
    center: center,
    zoom: zoom,
    layers: [osm, geojson],
  });
  map.addControl(L.control.scale({ position: "bottomright", imperial: false }));
}
