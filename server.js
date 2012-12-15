var app = require('http').createServer(),
io = require('socket.io').listen(app),
fs = require('fs')

app.listen(8000);

function sendFile(socket, id, filename)
{
  fs.readFile(__dirname + '/' + filename,
    function(err, data)
    {
      if (err)
        socket.emit(id, {"status": 500, "data": null});
      else 
        socket.emit(id, {"status": 200,"data": new Buffer(data).toString('base64')});
    });
}
var detectFileChange = function(socket, id, filename) {
    fs.watchFile(__dirname + '/' + filename, function(curr, prev) {
      sendFile(socket, id, filename);
    });
}

io.sockets.on('connection', function (socket) {
  sendFile(socket, 'image', 'output/camera.png');
  detectFileChange(socket, 'image', 'output/camera.png');
});
