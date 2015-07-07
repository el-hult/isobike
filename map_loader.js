function initialize() {
  var myLatlng = new google.maps.LatLng(59.332144,18.066365);
  var mapOptions = {
    zoom: 12,
    center: myLatlng
  }
  var map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);


    
var    x1 = 59.29;
var    x2 = 59.40;
var    y1  = 17.98;
var    y2  = 18.15;
var dx = x2-x1;
var dy = y2-y1;

for (i = 0; i < 10; i++) { 
  for (j = 0; j <10; j++) {
      var markLatlng = new google.maps.LatLng(x1+i*dx/10,y1+j*dy/10)
      new google.maps.Marker({
	  position: markLatlng,
	  map: map
      });
  }
}
  

}

google.maps.event.addDomListener(window, 'load', initialize);
