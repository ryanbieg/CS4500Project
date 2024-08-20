//code adapted from that found at https://www.w3schools.com/howto/howto_js_autocomplete.asp
//function that runs autocomplete fill
function autocomplete(dataField, arr, cities, icaos) {
    var currentFocus;
    //when someone writes in text field
    dataField.addEventListener("input", function(e) {
        var containerDiv, flightDiv, i, val = this.value;
        //close any already open lists of autocompleted values
        closeAllLists();
        if (!val) { return false;}
        currentFocus = -1;
        //create a DIV element that will contain the items (values)
        containerDiv = document.createElement("DIV");
        containerDiv.setAttribute("id", this.id + "autocomplete-list");
        containerDiv.setAttribute("class", "autocomplete-items");
        this.parentNode.appendChild(containerDiv);
        for (i = 0; i < arr.length; i++) {
            //check if the item starts with the same letters as the text field value:
            if (val.length > 2 && arr[i].substr(7, val.length).toUpperCase() == val.toUpperCase()) { 
                flightDiv = document.createElement("DIV");

                //highlights matching part of city
                flightDiv.innerHTML = arr[i].substr(0,7);
                flightDiv.innerHTML += "<strong>" + arr[i].substr(7, val.length) + "</strong>";
                flightDiv.innerHTML += arr[i].substr(7 + val.length);
                
                flightDiv.innerHTML += "<input type='hidden' value='" + arr[i] + "'>";
                //when someone clicks on specific flight
                flightDiv.addEventListener("click", function(e) {
                    dataField.value = this.getElementsByTagName("input")[0].value;
                    closeAllLists();
                });
                
                containerDiv.appendChild(flightDiv);
            }
            else if (val.length <= 4 && icaos[i].substr(0, val.length).toUpperCase() == val.toUpperCase()){
                flightDiv = document.createElement("DIV");
                //highlights matching ICAO code
                flightDiv.innerHTML = "<strong>" + arr[i].substr(0, val.length) + "</strong>" + arr[i].substr(val.length);

                flightDiv.innerHTML += "<input type='hidden' value='" + arr[i] + "'>";
                //when someone clicks on specific flight
                flightDiv.addEventListener("click", function(e) {
                    dataField.value = this.getElementsByTagName("input")[0].value;
                    closeAllLists();
                });
                containerDiv.appendChild(flightDiv);
            } 
            else if(val.length > 2 && cities[i].toUpperCase().includes(val.toUpperCase())) {
                flightDiv = document.createElement("DIV");
                //adds matching flight to list
                flightDiv.innerHTML = arr[i];

                flightDiv.innerHTML += "<input type='hidden' value='" + arr[i] + "'>";
                //when someone clicks on specific flight
                flightDiv.addEventListener("click", function(e) {
                    dataField.value = this.getElementsByTagName("input")[0].value;
                    closeAllLists();
                });
                
                containerDiv.appendChild(flightDiv);
            }
        }
    });
    //keyboard press
    dataField.addEventListener("keydown", function(e) {
        var x = document.getElementById(this.id + "autocomplete-list");
        if (x) x = x.getElementsByTagName("div");
        //down arrow
        if (e.keyCode == 40) {
            currentFocus++;
            addActive(x);
        //up arrow
        } else if (e.keyCode == 38) { //up
            currentFocus--;
            addActive(x);
        //enter
        } else if (e.keyCode == 13) {
            e.preventDefault();
            if (currentFocus > -1) {
            if (x) x[currentFocus].click();
            }
        }
    });
    function addActive(x) {
        /*a function to classify an item as "active":*/
        if (!x) return false;
        /*start by removing the "active" class on all items:*/
        removeActive(x);
        if (currentFocus >= x.length) currentFocus = 0;
        if (currentFocus < 0) currentFocus = (x.length - 1);
        /*add class "autocomplete-active":*/
        x[currentFocus].classList.add("autocomplete-active");
    }
    function removeActive(x) {
        /*a function to remove the "active" class from all autocomplete items:*/
        for (var i = 0; i < x.length; i++) {
        x[i].classList.remove("autocomplete-active");
        }
    }
    function closeAllLists(elmnt) {
        /*close all autocomplete lists in the document,
        except the one passed as an argument:*/
        var x = document.getElementsByClassName("autocomplete-items");
        for (var i = 0; i < x.length; i++) {
        if (elmnt != x[i] && elmnt != dataField) {
            x[i].parentNode.removeChild(x[i]);
        }
        }
    }
    /*execute a function when someone clicks in the document:*/
    document.addEventListener("click", function (e) {
        closeAllLists(e.target);
    });

}
//gets all data from csv file
const arr = [];
const cities = [];
const icaos = [];
const filePath = "/static/data/airport-codes.csv"; 
fetch(filePath)
    .then(response => response.text())
    .then(data => {
        const rows = data.split('\n');
        for (const row of rows) {
            const columns = row.split(',');
            //filters out non airports and closed airports, adds ICAO code to front of airport
            if (columns.length >= 12 && columns[1].includes('airport') && !columns[1].includes('closed')) {
                const flight = columns[0] + " - " + columns[2];
                const city = columns[7];
                const icao = columns[0];
                arr.push(flight);
                cities.push(city);
                icaos.push(icao);
            }
        }
    }).catch(error => console.error('Error fetching data:', error));

document.addEventListener("DOMContentLoaded", function() {
    autocomplete(document.getElementById("departureInput"), arr, cities, icaos);
    autocomplete(document.getElementById("arrivalInput"), arr, cities, icaos);
});