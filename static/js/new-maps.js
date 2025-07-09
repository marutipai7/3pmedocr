
// 1 variable with multiple theme colors
const themeColors = {
customers: 'vivid-orange',
Advertiser: 'living-coral',
NGO:'violet-sky',
pharmacy:'light-sea-green',
client:'dark-blue'
};

// Get the current path
const path = window.location.pathname;

// Default color
let selectedColor = '#F79E1B';
let bgColor;

// Loop and match theme by keyword in path
$.each(themeColors, function(keyword, color) {
if (path.includes(keyword)) {
    selectedColor = color;
    bgColor = selectedColor == "vivid-orange" 
    ? "#F79E1B" 
    : selectedColor == "living-coral" 
    ? "#FF6F61" 
    : selectedColor == "light-sea-green"
    ? "#3AAFA9"
    : selectedColor == "dark-blue"
    ? "#123456"
    : "#6B79F5";
    return false;
}
});

// Declare global variables for map, location coordinates, markers, and places
let map;
let currentLat, currentLon;
let savedPlaces = [];
let searchHistory = [];
let activeMarkers = [];
allFetchedPlaces = [];
let routeLines = [];
let lastLat, lastLon, lastPlace;
let routingControl;
let currentMode = "auto";

// Define tags to query different types of healthcare amenities
const amenityTags = {
    hospital: 'hospital',
    doctor: 'doctors',
    pharmacy: 'pharmacy',
    lab: 'laboratory'
};

// Define custom Leaflet icons for different amenity types
const icons = {
hospital: L.icon({
    iconUrl: '/static/images/hospital-marker.svg',
    iconSize: [30, 30],
    iconAnchor: [15, 30],
    popupAnchor: [0, -30]
}),
doctor: L.icon({
    iconUrl: '/static/images/doctor-marker.svg',
    iconSize: [30, 30],
    iconAnchor: [15, 30],
    popupAnchor: [0, -30]
}),
pharmacy: L.icon({
    iconUrl: '/static/images/pharmacy-marker.svg',
    iconSize: [30, 30],
    iconAnchor: [15, 30],
    popupAnchor: [0, -30]
}),
lab: L.icon({
    iconUrl: '/static/images/lab-marker.svg',
    iconSize: [30, 30],
    iconAnchor: [15, 30],
    popupAnchor: [0, -30]
})
};

$(document).ready(function () {
if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(showLocation, showError);
} else {
    window.showToaster('error', 'Geolocation not supported by your browser.');
}

// Initialize map with user's location
function showLocation(position) {
    currentLat = position.coords.latitude;
    currentLon = position.coords.longitude;

    map = L.map("map").setView([currentLat, currentLon], 15);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    }).addTo(map);

    L.marker([currentLat, currentLon])
    .addTo(map)
    .bindPopup("You are here")
    .openPopup();
}

function showError(error) {
    window.showToaster('error', "Error getting location: " + error.message);
}

function clearMarkers() {
    activeMarkers.forEach(marker => map.removeLayer(marker));
    activeMarkers = [];
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
            }
        }
    }
    return cookieValue;
}

function fetchPlaces(type, buttonElement) {
    $(".map-search-btn").removeClass(function(index, className) {
    return (className.match(/(^|\s)bg-\S+/g) || []).join(' ');
    });
    $(".map-search-btn").removeAttr("style");
    $(buttonElement).css('background-color', bgColor);
    $(buttonElement).css('color', 'white');

    if (!currentLat || !currentLon) {
    window.showToaster('error', "Location not yet available");
    return;
    }

    clearMarkers();
    allFetchedPlaces = [];

    fetch("get_places/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({
            lat: currentLat,
            lng: currentLon,
            type: type,
            range: 500  // you can increase to 5000 if needed
        }),
    })
    .then((res) => res.json())
    .then((data) => {
        if (data?.amenities?.length > 0) {
        data.amenities.forEach((place) => {
            console.log("Place data:", place);
            const lat = place.latitude;
            const lon = place.longitude;

            // Only add marker if valid coordinates
            if (typeof lat === "number" && typeof lon === "number") {
            const marker = L.marker([lat, lon], {
                icon: icons[type],
            })
                .addTo(map)
                .bindPopup(`
                <strong>${place.title}</strong><br>
                ${place.address ? place.address + "<br>" : ""}
                Phone: ${place.phone_number || ""}
                `);

            const formattedPlace = {
                mongo_id: place.mongo_id,
                name: place.title,
                type: type,
                lat: place.latitude,
                lon: place.longitude,
                address: place.address,
                phone: place.phone_number,
                rating: place.rating || "0 stars",
                reviews: place.reviews || "0 reviews",
                website: place.website,
                tags: place.tags || {}
            };

            allFetchedPlaces.push(formattedPlace);
            activeMarkers.push(marker);
            }
        });
        } else {
        window.showToaster("error", `No ${type}s found nearby.`);
        }

    })
    .catch((err) => {
        console.error("Fetch error:", err);
        window.showToaster("error", `Failed to load nearby ${type}s.`);
    });
}

// Event handlers for amenity buttons
$(".map-search-btn:contains('Hospital')").on("click", function () {
    fetchPlaces("hospital", this);
});
$(".map-search-btn:contains('Doctor')").on("click", function () {
    fetchPlaces("doctor", this);
});
$(".map-search-btn:contains('Pharmacy')").on("click", function () {
    fetchPlaces("pharmacy", this);
});
$(".map-search-btn:contains('Lab')").on("click", function () {
    fetchPlaces("lab", this);
});

// Handle view toggling between map and list
$(".map-view").fadeIn(300);
$(".listview").hide();

$('.view-toggle').change(function () {
    const isChecked = $(this).is(":checked");
    $('.view-toggle').prop('checked', isChecked);

    if (isChecked) {
    $(".listview").fadeOut(200, function () {
        $(".map-view").fadeIn(300);
    });
    } else {
    $(".map-view").fadeOut(200, function () {
        $(".listview").fadeIn(300);
    });
    }
});

// Handle text search input
const $searchBox = $(".map-view input[type='text']");
const $suggestionBox = $("<div class='mt-14 max-h-[73vh] overflow-y-auto scroll'></div>").hide();
$(".suggestion").append($suggestionBox);

const $bookmarkIcon = $(".bookmark-icon");
const $historyIcon = $(".history-icon");
const $closeIcon = $(".close-icon");

$searchBox.on("input", function () {
    $(".map-search").css('background-color', bgColor);
    const query = $(this).val().toLowerCase();
    $suggestionBox.empty();

    if (query) {
        $bookmarkIcon.addClass("!hidden");
        $historyIcon.addClass("!hidden");
        $closeIcon.removeClass("!hidden");
        $(".map-search").addClass("placeholder:text-white");
        $(".map-search,.search,.close-icon").addClass("text-white");
    } else {
        $bookmarkIcon.removeClass("!hidden");
        $historyIcon.removeClass("!hidden");
        $closeIcon.addClass("!hidden");
        $(".map-search").removeAttr("style");
        $(".map-search,.search,.close-icon").removeClass("text-white");
        $(".map-search").removeClass("placeholder:text-white");
        $suggestionBox.hide();
        return;
    }

    fetch("search/", {
        method: "POST",
        headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({
        q: query,
        lat: currentLat,
        lng: currentLon
        })
    })
    .then(res => res.json())
    .then(data => {
        const matches = data.results || [];
        const places = data.places || [];

        if (!matches.length && !places.length) {
            $suggestionBox.html("<p class='p-2'>No Suggestion Found...</p>").show();
            return;
        }
    
        console.log("Search results:\n");
        console.log("Matches:", matches, "\n", "Places:", places);

    [...matches].forEach(place => {
        const lat = place.latitude;
        const lon = place.longitude;
        const name = place.title || place.name;
        const avgRating = place.rating;
        const stars = avgRating
        ? '★'.repeat(Math.floor(avgRating)) + '☆'.repeat(5 - Math.floor(avgRating))
        : '★★★☆☆';

        const $item = $(`
            <div class="px-4 py-3 border-b border-${selectedColor} last:border-b-0 cursor-pointer transition-all hover:bg-opacity-10">
                <div class="flex flex-col gap-2">
                <p class="text-lg font-semibold">${place.title}</p>
                <p class="flex gap-2 items-center"> ${place.rating} <span class="text-xl text-star-orange">${stars}</span> ${place.reviews}}</p>
                <p>${place.type}</p>
                <p class="text-sm">${place.address}</p>
                <p class="text-sm">${place.phone_number}</p>
                <p class="text-sm">${place.email }</p>
                </div>
                <div class="ml-4 flex justify-between mt-2">
                <button class="flex flex-col gap-2 text-xs cursor-pointer" data-lat="${place.latitude}" data-lon="${place.longitude}">
                    <span class='material-symbols-outlined material-filled !text-xl !font-semibold'>directions</span><span>Directions</span>
                </button>
                <a href="tel:${place.phone_number}" title="Call" class="flex flex-col gap-2 text-xs cursor-pointer">
                    <span class='material-symbols-outlined material-filled !text-xl !font-semibold'>call</span><span>Call</span></a>
                <button class="flex flex-col gap-2 text-xs cursor-pointer" data-name="${encodeURIComponent(place.title)}">
                    <span class='material-symbols-outlined material-filled !text-xl !font-semibold'>share</span><span>Share</span>
                </button>
                </div>
            </div>
        `);

        $item.find("button:contains('Directions')").on("click", function (e) {
            e.stopPropagation();
            showDirections(lat, lon, place);
            });

            $item.on("click", function () {
            $searchBox.val(name);
            const overviewHtml = `
                <div class="px-4 py-3 suggestion-detail">
                <div class="h-32 w-full bg-cover bg-center" 
                    style="background-image: url('${place.imageUrl || "/static/images/hospital.svg"}')">
                </div>
                <div class="flex flex-col gap-2 mt-2">
                    <div class="flex justify-between">
                    <p class="text-xl font-bold">${place.title}</p>
                    <span class="material-symbols-outlined bookmark-fill cursor-pointer" data-id="${place.mongo_id}" data-type="${place.type}">bookmark</span>
                    </div>
                    ${place.address ? `<p class="text-sm">${place.address}</p>` : ""}
                    ${place.phone_number ? `<p class="text-sm">${place.phone_number}</p>` : ""}
                    <p class="flex gap-2 items-center"> ${place.rating} <span class="text-xl text-star-orange">${stars + ` (${place.reviews})`}</span></p>
                    <p>${place.title}</p>
                </div>
                <!-- Tabs -->
                <div class="flex mb-3">
                    <button class="tab-button cursor-pointer text-sm px-4 py-2 focus:outline-none border-b-2 border-transparent hover:!border-${selectedColor}" style="border-color: ${bgColor}; color: ${bgColor};" data-tab="overview">Overview</button>
                    <button class="tab-button cursor-pointer text-sm px-4 py-2 focus:outline-none border-b-2 border-transparent hover:!border-${selectedColor}" data-tab="timings">Timings</button>
                </div>
                <div class="tab-content" id="overview">
                    <div class="ml-4 flex justify-between mt-2">
                    <button class="flex flex-col gap-2 text-xs cursor-pointer overviewDirections" data-lat="${place.latitude}" data-lon="${place.longitude}">
                        <span class='material-symbols-outlined material-filled !text-xl !font-semibold'>directions</span><span>Directions</span>
                    </button>
                    <a href="tel:${place.phone_number}" title="Call" class="flex flex-col gap-2 text-xs cursor-pointer">
                        <span class='material-symbols-outlined material-filled !text-xl !font-semibold'>call</span><span>Call</span></a>
                    <button class="flex flex-col gap-2 text-xs cursor-pointer" data-name="${encodeURIComponent(place.title)}">
                        <span class='material-symbols-outlined material-filled !text-xl !font-semibold'>share</span><span>Share</span>
                    </button>
                    </div>
                    <div class="flex flex-col gap-2 text-sm mt-4">
                    <p class="flex gap-2">                  
                        <span class="material-symbols-outlined text-${selectedColor}">location_on</span>
                        ${place.address || "Address not available"}
                    </p>
                    <p class="flex gap-2">                  
                        <span class="material-symbols-outlined text-${selectedColor}">call</span>
                        ${place.phone_number || "Phone number not available"}
                    </p>
                    <p class="flex gap-2">                  
                        <span class="material-symbols-outlined text-${selectedColor}">mail</span>
                        ${place.email || "Email not available"}
                    </p>
                    <p class="text-base font-semibold">Services</p>
                    <p>Ambulance Service</p>
                    <p>Anaesthesiology</p> // Need to make this dynamic
                    <p>Cancer</p>
                    <p>Dental Services</p>
                    <p>Emergency Care</p>
                    </div>
                </div>
                <div class="tab-content hidden" id="timings">
                    <p class="font-semibold">Open Now</p>
                    <ul class="text-sm flex flex-col gap-2 mt-2">
                    <li class="flex justify-between">Monday <span>Open 24 hours</span></li>
                    <li class="flex justify-between">Tuesday <span>Open 24 hours</span></li>
                    <li class="flex justify-between">Wednesday <span>Open 24 hours</span></li>
                    <li class="flex justify-between">Thursday <span>Open 24 hours</span></li>
                    <li class="flex justify-between">Friday <span>Open 24 hours</span></li>
                    <li class="flex justify-between">Saturday <span>Open 24 hours</span></li>
                    <li class="flex justify-between">Sunday <span>Open 24 hours</span></li>
                    </ul>
                </div>
                </div>
            `;

            $suggestionBox.on('click', '.tab-button', function () {
            const tab = $(this).data('tab');

            $suggestionBox.find('.tab-button').removeAttr("style");
                $(this).css({'border-color': bgColor, 'color':bgColor});
                $suggestionBox.find('.tab-content').addClass('hidden');
                $suggestionBox.find(`#${tab}`).removeClass('hidden');
            });

            $suggestionBox.fadeOut(100, () => {
                $suggestionBox.html(overviewHtml).fadeIn(150);
            });

            map.setView([lat, lon], 17);
            L.popup()
                .setLatLng([lat, lon])
                .setContent(`<strong>${name}</strong>${place.address ? `<br>${place.address}` : ""}`)
                .openOn(map);

            $suggestionBox.on("click", "#backToSuggestions", () => {
                $searchBox.trigger("input");
            });

            $suggestionBox.on("click", ".overviewDirections", function (e) {
                e.stopPropagation();
                showDirections(lat, lon, place);
            });

            $suggestionBox.on("click", "#overviewShare", function () {
                const url = `${window.location.origin}?place=${encodeURIComponent(name)}`;
                navigator.clipboard.writeText(url);
                window.showToaster('error', "Place link copied to clipboard!");
            });
        });

        $suggestionBox.append($item);
    });
    // Add filter dropdown
    $suggestionBox.prepend(`<div class='flex justify-between p-2 border-b border-${selectedColor}'>
    <span class="font-semibold">Suggestion</span>
    <div class="relative">
        <span class="material-symbols-outlined cursor-pointer filterToggle">swap_vert</span>
        <div class="filterDropdown absolute right-0 mt-2 w-28 rounded-lg shadow-lg hidden z-50 bg-snow-gray p-2">
        <div class="relative">
            <p class="text-base font-normal cursor-pointer hover:bg-white p-2 filterItem" data-target="#sort">
            Sort by
            </p>
            <div id="sort" class="absolute right-full top-0 mr-2 w-38 rounded-lg shadow-lg bg-white p-2 hidden z-50">
            <p class="text-base font-normal p-2 cursor-pointer flex items-center gap-2">
                <span class="material-symbols-outlined">check</span>
                Open
            </p>
            <p class="text-base font-normal p-2 cursor-pointer flex items-center gap-2">
                <span class="material-symbols-outlined">check</span>
                Closed
            </p>
            <p class="text-base font-normal p-2 cursor-pointer flex items-center gap-2">
                <span class="material-symbols-outlined">check</span>
                Directions
            </p>
            </div>
        </div>
        <div class="relative">
            <p class="text-base font-normal cursor-pointer hover:bg-white p-2 filterItem" data-target="#service">
            Services
            </p>
            <div id="service" class="absolute right-full top-0 mr-2 w-38 rounded-lg shadow-lg bg-white p-2 hidden z-50">
            <p class="text-base font-normal p-2 cursor-pointer flex items-center gap-2">
                <span class="material-symbols-outlined">check</span>
                Open
            </p>
            <p class="text-base font-normal p-2 cursor-pointer flex items-center gap-2">
                <span class="material-symbols-outlined">check</span>
                Closed
            </p>
            <p class="text-base font-normal p-2 cursor-pointer flex items-center gap-2">
                <span class="material-symbols-outlined">check</span>
                Directions
            </p>
            </div>
        </div>          
        </div>
    </div>
    </div>`);
    $suggestionBox.show();
    })
    .catch(err => {
    console.error("Search error:", err);
    window.showToaster("error", "Failed to fetch search results.");
    });
});
$closeIcon.on("click", function () {
    $searchBox.val("").trigger("input");
    $suggestionBox.hide();
});

// Filter dropdown toggle behavior
$(document).on('click', '.filterToggle', function (e) {
    e.stopPropagation();
    const $dropdown = $(this).siblings('.filterDropdown');
    $('.filterDropdown').not($dropdown).hide();
    $dropdown.toggle();
    $dropdown.find('.absolute').hide(); 
});
$(document).on('click', '.filterItem', function (e) {
    e.stopPropagation();
    const target = $($(this).data('target'));
    $('.filterDropdown .absolute').not(target).hide(); 
    target.toggle();
});
$(document).on("click", function (e) {
    if (!$(e.target).closest(".map-view").length) {
        $suggestionBox.hide();
    }
});

// Handle Bookmark Click
$(".bookmark-icon").on("click", function (e) {
    e.stopPropagation();
    fetch("save_location/", {
        method: "GET",
        headers: { "X-CSRFToken": getCookie("csrftoken") }
    })
    .then(res => res.json())
    .then(data => {
        const saved = data.saved || [];
        const places = saved.map(p => ({
            mongo_id: p.mongo_id,
            name: p.title,
            lat: p.latitude,
            lon: p.longitude,
            address: p.address,
            phone: p.phone_number,
            reviews: p.reviews || 0,
            rating: p.rating || 0,
            type: p.type,
            isBookmarked: true
        }));
        savedPlaces = places;

        showFilteredSuggestions("Saved Locations", place =>
            places.find(p => p.lat === place.lat && p.lon === place.lon)
        );

        allFetchedPlaces = [...places];
    })
    .catch(err => {
        console.error("Error fetching saved:", err);
        window.showToaster("error", "Could not fetch saved locations.");
    });
});

// Handle History Click
$(".history-icon").on("click", function (e) {
    e.stopPropagation();
    fetch("search_history/", {
        method: "GET",
        headers: { "X-CSRFToken": getCookie("csrftoken") }
    })
    .then(res => res.json())
    .then(data => {
        const history = data.clicked_results || [];
        const places = history.map(p => ({
            mongo_id: p.mongo_id,
            name: p.title,
            lat: p.latitude,
            lon: p.longitude,
            address: p.address,
            phone: p.phone_number,
            reviews: p.reviews || 0,
            rating: p.rating || 0,
            type: p.type,
        }));
        searchHistory = places;

        showFilteredSuggestions("Recent Locations", place =>
        places.find(p => p.lat === place.lat && p.lon === place.lon)
        );

        allFetchedPlaces = [...places]; // Makes suggestions reusable
    })
    .catch(err => {
        console.error("Error fetching history:", err);
        window.showToaster("error", "Could not fetch recent searches.");
    });
});

// Reusable function for rendering filtered suggestions
function showFilteredSuggestions(title, filterFn) {
    const filteredPlaces = allFetchedPlaces.filter(filterFn);
    $suggestionBox.empty();
        $(".map-search").css('background-color', bgColor);
    $bookmarkIcon.addClass("!hidden");
    $historyIcon.addClass("!hidden");
    $closeIcon.removeClass("!hidden");
    $(".map-search,.search,.close-icon").addClass("text-white");
    $(".map-search").addClass("placeholder:text-white");

    $suggestionBox.append(`
        <div class='flex justify-between p-2 border-b border-${selectedColor}'>
        <span>${title}</span>
        <span class="material-symbols-outlined">swap_vert</span>
        <div class="flex gap-2 items-center">
            See All<span class="material-symbols-outlined">keyboard_arrow_right</span>
        </div>
        </div>
    `);

    filteredPlaces.forEach(place => {
        const avgRating = place.rating;
        const stars = avgRating
        ? '★'.repeat(Math.floor(avgRating)) + '☆'.repeat(5 - Math.floor(avgRating))
        : '★★★☆☆';
        const $item = $(`<div class="px-4 py-3 border-b border-${selectedColor} cursor-pointer transition-all hover:bg-opacity-10">
        <div class="flex flex-col gap-2">
            <p class="text-lg font-semibold">${place.title}</p>
            <p class="flex gap-2 items-center"><span class="text-xl text-star-orange">${stars + ` (${avgRating})`}</span></p>
            <p class="text-sm text-light-gray">${place.address || "Unknown address"}</p>
        </div>
        <span class="material-symbols-outlined text-red-500 cursor-pointer remove-icon" title="Remove">delete</span>
        </div>`);
        $item.on("click", function () {
        $searchBox.val(place.name);
        });
        $item.find(".remove-icon").on("click", function (e) {
            e.stopPropagation();
            const payload = {
                mongo_id: place.mongo_id,
                amenity_type: place.type
            };
            const endpoint = place.isHistory ? "remove_search_history/" : "remove_saved_location/";
            fetch(endpoint, {
                method: "POST",
                headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify(payload)
            })
            .then(res => res.json())
            .then(data => {
                window.showToaster("success", data.message || "Removed successfully.");
                $item.remove(); // Remove from UI
            })
            .catch(err => {
                console.error("Removal error:", err);
                window.showToaster("error", "Could not remove the item.");
            });
        });
        $suggestionBox.append($item);
    });
    $suggestionBox.show();
}

// List view behavior
$('.cards').addClass('hidden');
$('.list-search-btn').on('click', function () {
    $(".list-search-btn").removeClass(function(index, className) {
    return (className.match(/(^|\s)bg-\S+/g) || []).join(' ');
    });
    $(".list-search-btn").removeAttr("style");
    $(this).css('background-color', bgColor);
    $(this).css('color', 'white');
    $('.placeholder').addClass('hidden');
    $('.cards').removeClass('hidden');
});

// Pagination logic for list view
const cardsPerPage = 3;
const cards = $(".places-card");
const totalCards = cards.length;
const totalPages = Math.ceil(totalCards / cardsPerPage);

function showPage(page) {
    cards.hide();
    const start = (page - 1) * cardsPerPage;
    const end = start + cardsPerPage;
    cards.slice(start, end).show();

    $("#pagination button").removeClass("font-semibold").removeAttr("style");
    $(`#pagination button[data-page='${page}']`).addClass("font-semibold").css({"background-color":bgColor, "color":"white"});
}
let paginationHTML = `
    <div class="flex items-center gap-4">
    <p class="text-dark-gray cursor-pointer" id="prev">Previous</p>
`;
for (let i = 1; i <= totalPages; i++) {
    paginationHTML += `
    <button 
        data-page="${i}" 
        class="px-4 py-2 rounded-lg cursor-pointer bg-pagination text-jet-black hover:!bg-${selectedColor} hover:transition"
    >
        ${i}
    </button>
    `;
}
paginationHTML += `
    <p class="text-dark-gray cursor-pointer" id="next">Next</p>
    </div>
`;
$("#pagination").html(paginationHTML);

$("#pagination").on("click", "button", function () {
    const page = $(this).data("page");
    currentPage = page;
    showPage(page);
});
let currentPage = 1;

$("#pagination").on("click", "#prev", function () {
    if (currentPage > 1) {
    currentPage--;
    showPage(currentPage);
    }
});

$("#pagination").on("click", "#next", function () {
    if (currentPage < totalPages) {
    currentPage++;
    showPage(currentPage);
    }
});

showPage(currentPage);
$(document).on("click", ".bookmark-fill", function () {
    const $btn = $(this);
    const mongo_id = $btn.data("id");
    const type = $btn.data("type");
    console.log(mongo_id, type)

    if (!mongo_id || !type) return;

    fetch("save_location/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({ mongo_id, type })
        })
        .then(res => res.json())
        .then(data => {
        if (data.created) {
            $btn.html("bookmark");
            $btn.addClass(`material-filled text-${selectedColor}`);
            window.showToaster("success", "Saved to bookmarks!");
        } else {
            window.showToaster("info", "Already bookmarked.");
        }
    })
    .catch(() => {
        window.showToaster("error", "Could not save bookmark.");
    });
    $(this).addClass(`material-filled text-${selectedColor}`);
});

// Render step-by-step directions
function renderSteps(steps) {
    const html = steps.map(s => `
        <div class="flex items-start justify-between">
            <span class="material-symbols-outlined pl-1 text-${selectedColor}">navigate</span>
            <div class="flex flex-col">
            <span class="font-medium">${s.instruction}</span>
            <div class="text-xs text-light-gray">
                ${(s.length).toFixed(1)} km </div>
            </div>
            <div class="flex flex-col">
            <span class="text-${selectedColor} font-semibold">${Math.ceil(s.time / 60)} min</span>
            </div>
        </div>
        `).join("");
    document.querySelector(".route-steps").innerHTML = html;
}

function showDirections(lat, lon, place = null) {

    fetch("search_history/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({ mongo_id: place.mongo_id, type: place.type })
    });

    lastLat = lat; lastLon = lon; lastPlace = place;
    // clear old routes
    routeLines.forEach(l=>map.removeLayer(l));
    routeLines = [];
    navigator.geolocation.getCurrentPosition(function (position) {
        const startLat = position.coords.latitude;
        const startLng = position.coords.longitude;

        const payload = {
        start_lat: startLat,
        start_lng: startLng,
        end_lat: lat,
        end_lng: lon,
        mode: currentMode,
        alternatives: {target_count: 3}
        };

        fetch("get_routes/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify(payload)
        })
        .then(res => {
            if (!res.ok) throw new Error("Server returned error status: " + res.status);
            return res.json();
        })
        .then(data => {
            const routes = data.routes;
            if (!routes.length) {
                window.showToaster("info", "No routes found.");
                return;
            }
            routes.forEach((r, idx) => {
                const coords = r.coordinates.map(c=>[c[0],c[1]]);
                const line = L.polyline(coords, {
                color: idx===0 ? bgColor : "#aaa",
                weight: idx===0 ? 6 : 4,
                opacity: idx===0 ? 0.8 : 0.4
                }).addTo(map);
                routeLines.push(line);
            });
            map.fitBounds(routeLines[0].getBounds());

            // Build the full directions HTML
            const directionsHtml = `
                <div class="px-4 py-3 suggestion-detail">
                <div class="h-32 w-full bg-cover bg-center"
                    style="background-image: url('${place?.imageUrl || "/static/images/hospital.svg"}')"></div>
                <div class="flex flex-col gap-2 mt-2">
                    <div class="flex justify-between">
                    <p class="text-xl font-bold">${place?.title}</p>
                    <span class="material-symbols-outlined bookmark-fill cursor-pointer"
                            data-id="${place?.mongo_id}" data-type="${place?.type?.toLowerCase()}">
                        ${place?.isBookmarked ? "bookmark" : "bookmark_add"}
                    </span>
                    </div>
                    <p class="text-sm">${place?.address || ""}</p>
                    <p class="text-sm">${place?.phone || ""}</p>
                    <p class="flex gap-2 items-center">${place?.rating || ""} 
                    <span class="text-xl text-star-orange">
                        ${place?.rating ? '★'.repeat(Math.floor(place.rating)) + '☆'.repeat(5 - Math.floor(place.rating)) + ` (${place.rating})` : ''}
                    </span>
                    </p>
                </div>
                <div class="route-options flex justify-between px-4 py-2"></div>
                <div class="route-steps overflow-y-auto max-h-[50vh] px-4"></div>
                <!-- Tab buttons -->
                <div class="flex my-5 justify-between">
                    <button class="tab-button cursor-pointer text-sm px-4 py-2 focus:outline-none hover:text-${selectedColor} flex flex-col" style="border-color: ${bgColor}; color: ${bgColor};" data-tab="best" >
                        <span class="material-symbols-outlined material-filled !font-semibold">directions</span>Best
                    </button>
                    <button class="tab-button mode-btn cursor-pointer text-sm px-4 py-2 focus:outline-none hover:text-${selectedColor} flex flex-col" data-tab="car" data-mode="auto">
                        <span class="material-symbols-outlined !font-semibold">directions_car</span>Car
                    </button>
                    <button class="tab-button mode-btn cursor-pointer text-sm px-4 py-2 focus:outline-none hover:text-${selectedColor} flex flex-col" data-tab="bike" data-mode="bicycle">
                        <span class="material-symbols-outlined !font-semibold">two_wheeler</span>Bike
                    </button>
                    <button class="tab-button mode-btn cursor-pointer text-sm px-4 py-2 focus:outline-none hover:text-${selectedColor} flex flex-col" data-tab="walk" data-mode="pedestrian">
                        <span class="material-symbols-outlined !font-semibold">directions_walk</span>Walking
                    </button>
                </div>

                <!-- Tab content -->
                <div class="tab-content" id="best">
                    <div class="flex items-center justify-between">
                        <div class="flex flex-col items-center justify-center">
                        <div class="w-4 h-4 rounded-full border-4"></div>
                        <hr class="h-6 border border-dashed w-0"/>
                        <span class="material-symbols-outlined text-${selectedColor}">location_on</span>
                        </div>
                        <div class="flex flex-col items-center gap-3">
                        <input type="text" placeholder="Your Location" class="${selectedColor === 'dark-blue' ? 'text-white placeholder:text-white' : ''} backdrop-blur-[20px] shadow-[4px_4px_10px_2px_#00000026] text-sm px-3 py-1.5 rounded-md w-full border-none focus:outline-none focus:ring-0" style="background-color: ${bgColor}A6;"/>
                        <input type="text" placeholder="Zenith Hospital" class="${selectedColor === 'dark-blue' ? 'text-white placeholder:text-white' : ''} backdrop-blur-[20px] shadow-[4px_4px_10px_2px_#00000026] text-sm px-3 py-1.5 rounded-md w-full border-none focus:outline-none focus:ring-0" style="background-color: ${bgColor}A6;" />
                        </div>
                        <span class="material-symbols-outlined">swap_vert</span>
                    </div>

                    <div class="flex gap-2 items-center justify-center py-5">
                        <span class="material-symbols-outlined !text-lg">share</span>Share directions
                    </div>

                    <div class="flex flex-col gap-4">
                        <div class="flex items-start justify-between">
                        <div class="border-l-2 pl-1 border-${selectedColor}">
                            <span class="material-symbols-outlined text-${selectedColor}">two_wheeler</span>
                        </div>
                        <div class="flex flex-col">
                            <span class="font-medium">Via String Rd</span>
                            <div class="text-xs">Fastest route. the usual traffic</div>
                        </div>
                        <div class="flex flex-col">
                            <span class="text-${selectedColor} font-semibold">4 min</span>
                            <div class="text-xs text-light-gray">1.3km</div>
                        </div>
                        </div>
                        <div class="flex items-start justify-between">
                        <span class="material-symbols-outlined pl-1">two_wheeler</span>
                        <div class="flex flex-col">
                            <span class="font-medium">Via String Rd</span>
                            <div class="text-xs">Fastest route. the usual traffic</div>
                        </div>
                        <div class="flex flex-col">
                            <span class="text-${selectedColor} font-semibold">4 min</span>
                            <div class="text-xs text-light-gray">1.3km</div>
                        </div>
                        </div>
                        <div class="flex items-start justify-between">
                        <span class="material-symbols-outlined pl-1">two_wheeler</span>
                        <div class="flex flex-col">
                            <span class="font-medium">Via String Rd</span>
                            <div class="text-xs">Fastest route. the usual traffic</div>
                        </div>
                        <div class="flex flex-col">
                            <span class="text-${selectedColor} font-semibold">4 min</span>
                            <div class="text-xs text-light-gray">1.3km</div>
                        </div>
                        </div>
                    </div>
                    <p class="text-center text-sm py-4">
                        Congratulation! You will earn <span class="text-${selectedColor} font-bold">2.8</span> Credit points on the ride completion.
                    </p>
                    <button class="w-full py-2 rounded-md bg-[#d9d9d9] text-[#a1a1a1] text-sm font-medium cursor-not-allowed">
                        Start
                    </button>
                    </div>
                </div>
            `;
            $suggestionBox.fadeOut(100, () => {
                $suggestionBox.html(directionsHtml).fadeIn(150);
            });

            let altHtml = routes.map((r, i) => {
                return `
                <div class="route-option ${i===0?'selected':''}" data-idx="${i}">
                    <span>${(r.distance).toFixed(1)} km</span>
                    <span>${Math.ceil(r.duration/60)} min</span>
                </div>
                `;
            }).join("");
            $(".route-options").html(altHtml);
            // When user clicks an alternative:
            $(document).on("click", ".route-option", function(){
                const i = $(this).data("idx");
                // clear previous highlight
                window.routeLines.forEach((ln, j)=>{
                ln.setStyle({ color: j===i?bgColor:"#aaa", weight: j===i?6:4, opacity: j===i?0.8:0.4 });
                $(".route-option").eq(j).toggleClass("selected", j===i);
                });
                map.fitBounds(window.routeLines[i].getBounds());
                renderSteps(routes[i].steps);
            });
            renderSteps(routes[0].steps);
        })
        .catch(err => {
            console.error("Routing error:", err);
            window.showToaster("error", err.message || "Routing failed.");
        })
        });
        $(document).on("click", ".mode-btn", function(){
            currentMode = $(this).data("mode");
            $(".mode-btn").removeClass("active");
            $(this).addClass("active");
            showDirections(lastLat, lastLon, lastPlace);
        });
}
































});