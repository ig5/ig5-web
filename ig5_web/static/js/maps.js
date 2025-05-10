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
  if (Object.keys(data).length === 0) {
    return;
  }

  let routeGeojson = L.geoJson(data, {
    style: {
      color: LINE_COLOR,
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

  // var elevation_options = {
  //   // theme: "white-theme",
  //   almostOver: true,
  //   waypoints: false,
  //   detached: true,
  //   position: "bottomright",
  //   speed: false,
  //   altitude: true,
  //   time: false,
  //   summary: false,
  //   legend: false,
  //   distanceMarkers: false,
  //   distance: true,
  //   hotline: true,
  //   downloadLink: false,
  //   ruler: true,
  //   summary: false,
  //   wptIcons: false,
  //   // height: 200,
  // };
  // var controlElevation = L.control.elevation(elevation_options).addTo(map);
  // var elevationGeoJson = {
  //   results: [
  //     {
  //       dataset: "eudem25m",
  //       elevation: 278.52667236328125,
  //       location: {
  //         lat: 48.355,
  //         lng: 19.57547,
  //       },
  //     },
  //     {
  //       dataset: "eudem25m",
  //       elevation: 249.78109741210938,
  //       location: {
  //         lat: 48.35396,
  //         lng: 19.57876,
  //       },
  //     },
  //     {
  //       dataset: "eudem25m",
  //       elevation: 256.8179626464844,
  //       location: {
  //         lat: 48.35567,
  //         lng: 19.57832,
  //       },
  //     },
  //     {
  //       dataset: "eudem25m",
  //       elevation: 239.8062286376953,
  //       location: {
  //         lat: 48.35685,
  //         lng: 19.5797,
  //       },
  //     },
  //     {
  //       dataset: "eudem25m",
  //       elevation: 244.0004425048828,
  //       location: {
  //         lat: 48.36045,
  //         lng: 19.57555,
  //       },
  //     },
  //     {
  //       dataset: "eudem25m",
  //       elevation: 243.7277069091797,
  //       location: {
  //         lat: 48.36301,
  //         lng: 19.57226,
  //       },
  //     },
  //     {
  //       dataset: "eudem25m",
  //       elevation: 248.00827026367188,
  //       location: {
  //         lat: 48.36251,
  //         lng: 19.5696,
  //       },
  //     },
  //     {
  //       dataset: "eudem25m",
  //       elevation: 249.32687377929688,
  //       location: {
  //         lat: 48.36674,
  //         lng: 19.5658,
  //       },
  //     },
  //     {
  //       dataset: "eudem25m",
  //       elevation: 258.1531066894531,
  //       location: {
  //         lat: 48.37156,
  //         lng: 19.56126,
  //       },
  //     },
  //     {
  //       dataset: "eudem25m",
  //       elevation: 265.7034606933594,
  //       location: {
  //         lat: 48.37922,
  //         lng: 19.55347,
  //       },
  //     },
  //     {
  //       dataset: "eudem25m",
  //       elevation: 287.6736145019531,
  //       location: {
  //         lat: 48.3739,
  //         lng: 19.54786,
  //       },
  //     },
  //     {
  //       dataset: "eudem25m",
  //       elevation: 288.09490966796875,
  //       location: {
  //         lat: 48.37265,
  //         lng: 19.54908,
  //       },
  //     },
  //     {
  //       dataset: "eudem25m",
  //       elevation: 341.3575439453125,
  //       location: {
  //         lat: 48.37347,
  //         lng: 19.53913,
  //       },
  //     },
  //     {
  //       dataset: "eudem25m",
  //       elevation: 353.8987731933594,
  //       location: {
  //         lat: 48.37409,
  //         lng: 19.53701,
  //       },
  //     },
  //     {
  //       dataset: "eudem25m",
  //       elevation: 368.0915832519531,
  //       location: {
  //         lat: 48.37496,
  //         lng: 19.53689,
  //       },
  //     },
  //     {
  //       dataset: "eudem25m",
  //       elevation: 394.8926086425781,
  //       location: {
  //         lat: 48.37567,
  //         lng: 19.53568,
  //       },
  //     },
  //     {
  //       dataset: "eudem25m",
  //       elevation: 425.6297302246094,
  //       location: {
  //         lat: 48.3767,
  //         lng: 19.53526,
  //       },
  //     },
  //     {
  //       dataset: "eudem25m",
  //       elevation: 427.70159912109375,
  //       location: {
  //         lat: 48.37792,
  //         lng: 19.53159,
  //       },
  //     },
  //     {
  //       dataset: "eudem25m",
  //       elevation: 436.0555725097656,
  //       location: {
  //         lat: 48.37796,
  //         lng: 19.53073,
  //       },
  //     },
  //     {
  //       dataset: "eudem25m",
  //       elevation: 385.57177734375,
  //       location: {
  //         lat: 48.37425,
  //         lng: 19.5347,
  //       },
  //     },
  //     {
  //       dataset: "eudem25m",
  //       elevation: 373.0794982910156,
  //       location: {
  //         lat: 48.373,
  //         lng: 19.5358,
  //       },
  //     },
  //     {
  //       dataset: "eudem25m",
  //       elevation: 384.9365539550781,
  //       location: {
  //         lat: 48.36984,
  //         lng: 19.5349,
  //       },
  //     },
  //     {
  //       dataset: "eudem25m",
  //       elevation: 398.2651062011719,
  //       location: {
  //         lat: 48.36927,
  //         lng: 19.53272,
  //       },
  //     },
  //     {
  //       dataset: "eudem25m",
  //       elevation: 376.81427001953125,
  //       location: {
  //         lat: 48.36693,
  //         lng: 19.52875,
  //       },
  //     },
  //     {
  //       dataset: "eudem25m",
  //       elevation: 358.52716064453125,
  //       location: {
  //         lat: 48.36533,
  //         lng: 19.52947,
  //       },
  //     },
  //     {
  //       dataset: "eudem25m",
  //       elevation: 361.3663024902344,
  //       location: {
  //         lat: 48.36476,
  //         lng: 19.5294,
  //       },
  //     },
  //     {
  //       dataset: "eudem25m",
  //       elevation: 374.2415771484375,
  //       location: {
  //         lat: 48.36479,
  //         lng: 19.5288,
  //       },
  //     },
  //     {
  //       dataset: "eudem25m",
  //       elevation: 384.4287414550781,
  //       location: {
  //         lat: 48.36222,
  //         lng: 19.52817,
  //       },
  //     },
  //     {
  //       dataset: "eudem25m",
  //       elevation: 314.80108642578125,
  //       location: {
  //         lat: 48.35776,
  //         lng: 19.54036,
  //       },
  //     },
  //     {
  //       dataset: "eudem25m",
  //       elevation: 292.545166015625,
  //       location: {
  //         lat: 48.35779,
  //         lng: 19.54522,
  //       },
  //     },
  //     {
  //       dataset: "eudem25m",
  //       elevation: 297.5272521972656,
  //       location: {
  //         lat: 48.35868,
  //         lng: 19.54606,
  //       },
  //     },
  //     {
  //       dataset: "eudem25m",
  //       elevation: 265.1868591308594,
  //       location: {
  //         lat: 48.35482,
  //         lng: 19.56684,
  //       },
  //     },
  //     {
  //       dataset: "eudem25m",
  //       elevation: 265.5827331542969,
  //       location: {
  //         lat: 48.35299,
  //         lng: 19.56932,
  //       },
  //     },
  //     {
  //       dataset: "eudem25m",
  //       elevation: 265.25152587890625,
  //       location: {
  //         lat: 48.35327,
  //         lng: 19.56962,
  //       },
  //     },
  //     {
  //       dataset: "eudem25m",
  //       elevation: 263.963134765625,
  //       location: {
  //         lat: 48.35383,
  //         lng: 19.57046,
  //       },
  //     },
  //   ],
  //   status: "OK",
  // };

  // const geojson = {
  //   name: "demo.geojson",
  //   type: "FeatureCollection",
  //   features: [
  //     {
  //       type: "Feature",
  //       geometry: {
  //         type: "LineString",
  //         coordinates: elevationGeoJson.results.map((item) => [item.location.lng, item.location.lat, item.elevation]),
  //       },
  //     },
  //   ],
  // };
  // controlElevation.load(JSON.stringify(geojson));
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
