
//to run: #nodejs js1.js
// broswer: http://localhost:8080/hello?year=2017&month=08
console.log('This example is different!');
console.log('The result is displayed in the Command Line Interface'); 

var http = require('http');
var dt = require('./myfirstmodule');
var url = require('url');

http.createServer(function (req, res) {
    res.writeHead(200, {'Content-Type': 'text/plain'});
    res.write("The date and time are currently: " + dt.myDateTime());
    res.write("\n"+req.url+"\n");

    var q = url.parse(req.url, true).query;
    var txt = q.year + " " + q.month +"\n";
    res.write(txt);

    res.end('\nHello World!');
}).listen(8080); 
