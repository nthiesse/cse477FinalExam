

// code for login feature 
let count = 0;
    function checkCredentials() {
        // package data in a JSON object
        // var data_d = {'email': 'owner@email.com', 'password': 'password'}
        // console.log('data_d', data_d)

        // get the email and password from the form
        let email = document.getElementById("email").value;
        let password = document.getElementById("password").value;
        var data_d = { 'email': email, 'password': password }
        console.log('data_d', data_d)

        // SEND DATA TO SERVER VIA jQuery.ajax({})
        jQuery.ajax({
            url: "/processlogin",
            data: data_d,
            type: "POST",
            success: function (retruned_data) {
                retruned_data = JSON.parse(retruned_data);
                //   console.log("TEST", retruned_data)
                //   window.location.href = "/home";
                if (retruned_data.status === 1) {
                    window.location.href = "/events"; // Redirect to events page on success
                    count = 0;
                } else {
                    count++;
                    let errorMessage = document.getElementById("error-message");
                    errorMessage.style.visibility = "visible";
                    errorMessage.innerHTML = `Email or password are incorrect. Attempt: ${count}`;
                }
            }
        });
    }


function registerUser() {
    let email = document.getElementById("email").value;
    let password = document.getElementById("password").value;
    var data_d = { 'email': email, 'password': password }
    console.log('data_d', data_d)

    // SEND DATA TO SERVER VIA jQuery.ajax({})
    jQuery.ajax({
        url: "/processregistration",
        data: data_d,
        type: "POST",
        success: function (retruned_data) {
            retruned_data = JSON.parse(retruned_data);
            //   console.log("TEST", retruned_data)
            //   window.location.href = "/home";
            if (retruned_data.status === 1) {
                window.location.href = "/events"; // Redirect to events page on success
            } else {
                let errorMessage = document.getElementById("error-message");
                errorMessage.style.visibility = "visible";
                errorMessage.innerHTML = `Email already exists.`;
            }
        }
    });
}


// Time grid code 
let dragging = false;
let user_avalibility = 'available';
document.addEventListener('DOMContentLoaded', () => {
    const cells = document.querySelectorAll('.cell');
    const available_menu = document.getElementById('availability');

    available_menu.addEventListener('change', () => {
        user_avalibility = available_menu.value; 
    });

    // keep watch on each cell for if it is clicked on 
    cells.forEach(cell => {
        cell.addEventListener('mousedown', (e) => {
            e.preventDefault();
            dragging = true;
            makeAvailible(cell)
        });

        // listen for if the mouse is entering a cell 
        cell.addEventListener('mouseenter', () => {
            if (dragging) {
                makeAvailible(cell);
            }
        });
    });

    // listen for when the mouse is let go 
    document.addEventListener('mouseup', () => {
        dragging = false;
    });
});

function makeAvailible(cell) {
    cell.classList.remove('available', 'maybe', 'unavailable');
    cell.classList.add(user_avalibility);
    sendAvailability(cell);
}


const socket = io();
// sends the user availability to the database 
function sendAvailability(cell) {
    const availabile = {
        date: cell.getAttribute('date'),
        time_slot: cell.getAttribute('time'),
        available: cell.classList.contains('available') ? 'available' :
                   cell.classList.contains('maybe') ? 'maybe' : 'unavailable'
    };

    // get the event id 
    let temp = document.body.getAttribute('data-event-id');
    let id = parseInt(temp); 
    // send this information to routes.py 
    fetch(`/add_availability/${id}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json' 
        },
        body: JSON.stringify([availabile]) 
    })
    .then(response => response.json())
    .then(data => {
        socket.emit('availability_changed', {
            event_id: id,
            date: availabile.date,
            time: availabile.time_slot,
            availabile: availabile.available
        });
        console.log('Saved:', data.message);
    })
    .catch(error => {
        console.error('Error saving availability:', error);
    });

    // update the heatmap 
    configureHeatmap(id);
    getBestTime(id);
}


function reloadAvailability(event_id) {
    fetch(`/load_availability/${event_id}`)
    // put the response in json
    .then(response => response.json())
    // parse out the returned data
    .then(data => {
        if (data.status === 1) {
            console.log("Status is good")
            const availability = data.data;
            availability.forEach(i => {

                console.log(i)
                const cellSelector = `.cell[date="${i.date}"][time="${i.time}"]`;
                console.log('Cell Selector:', cellSelector);

                const cell = document.querySelector(`.cell[date="${i.date}"][time="${i.time}"]`);
                if (cell) {
                    console.log(`Found cell for ${i.date} ${i.time}`);

                    cell.classList.remove('available', 'maybe', 'unavailable');
                    cell.classList.add(i.available);
                }
            });
        } 
    });
}


// listen for if/when the events page loads 
document.addEventListener('DOMContentLoaded', function() {
    // get the event id 
    let temp = document.body.getAttribute('data-event-id');
    let id = parseInt(temp);
    socket.emit('join_event', id);
    reloadAvailability(id);
    // load in the heatmap as well
    configureHeatmap(id)
    getBestTime(id);
    
    
    // socket.on('heatmap_update', () => {
    //     configureHeatmap(id);
    // });
    socket.on('heatmap_update', function() {
        let temp = document.body.getAttribute('data-event-id');
        let id = parseInt(temp); 
        configureHeatmap(id);
    });


    socket.on('best_time_update', () => {
        getBestTime(id);
    });
})


// figures out the heatmap
// function gets the information from the database and then colors the cell according the availability 
function configureHeatmap(event_id) {
    fetch(`/get_heatmap_info/${event_id}`)
    // put the response in json
    .then(response => response.json())
    // parse out the returned data
    .then(data => {
        if (data.status === 1) {
            // console.log("Status is good")
            const availability = data.data;
            availability.forEach(i => {
                const cell = document.querySelector(`.unchangableCell[date="${i.date}"][time="${i.time}"]`);
                if (cell) {
                    if (i.available > 2) {
                        // dark green 
                        cell.style.backgroundColor = "#597240";
                    } else if (i.available > 1) {
                        // medium green 
                        cell.style.backgroundColor = "#81a55f";
                    } else if (i.available === 1) {
                        // light green 
                        cell.style.backgroundColor = "#d3e0c8";
                    } else if (i.maybe >= 1) {
                        // yellow 
                        cell.style.backgroundColor = "#ffff00";
                    } else {
                        // light grey 
                        cell.style.backgroundColor = "#d3d3d3";
                    }
                }
            });
        } 
    });
}


function formatDate(dateStr) {
    const dateObj = new Date(dateStr);
    return dateObj.toLocaleDateString('en-US', {
        weekday: 'long',
        month: 'long',
        day: 'numeric'
    });
}


function formatTimeRange(timeStr) {
    const [hours, minutes] = timeStr.split(':').map(Number);
    const start = new Date(0, 0, 0, hours, minutes);
    const end = new Date(start.getTime() + 30 * 60000); // add 30 minutes

    const options = { hour: 'numeric', minute: '2-digit' };
    return `${start.toLocaleTimeString('en-US', options)} - ${end.toLocaleTimeString('en-US', options)}`;
}

// get and display the best time calculation 
function getBestTime(event_id) {
    fetch(`/get_best_time/${event_id}`)
    // put the response in json
    .then(response => response.json())
    // parse out the returned data
    .then(data => {
        // get each of the ids from the html 
        const noAvailability = document.getElementById("noAvailabilityMessage");
        const timeDisplay = document.getElementById("bestTimeDisplay");
        const timeActual = document.getElementById("timeDetails");

        if (data.status === 1) {
            // best time to meet actually exists
            timeActual.textContent = `${formatDate(data.date)}, ${formatTimeRange(data.time)}`;
            // hide the not Available phrase 
            noAvailability.style.visibility = "hidden";
            // show the time parts 
            timeDisplay.style.visibility = "visible";
            timeActual.style.visibility = "visible";
        } else if (data.status === 2) {
            // no information logged 
            // show the not Available phrase 
            noAvailability.style.visibility = "visible";
            // hide the time parts 
            timeDisplay.style.visibility = "hidden";
            timeActual.style.visibility = "hidden";
        } else if (data.status === 3) {
            // should show the first available time to meet 
            timeActual.textContent = `${formatDate(data.date)}, ${formatTimeRange(data.time)}`;
            // times are logged but no one is available
            noAvailability.textContent = "No one is currently available";
            noAvailability.style.visibility = "visible";
            timeDisplay.style.visibility = "hidden";
            timeActual.style.visibility = "visible";
        }
 
    });
}


// function updateCellFromSocket(data) {
//     const { date, time, available } = data;
//     const cell = document.querySelector(`.cell[date="${date}"][time="${time}"]`);
//     if (cell) {
//         cell.classList.remove('available', 'maybe', 'unavailable');
//         cell.classList.add(available);
//     }
// }