var mapboxUrl = "https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoiYmVyc2lobmwiLCJhIjoiY2l1c3R1bmVwMDAwMTJvcXd6NnpwZW0yMCJ9.zrMm9tMHb9L41nG9XuXT-w",
    mapboxAttr = 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
      '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
      'Imagery © <a href="http://mapbox.com">Mapbox</a>',

    opentopoUrl = 'http://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
    opentopoAttr = 'Map data: &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)',

    osmUrl = 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    osmAttr = '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',

    esriWorldImageryUrl = 'http://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    esriWorldImageryAttr = 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community' ;

var satellite = L.tileLayer(mapboxUrl, {id: 'mapbox.satellite', maxZoom: 18, attribution: mapboxAttr}),
    topo = L.tileLayer(opentopoUrl, {maxZoom: 17, attribution: opentopoAttr}),
    osm = L.tileLayer(osmUrl, {maxZoom: 19, attribution: osmAttr}),
    esriWorldImagery =  L.tileLayer(esriWorldImageryUrl, {maxZoom: 19, attribution: esriWorldImageryAttr});

var mymap = L.map("mapid", {
    center: [51.755, 4.373],
    zoom: 10,
    layers: [osm]
});

var baseLayers = {
    "OSM": osm,
    "World Imagery (ESRI)": esriWorldImagery
};

L.control.layers(baseLayers).addTo(mymap);

var geojsonMarkerOptions = {
  radius: 8,
  color: "#000",
  weight: 1,
  opacity: 1,
  fillOpacity: 0.8
};

function onEachFeature(feature, layer) {
    // does this feature have a property named popupContent?
    if (feature.properties && feature.properties.popup) {
    layer.bindPopup(feature.properties.popup);
    }
}

function addLayerToMap(map, layer) {
  locationLayer = L.geoJSON(layer, {
      pointToLayer: function (feature, latlng) {
      switch (feature.properties.eventtype) {
        case "nice":        
          geojsonMarkerOptions.fillColor="#00FF00";
          return L.circleMarker(latlng, geojsonMarkerOptions);
        case "notable":
          geojsonMarkerOptions.fillColor="#B9FF00";
          return L.circleMarker(latlng, geojsonMarkerOptions);
        case "threatening":
          geojsonMarkerOptions.fillColor="#FFFF00";
          return L.circleMarker(latlng, geojsonMarkerOptions);
        case "harassment":
          geojsonMarkerOptions.fillColor="#FB5C00";
          return L.circleMarker(latlng, geojsonMarkerOptions);
        case "violence":
          geojsonMarkerOptions.fillColor="#FA0000";
          return L.circleMarker(latlng, geojsonMarkerOptions);
        default:
          geojsonMarkerOptions.fillColor="#d3d3d3";
          return L.circleMarker(latlng, geojsonMarkerOptions);
      }
    }, onEachFeature: onEachFeature
  }).addTo(map);
}

//addLayerToMap(mymap, mapitems);
	

function getFormData() {
  var enddate = document.getElementsByName("enddate")[0].value;
  var numberofdays = document.getElementsByName("numberofdays")[0].value;
  var type = document.getElementsByName("type")[0].value;
  var user = document.getElementsByName("user")[0].value;
  var baseurl = document.getElementsByName("baseurl")[0].value;
  var timezone = document.getElementsByName("timezone")[0].value;
  
  url = baseurl + "?enddate=" + enddate + "&numberofdays=" + numberofdays + "&type=" + type + "&user=" + user + "&timezone=" + timezone + "&f=pjson";
  
  function getNewJSON(src, callback) {
    newjsonfile = document.createElement("script");
    newjsonfile.type = "text/javascript";
    newjsonfile.id = "jsonfile";
    newjsonfile.src = src;
    newjsonfile.onload = function(){
      callback(mapitems);
    };
    document.getElementsByTagName('head')[0].appendChild(newjsonfile);
  }

  getNewJSON(url, function(mapitems) {
    mymap.removeLayer(locationLayer);
    addLayerToMap(mymap, mapitems);
    //alert(url, JSON.stringify(mapitems));
  });
}
	
new Pikaday({
  field: document.getElementById("enddate"),
  onSelect: date => {
  const year = date.getFullYear(),
    month = date.getMonth() + 1,
    day = date.getDate(),
    formattedDate = [
      year,
      month < 10 ? "0" + month : month,
      day < 10 ? "0" + day : day
    ].join("-");
    document.getElementById("enddate").value = formattedDate;
  }
});

var mytimezone=jstz.determine().name();
var jsonurl = 'http://gpsphoto.fritz.box/get?f=pjson&timezone=' + mytimezone;

(function(d, script) {
    script = d.createElement('script');
    script.type = 'text/javascript';
    script.async = true;
    script.onload = function(){
        addLayerToMap(mymap, mapitems);
        //alert(JSON.stringify(mapitems))
    };
    script.src = jsonurl;
    script.id = 'jsonfile';
    d.getElementsByTagName('head')[0].appendChild(script);
}(document));


qform.elements.timezone.value = jstz.determine().name();

