
//to run: #nodejs js1.js
// broswer: http://localhost:8080/hello?year=2017&month=08
console.log('This example is different!');
console.log('The result is displayed in the Command Line Interface'); 

var http = require('http');
var dt = require('./myfirstmodule');
var url = require('url');
var fs = require('fs'); 

var events = require('events');
var eventEmitter = new events.EventEmitter();

//Create an event handler:
var myEventHandler = function () {
  console.log('I hear a scream!');
}

//Assign the event handler to an event:
eventEmitter.on('scream', myEventHandler);

//Fire the 'scream' event:
eventEmitter.emit('scream');

//var buf = Buffer.from('abc');
//console.log(buf);

/*fs.appendFile('mynewfile1.txt', 'Hello content!', function (err) {
  if (err) throw err;
  console.log('Saved!');
}); 

fs.open('mynewfile2.txt', 'w', function (err, file) {
  if (err) throw err;
  console.log('Saved!');
}); 

fs.writeFile('mynewfile3.txt', 'Hello content!', function (err) {
  if (err) throw err;
  console.log('Saved!');
}); 

fs.unlink('mynewfile2.txt', function (err) {
  if (err) throw err;
  console.log('File deleted!');
}); 

fs.rename('mynewfile1.txt', 'myrenamedfile.txt', function (err) {
  if (err) throw err;
  console.log('File Renamed!');
}); */

    fs.readFile('demofile1.html', function(err, data) {
        //res.write(data);
	console.log(data);
      });

http.createServer(function (req, res) {
    res.writeHead(200, {'Content-Type': 'text/plain'});
    res.write("The date and time are currently: " + dt.myDateTime());
    res.write("\n"+req.url+"\n");

    var q = url.parse(req.url, true).query;
    var txt = q.year + " " + q.month +"\n";
    res.write(txt);


    res.end('\nHello World!');
}).listen(8080); 
