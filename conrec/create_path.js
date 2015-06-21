var conrecModule = require('./conrec.js');

if (process.argv.length < 4) {
    console.log('Missing argument for the grid file');
    console.log('Usage create_path.js grid_file downsample')
    process.exit();
}

var downSample = +process.argv[3];

var times = [2,4,6,8,10,12,14,16,18,20,22,24];
var zs = times.map(function(d) { return Math.log((d + 0.26) * 60); });
var d3 = require('d3');

jsonStruct = require(process.argv[2]);

var data = jsonStruct.grid_z;
var max_z = Math.max.apply(null, data.map(function(d) { return Math.max.apply(null, d); }));

var lenXDim = data.length;
var lenYDim = data[0].length;

var xGridValues = d3.scale.ordinal().domain(d3.range(lenXDim))
.rangePoints([jsonStruct.min_x, jsonStruct.max_x], 0).range();
var yGridValues = d3.scale.ordinal().domain(d3.range(lenYDim))
.rangePoints([jsonStruct.min_y, jsonStruct.max_y], 0).range();

var c = new conrecModule.Conrec();
c.contour(data, 0, xGridValues.length - 1, 0, yGridValues.length - 1, xGridValues, yGridValues, zs.length, zs);

var contourList = c.contourList();

/*
for (var i = 0; i < contourList; i++) {
    var contour = contourList[i];
    for (var j = 0; j < contour.length; j++) {
        
    }
}
*/



var newContours = [];
var oldContours = c.contourList().reverse();

for (var i = 0; i < oldContours.length; i++) {
    newContour = {};
    newContour.path = [];
    for (var j = 0; j < oldContours[i].length; j++) {
        if (oldContours[i].length > 4)  {
            if (j % downSample === 0)
            newContour.path.push(oldContours[i][j]);
        } else {
            newContour.path.push(oldContours[i][j]);
        }
    }

    newContour.path.push(oldContours[i][oldContours[i].length-1])
    newContour.level = oldContours[i].level;
    newContour.k = oldContours[i].k;

    newContours.push(newContour);
}

console.log(JSON.stringify(newContours, function(key, val) {
                              return val.toFixed ? Number(val.toFixed(2)) : val;
}));
//console.log(JSON.stringify(c.contourList().reverse(
//console.log(c.contourList().reverse());
