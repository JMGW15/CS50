// Google Map
var map;

// markers for map
var markers = [];

// info window
var info = new google.maps.InfoWindow();


// execute when the DOM is fully loaded
$(function() {

    // styles for map
    // https://developers.google.com/maps/documentation/javascript/styling
    var styles = [

        // hide Google's labels
        {
            featureType: "all",
            elementType: "labels",
            stylers: [
                {visibility: "off"}
            ]
        },

        // hide roads
        {
            featureType: "road",
            elementType: "geometry",
            stylers: [
                {visibility: "off"}
            ]
        }

    ];

    // options for map
    // https://developers.google.com/maps/documentation/javascript/reference#MapOptions
    var options = {
        center: {lat: 47.9445, lng: -122.3046}, // Mukilteo, WA
        disableDefaultUI: true,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        maxZoom: 14,
        panControl: true,
        styles: styles,
        zoom: 13,
        zoomControl: true
    };

    // get DOM node in which map will be instantiated
    var canvas = $("#map-canvas").get(0);

    // instantiate map
    map = new google.maps.Map(canvas, options);

    // configure UI once Google Map is idle (i.e., loaded)
    google.maps.event.addListenerOnce(map, "idle", configure);

});

/**
 * Adds marker for place to map.
 */
function addMarker(place)  //update to pull in article
{
    // create variable to capture location based on google documentation and the lat/long referenced above in anonymous function 
    var myLatLng = new google.maps.LatLng(place["latitude"], place["longitude"]);
    // create variable for place_city to be used in infowindow header
    var place_city = (" " + place["place_name"]); 
    
    
    //scale image https://stackoverflow.com/questions/32062849/modify-my-custom-marker-image-size-for-my-google-map
    var icon = {
        url: 'https://cdn4.iconfinder.com/data/icons/navigation-2/500/Base_base_marker_gps_location_map_map_marker_place-512.png', 
        scaledSize : new google.maps.Size(50, 50)
    };
        
    // create marker - https://developers.google.com/maps/documentation/javascript/examples/marker-simple
    var marker = new google.maps.Marker({
        position: myLatLng,
        map: map,
        icon: icon,
    });
    
    
    // get articles for place using code found in line 187 of the search function
    // upon success call a function called news
    $.getJSON(Flask.url_for("articles"), {geo: place.postal_code}, function(news) {
        
        // if the function news doesn't return an empty JSON object - https://api.jquery.com/jQuery.isEmptyObject/
        if (!$.isEmptyObject(news))
        {			
			// create content variable and build html, calling in place_city for header
            var newsContent = "<div><h4>News from" + place_city + "</h4><ul>";
            // look over each item in the object returned -https://stackoverflow.com/questions/9887009/how-do-i-iterate-through-this-json-object-in-jquery
            for (var i = 0; i < news.length; i++)
            {
				//finish HTML with Key/value pairs from the returned JSON
            	newsContent += "<li><a target='_NEW' href='" + news[i].link
            	+ "'>" + news[i].title + "</a></li>";
            }
        }
        
        // add the closing tag to the HTML
		newsContent += "</div></ul>";
		
		// listen for clicks on marker per google documentation
		// for click on marker show infowindow inserting newsContent
        google.maps.event.addListener(marker, 'click', function() {
            showInfo(marker, newsContent);
		});
	
    });
    // add marker to the array markers to be able to clear the markers later in the delete markers function
    markers.push(marker);
}

// Deletes all markers in the array by removing references to them.  function is called in HTML
function removeMarkers() 
//for all the markers included in the array marker, set them to null
{
    for(i=0; i<markers.length; i++){
        markers[i].setMap(null);
    }
}

/**
 * Configures application.
 */
 
function configure()
{
    // update UI after map has been dragged
    google.maps.event.addListener(map, "dragend", function() {

        // if info window isn't open
        // http://stackoverflow.com/a/12410385
        if (!info.getMap || !info.getMap())
        {
            update();
        }
    });

    // update UI after zoom level changes
    google.maps.event.addListener(map, "zoom_changed", function() {
        update();
    });

    // configure typeahead
    $("#q").typeahead({
        highlight: false,
        minLength: 1
    },
    {
        display: function(suggestion) { return null; },
        limit: 10,
        source: search,
        templates: {
            suggestion: Handlebars.compile(
            "<div>{{place_name}}, {{admin_name1}}, {{postal_code}}</div>" //why so slow
            )
        }
    });

    // re-center map after place is selected from drop-down
    $("#q").on("typeahead:selected", function(eventObject, suggestion, name) {

        // set map's center
        map.setCenter({lat: parseFloat(suggestion.latitude), lng: parseFloat(suggestion.longitude)});

        // update UI
        update();
    });

    // hide info window when text box has focus
    $("#q").focus(function(eventData) {
        info.close();
    });

    // re-enable ctrl- and right-clicking (and thus Inspect Element) on Google Map
    // https://chrome.google.com/webstore/detail/allow-right-click/hompjdfbfmmmgflfjdlnkohcplmboaeo?hl=en
    document.addEventListener("contextmenu", function(event) {
        event.returnValue = true; 
        event.stopPropagation && event.stopPropagation(); 
        event.cancelBubble && event.cancelBubble();
    }, true);

    // update UI
    update();

    // give focus to text box
    $("#q").focus();
}


/**
 * Searches database for typeahead's suggestions.
 */
function search(query, syncResults, asyncResults)
{
    // get places matching query (asynchronously)
    var parameters = {
        q: query
    };
    $.getJSON(Flask.url_for("search"), parameters)
    .done(function(data, textStatus, jqXHR) {
     
        // call typeahead's callback with search results (i.e., places)
        asyncResults(data);
    })
    .fail(function(jqXHR, textStatus, errorThrown) {

        // log error to browser's console
        console.log(errorThrown.toString());

        // call typeahead's callback with no results
        asyncResults([]);
    });
}

/**
 * Shows info window at marker with content.
 */
function showInfo(marker, content)
{
    // start div
    var div = "<div id='info'>";
    if (typeof(content) == "undefined")
    {
        // http://www.ajaxload.info/
        div += "<img alt='loading' src='/static/ajax-loader.gif'/>";
    }
    else
    {
        div += content;
    }

    // end div
    div += "</div>";

    // set info window's content
    info.setContent(div);

    // open info window (if not already open)
    info.open(map, marker);
}

/**
 * Updates UI's markers.
 */
function update() 
{
    // get map's bounds
    var bounds = map.getBounds();
    var ne = bounds.getNorthEast();
    var sw = bounds.getSouthWest();

    // get places within bounds (asynchronously)
    var parameters = {
        ne: ne.lat() + "," + ne.lng(),
        q: $("#q").val(),
        sw: sw.lat() + "," + sw.lng()
    };
    $.getJSON(Flask.url_for("update"), parameters)
    .done(function(data, textStatus, jqXHR) {

       // remove old markers from map
       removeMarkers();

       // add new markers to map
       for (var i = 0; i < data.length; i++)
       {
           addMarker(data[i]);
       }
    })
    .fail(function(jqXHR, textStatus, errorThrown) {

        // log error to browser's console
        console.log(errorThrown.toString());
    });
};
