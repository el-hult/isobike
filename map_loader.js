function initialize() {
  var myLatlng = new google.maps.LatLng(59.332144,18.066365);
  var mapOptions = {
    zoom: 12,
    center: myLatlng
  }
  var map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);

  map.data.loadGeoJson('bike_times_16.geojson');

  map.data.setStyle(function(feature) {
    var bike_time = feature.getProperty('Biking time [s]');
    var color = 'red';
    var opacity = .1
      if( bike_time < 35*60 ){ color='orange'};
      if( bike_time < 30*60 ){ color='orange'};
      if( bike_time < 25*60 ){ color='orange'};
      if( bike_time < 20*60 ){ color='orange'};
      if( bike_time < 15*60 ){ color='teal'};
      if( bike_time == -1){ opacity = 1};
    
    return {
      icon: {
        path: google.maps.SymbolPath.CIRCLE,
        scale: 6,
        strokeWeight: 1,
        fillColor: color,
        fillOpacity: opacity
      }
    }
  })

  map.data.addListener('click', function(event) {

    event.feature.forEachProperty(function(value,property) {
        console.log(property,':',value);
    });

  });
}

google.maps.event.addDomListener(window, 'load', initialize);