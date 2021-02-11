// JS client for the flask-socket
let socket = io.connect('http://localhost:5000');

let socketData = document.getElementById('socketData');



// When connected to the server
socket.on('connect', ()=>{
    // Send message to the server
    socket.send('I am now connected');

    // Wait for reply from the server
socket.on('message', (msg) =>{
    console.log('message event');
    socketData.innerHTML = 'Data from the flask server: ' + msg;
});

socket.on('dashboard', (data) =>{
    console.log('dashboard event');
    socketData.innerHTML += 'Professor dashboard: ' + data;
});
    
});

