// Basemap layers:
// mapbox layer: registration required, limited tiles
var mapboxUrl = "https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoiYmVyc2lobmwiLCJhIjoiY2l1c3R1bmVwMDAwMTJvcXd6NnpwZW0yMCJ9.zrMm9tMHb9L41nG9XuXT-w",
    mapboxAttr = 'Map data &copy; <a href="https://openstreetmap.org">OpenStreetMap</a> contributors, ' +
      '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
      'Imagery © <a href="https://mapbox.com">Mapbox</a>';

// opentopo layer: free but not very stable
var opentopoUrl = 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
    opentopoAttr = 'Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>, <a href="https://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)';

// osm layer: free and fast
var osmUrl = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    osmAttr = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>';

// esri world imagery layer: free and fast
var esriWorldImageryUrl = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    esriWorldImageryAttr = 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community';

// let's define the layers we can add as basemaps
var satellite = L.tileLayer(mapboxUrl, {id: 'mapbox.satellite', maxZoom: 18, attribution: mapboxAttr}),
    topo = L.tileLayer(opentopoUrl, {maxZoom: 17, attribution: opentopoAttr}),
    osm = L.tileLayer(osmUrl, {maxZoom: 19, attribution: osmAttr}),
    esriWorldImagery =  L.tileLayer(esriWorldImageryUrl, {maxZoom: 19, attribution: esriWorldImageryAttr});

server = php_vars.server;
org = php_vars.org;
types = php_vars.types.split(',');
longitude = php_vars.longitude;
latitude = php_vars.latitude;
zoomlevel = php_vars.zoomlevel;



var mymap = L.map("mapid", {
    center: [php_vars.latitude, php_vars.longitude],
    zoom: php_vars.zoomlevel,
    layers: [osm]
});
var cluster = new L.MarkerClusterGroup();

// Chosen basemap layers for inclusion
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
      switch (feature.properties.incidenttype) {
        case types[0]:        
          geojsonMarkerOptions.fillColor="#00FF00";
          return L.circleMarker(latlng, geojsonMarkerOptions);
        case types[1]:
          geojsonMarkerOptions.fillColor="#B9FF00";
          return L.circleMarker(latlng, geojsonMarkerOptions);
        case types[2]:
          geojsonMarkerOptions.fillColor="#FFFF00";
          return L.circleMarker(latlng, geojsonMarkerOptions);
        case types[3]:
          geojsonMarkerOptions.fillColor="#FB5C00";
          return L.circleMarker(latlng, geojsonMarkerOptions);
        case types[4]:
          geojsonMarkerOptions.fillColor="#FA0000";
          return L.circleMarker(latlng, geojsonMarkerOptions);
        default:
          geojsonMarkerOptions.fillColor="#d3d3d3";
          return L.circleMarker(latlng, geojsonMarkerOptions);
      }
    }, onEachFeature: onEachFeature
  })
  //}).addTo(map);
  cluster.addLayer(locationLayer).addTo(map);
}

function getFormData() {
  var enddate = document.getElementsByName("enddate")[0].value;
  var begindate = document.getElementsByName("begindate")[0].value;
  var type = document.getElementsByName("type")[0].value;
  var timezone = document.getElementsByName("timezone")[0].value;
  var verified = document.getElementsByName("verified")[0].value;
  var event = document.getElementsByName("event")[0].value;
  
  url = server + "/get?org=" + org + "&enddate=" + enddate + "&begindate=" + begindate + "&type=" + type + "&timezone=" + timezone + "&event=" + event + "&verified=" + verified + "&f=pjson";
  
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
    //mymap.removeLayer(locationLayer);
    cluster.removeLayer(locationLayer)
    addLayerToMap(mymap, mapitems, types);
  });
  
}
	
new Pikaday({
  field: document.getElementById("enddate"),
  onSelect: function(date) {
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

new Pikaday({
  field: document.getElementById("begindate"),
  onSelect: function(date) {
    const year = date.getFullYear(),
    month = date.getMonth() + 1,
    day = date.getDate(),
    formattedDate = [
      year,
      month < 10 ? "0" + month : month,
      day < 10 ? "0" + day : day
    ].join("-");
    document.getElementById("begindate").value = formattedDate;
  }
});

var mytimezone=jstz.determine().name();
//var jsonurl = php_vars.server + '/get?org=' + php_vars.org + '&f=pjson&timezone=' + mytimezone;
var jsonurl = server + '/get?org=' + php_vars.org + '&f=pjson&timezone=' + mytimezone;

(function(d, script) {
    script = d.createElement('script');
    script.type = 'text/javascript';
    script.async = true;
    script.onload = function(){
        addLayerToMap(mymap, mapitems, types);
    };
    script.src = jsonurl;
    script.id = 'jsonfile';
    d.getElementsByTagName('head')[0].appendChild(script);
}(document));


qform.elements.timezone.value = mytimezone

