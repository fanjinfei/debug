var http = require('http');
var request = require("request");
var rp = require("request-promise");
var dt = require('./myfirstmodule');
var url = require('url');
var async = require('async');


var vurl = "http://open.canada.ca/data/api/action/package_show?id=4ae27978-0931-49ab-9c17-0b119c0ba92f";

//var proxyUrl = "http://" + user + ":" + password + "@" + host + ":" + port;
var proxyUrl = process.argv[2]

var pRequest = request.defaults({'proxy': proxyUrl});

pRequest({
	    url: vurl,
	}, function (error, response, body) {

	    if (!error && response.statusCode === 200) {
		//console.log(body); // Print the json response
		var obj = JSON.parse(body);
		console.log(obj.help);
	    }

	});
var get_rp = rp({uri:vurl, json: true, 'proxy':proxyUrl});
get_rp.then(function (body) {
	//var obj = JSON.parse(body);
	console.log(body.success); }); 
console.log('my frist server');

    function get_help(callback) {

	function cb1(error, response, body) {

		    if (!error && response.statusCode === 200) {
			//console.log(body); // Print the json response
			callback(body);
			//ckan = obj.help;
			//console.log(q.help);
		    }
		}
	
	pRequest({
	    url: vurl,
	    json: true
	}, cb1);
    }


http.createServer(function (req, res) {
    res.writeHead(200, {'Content-Type': 'text/plain'});
    res.write("The date and time are currently: " + dt.myDateTime());
    res.write("\n"+req.url+"\n");

    var q = url.parse(req.url, true).query;
    var txt = q.year + " " + q.month +"\n";
    res.write(txt);
	var ckan="a", b="b";

    async.parallel([ function(callback) {
        res.write('a');
        res.write('b');
        res.write('c\n');
        callback(null, "abc");
    }, function(callback) {
        res.write('x');
        res.write('y');
        res.write('z\n');
	b = "modified b ";
        callback(null, "xyz");
    } ], function done(err, results) { //this is the callback function
        if (err) {
            throw err;
        }
	console.log(results);
	b = results[0] + " | " + results[1];
        //res.end("\nDone!");
    });

    res.write(b + " start \n");

    get_rp.then(function(resp) { return resp})
	.then(function (body) {
		//var obj = JSON.parse(body);
		//console.log(body.success); 
		//res.write(obj.success);
		res.write(body.result.state + "\n");
b = body.result.state + "\n";
		}); 

    get_rp.then(function (body) {
		//var obj = JSON.parse(body);
		//console.log(body.success); 
		//res.write(obj.success);
		res.write(body.result.collection + "\n");
		}); 

    get_help( function (body) {
	//console.log(body);
	res.write(body.help + "\n");
	res.end('\nHello World!');
	});

    res.write(ckan);
    //res.end('\nHello World!');
}).listen(8000); 

var connect = require('connect');
var serveStatic = require('serve-static');
connect().use(serveStatic(__dirname)).listen(8080, function(){
    console.log('Server running on 8080...');
});
