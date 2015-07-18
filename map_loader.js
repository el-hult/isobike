function initialize() {
  var myLatlng = new google.maps.LatLng(59.332144,18.066365);
  var mapOptions = {
    zoom: 13,
    center: myLatlng
  }
  var map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);

  map.data.loadGeoJson('bike_times_50.geojson');
  map.data.loadGeoJson('level_sets_50.geojson');

  map.data.setStyle(function(feature) {

  var bike_time = feature.getProperty('Biking time [s]');
  var color = 'white';
  if( bike_time <= 30*60 ){ color='black'};
  if( bike_time <= 25*60 ){ color='red'};
  if( bike_time <= 20*60 ){ color='blue'};
  if( bike_time <= 15*60 ){ color='yellow'};
  if( bike_time <= 10*60 ){ color='green'};
  if( bike_time <= 5*60 ){ color='orange'};
  var zIndex = 100000 - bike_time

    if(feature.getGeometry().getType() == 'Point'){

      var opacity = .4
      if( bike_time < 0 ){ color='black'};
      if( bike_time == -1){ opacity = .1};

      return {
        icon: {
          path: google.maps.SymbolPath.CIRCLE,
          scale: 2,
          strokeWeight: 0,
          fillColor: color,
          fillOpacity: opacity,
          zIndex: zIndex
        }
      }
    } else if (feature.getGeometry().getType() == 'Polygon'){
      return { 
        fillColor: color,
        strokeColor: color,
        fillOpacity: 0,
        strokeOpacity: .9,
        strokeWeight: .9,
        zIndex: zIndex
      }
    } else if (feature.getGeometry().getType() == 'LineString'){
      return { 
        strokeColor: color,
        strokeOpacity: 0.9,
        strokeWeight: .9,
        zIndex: zIndex
      }
    }
  })

  

  var infoWindow = new google.maps.InfoWindow();

map.data.addListener('click', function(event) {

  var featureType = event.feature.getGeometry().getType()

  if (featureType == 'Polygon') {


  infoWindow.setPosition(event.latLng)
  infoWindow.open(map);
  travelTime = String(Math.round(event.feature.getProperty('Biking time [s]') / 60))

  infoWindow.setContent('Zone: '+travelTime+' mins');

} else if (featureType == 'Point') {

  infoWindow.setPosition(event.latLng)
  infoWindow.open(map);
  travelTime = String(Math.round(event.feature.getProperty('Biking time [s]') / 60))

  infoWindow.setContent('Node: '+travelTime+' mins');
}

  event.feature.forEachProperty(function(value,property) {
    console.log(property,':',value);
  });

});
}

google.maps.event.addDomListener(window, 'load', initialize);