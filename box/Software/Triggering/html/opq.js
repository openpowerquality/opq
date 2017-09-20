Graph.prototype.drawArray = function(array){
    if(array.length <3)
        return;
    var context = this.context;
    context.save();
    var pixel_values = [];
    for (var i = 0; i < array.length; i++) {
        if(i*this.time_offset > this.maxX){
            break;
        }
        pixel_values.push({x : i*this.time_offset*this.unitX + this.AXISOFFSET ,
        y : this.centerY - this.unitY*(array[i] - this.minY)})
    }

    context.moveTo((pixel_values[0].x), pixel_values[0].y);
    for(i = 0; i < pixel_values.length-1; i ++)
    {

        var x_mid = (pixel_values[i].x + pixel_values[i+1].x) / 2;
        var y_mid = (pixel_values[i].y + pixel_values[i+1].y) / 2;
        var cp_x1 = (x_mid + pixel_values[i].x) / 2;
        var cp_y1 = (y_mid + pixel_values[i].y) / 2;
        var cp_x2 = (x_mid + pixel_values[i+1].x) / 2;
        var cp_y2 = (y_mid + pixel_values[i+1].y) / 2;
        context.beginPath();
        if(pixel_values[i].y < this.dangerMin || pixel_values[i].y > this.dangerMax) {
            context.strokeStyle = '#ff0000';
        }
        else {
            context.strokeStyle = '#000000';
        }
        context.quadraticCurveTo(cp_x1,pixel_values[i].y ,x_mid, y_mid);
        context.quadraticCurveTo(cp_x2,pixel_values[i+1].y ,pixel_values[i+1].x,pixel_values[i+1].y);
        context.stroke();
    }
    context.restore()
};

Graph.prototype.clear = function () {
    var context = this.context;
    var canvas = this.canvas;
    context.clearRect(0, 0, canvas.width, canvas.height);
    // draw x and y axis
    this.drawXAxis();
    this.drawYAxis();
};

Graph.prototype.drawXAxis = function() {
    var context = this.context;
    context.save();
    context.beginPath();
    context.moveTo(this.AXISOFFSET, this.centerY);
    context.lineTo(this.canvas.width, this.centerY);
    context.strokeStyle = this.axisColor;
    context.lineWidth = 2;
    context.stroke();

    // draw tick marks
    var xPosIncrement = this.unitsPerTickX * this.unitX;
    var xPos, unit;
    context.font = this.font;
    context.textAlign = 'center';
    context.textBaseline = 'top';

    // draw left tick marks
    xPos = this.centerX;
    unit = (this.minX);
    while(unit <= this.maxX) {
        context.moveTo(xPos, this.centerY);
        context.lineTo(xPos, this.centerY + this.tickSize / 2);
        context.stroke();
        context.fillText(unit, xPos, this.centerY + this.tickSize / 2 + 3);
        unit += this.unitsPerTickX;
        xPos = Math.round(xPos + xPosIncrement);
    }
    context.restore();
};

Graph.prototype.drawYAxis = function() {
    var context = this.context;
    context.save();
    context.beginPath();
    context.moveTo(this.centerX, 0);
    context.lineTo(this.centerX, this.canvas.height - this.AXISOFFSET);
    context.strokeStyle = this.axisColor;
    context.lineWidth = 2;
    context.stroke();

    // draw tick marks
    var yPosIncrement = this.unitsPerTickY * this.unitY;
    var yPos, unit;
    context.font = this.font;
    context.textAlign = 'right';
    context.textBaseline = 'top';

    // draw top tick marks
    yPos = this.centerY;
    //console.log(this.centerY);
    unit = this.minY;

    while(unit <= this.maxY) {
        context.moveTo(this.centerX - this.tickSize / 2, yPos);
        context.lineTo(this.centerX, yPos);
        context.stroke();
        if(this.unitsPerTickY < 1) {
            context.fillText(unit.toFixed(2), this.centerX - this.tickSize / 2 - 3, yPos);
        }
        else {
            context.fillText(unit, this.centerX - this.tickSize / 2 - 3, yPos);
        }
        unit += this.unitsPerTickY;
        yPos = Math.round(yPos - yPosIncrement);
    }
    context.restore();
};

function Graph(config) {
    // user defined properties
    this.canvas = document.getElementById(config.canvasId);

    this.AXISOFFSET = 40;
    this.minX = config.minX;
    this.minY = config.minY;
    this.maxX = config.maxX;
    this.maxY = config.maxY;
    this.unitsPerTickX = config.unitsPerTickX;
    this.unitsPerTickY = config.unitsPerTickY;
    this.labelX = config.labelX;
    this.labelY = config.labelY;
    // constants
    this.axisColor = '#aaa';
    this.font = '8pt Calibri';
    this.tickSize = 20;

    // relationships
    this.context = this.canvas.getContext('2d');
    this.context.imageSmoothingEnabled = true;
    this.rangeX = this.maxX - this.minX;
    this.rangeY = this.maxY - this.minY;
    this.unitX = (this.canvas.width - this.AXISOFFSET)/ this.rangeX;
    this.unitY = (this.canvas.height - this.AXISOFFSET) / this.rangeY;
    this.centerY =this.canvas.height - this.AXISOFFSET;
    this.centerX = this.AXISOFFSET;
    this.time_offset = 1.0/6;

    this.dangerMin = config.dangerMin;
    this.dangerMax = config.dangerMax;

}


var vGraph = new Graph({
    canvasId: 'voltage',
    minX: 0,
    minY: 100,
    maxX: 10.5,
    maxY: 140,
    unitsPerTickX: 1,
    unitsPerTickY: 5,
    labelX : "s",
    labelY : "V",
    dangerMin : 110,
    dangerMax :130
});

var fGraph = new Graph({
    canvasId: 'frequency',
    minX: 0,
    minY: 59.5,
    maxX: 10.5,
    maxY: 60.5,
    unitsPerTickX: 1,
    unitsPerTickY: 0.1,
    labelX : "s",
    labelY : "Hz",
    dangerMin : 59.9,
    dangerMax :61.1
});

fArray = [];
vArray = [];

function updatePlots() {
/*    fArray.push(Math.random()*1 + 59.5);
    if(fArray.length > 10*6)
        fArray.shift()
    vArray.push(Math.random()*40 + 100);
    if(vArray.length > 10*6)
        vArray.shift()
*/
    vGraph.clear();
    fGraph.clear();
    vGraph.drawArray(vArray);
    fGraph.drawArray(fArray);
}

var timer = window.setInterval(updatePlots, 1000.0/6);

var ws = new WebSocket("ws://" + window.location.host);
//var ws = new WebSocket("ws://127.0.0.1:8080");
ws.onmessage = function (event) {
    var message = JSON.parse(event.data);
    var elem = document.getElementById("rq");
    elem.style.height = message.q.r + "%";

    var elem = document.getElementById("aq");
    elem.style.height = message.q.a + "%";

    var elem = document.getElementById("zq");
    elem.style.height = message.q.z + "%";

    var elem = document.getElementById("dq");
    elem.style.height = message.q.d + "%";
    fArray.push(message.f);
    vArray.push(message.v);
    if(fArray.length > 10*6)
        fArray.shift();
    if(vArray.length > 10*6)
        vArray.shift();
};