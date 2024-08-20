function map() {
    //data passed from the template
    var flight1 = null, flight2 = null;
    document.addEventListener('DOMContentLoaded', function() {
        var myElement = document.getElementById('map');
        flights_data = Object.values(JSON.parse(myElement.getAttribute('data-flights'))); //converts into array of objects

        //intialzing map into the html div tag with id map

        const map = new google.maps.Map(document.getElementById("map"), {
            zoom: 5,
            center: { lat: 39.84937875926634, lng: -100.11546319759957 },
            mapTypeId: "terrain",
        });

        flightPlanCoordinates = [];

        flights_data.forEach(flight =>{
            const data = [
                { lat: parseFloat(flight.departure_location_latitude), lng: parseFloat(flight.departure_location_longitude), name: flight.departure_location, dep_time: flight.departure_time },
                { lat: parseFloat(flight.layover_location_latitude), lng: parseFloat(flight.layover_location_longitude), name: flight.layover_location },
                { lat: parseFloat(flight.arrival_location_latitude), lng: parseFloat(flight.arrival_location_longitude), name: flight.arrival_location, arr_time: flight.arrival_time },
            ]
            flightPlanCoordinates.push(data);
        });
    
    
        //creates path

        flightPaths = [];

        flightPlanCoordinates.forEach(flight =>{
            const path = new google.maps.Polyline({
                path: flight,
                geodesic: true,
                strokeColor: getRandomColor(),
                strokeOpacity: 1.0,
                strokeWeight: 3,
            });
            flightPaths.push(path);
        })    
    
        //creates markers

        flightPlanCoordinates.forEach(coords => {
            coords.forEach((coord, index) => {
                new google.maps.Marker({
                    position: {lat: parseFloat(coord.lat), lng: parseFloat(coord.lng)},
                    map: map,
                    title: coord.name,
                    label: (index + 1).toString(),
                });
            });
        });
    
      
        flightPaths.forEach(path =>{
            path.setMap(map);
        })
    
        // To display information of flight path
    
        //Flight 1
    
        //information overlay
        // const infoOverlay1 = new google.maps.OverlayView();
        // infoOverlay1.draw = function() {
        //     const projection = this.getProjection();
        //     const centerPixel = projection.fromLatLngToDivPixel(flightPlan1Coordinates[1]);
    
        //     const infoElement = document.createElement('div');
        //     infoElement.className = 'info-box';
        //     infoElement.style.position = 'absolute';
        //     infoElement.style.left = centerPixel.x  + 'px';
        //     infoElement.style.top = centerPixel.y + 'px';
        //     infoElement.innerHTML = `<div><b>${'Dep: ',new Date(flight1.departure_time),'Arr: ',flight1.arrival_time,'Price: $',flight1.price}<b></div>`;
        //     infoElement.style.zIndex = '100';
        //     infoElement.style.fontSize = 'large';
        //     infoElement.style.color = '#ff3333';
    
    
        //     this.getPanes().overlayLayer.appendChild(infoElement);
        // };
        // infoOverlay1.setMap(map);
    
        // // Flight 2
    
        // //overlay information
        // const infoOverlay2 = new google.maps.OverlayView();
        // infoOverlay2.draw = function() {
        //     const projection = this.getProjection();
        //     const centerPixel = projection.fromLatLngToDivPixel(flightPlan2Coordinates[1]);
    
        //     const infoElement = document.createElement('div');
        //     infoElement.className = 'info-box';
        //     infoElement.style.position = 'absolute';
        //     infoElement.style.left = centerPixel.x + 'px';
        //     infoElement.style.top = centerPixel.y + 'px';
        //     infoElement.innerHTML = `<div><b>${'Dep: ',flight2.departure_time,'Arr: ',flight2.arrival_time,'Price: $',flight2.price}<b></div>`;
        //     infoElement.style.zIndex = '100';
        //     infoElement.style.fontSize = 'large';
        //     infoElement.style.color = '#ff3333';
    
        //     this.getPanes().overlayLayer.appendChild(infoElement);
        // };
        // infoOverlay2.setMap(map);
    });
    

}

// Function to generate a random hexadecimal color
function getRandomColor() {
    // Generate random values for red, green, and blue components
    const red = Math.floor(Math.random() * 256);
    const green = Math.floor(Math.random() * 256);
    const blue = Math.floor(Math.random() * 256);
  
    // Convert the RGB values to hexadecimal format
    const redHex = red.toString(16).padStart(2, '0');
    const greenHex = green.toString(16).padStart(2, '0');
    const blueHex = blue.toString(16).padStart(2, '0');
  
    // Construct the hexadecimal color string
    const hexColor = `#${redHex}${greenHex}${blueHex}`;
  
    return hexColor;
  }

map();
  
