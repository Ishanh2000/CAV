// AUM SHREEGANESHAAYA NAMAH|| AUM SHREEHANUMATE NAMAH||

/*******************************************************************/
/*********** GLOBAL VARIABLES (DECLARE BEFORE FUNCTIONS) ***********/
/*******************************************************************/

const canvas = document.getElementById('cav_canvas');
canvas.width = window.innerWidth * 0.85; canvas.height = window.innerHeight * 0.85;
const ctx = canvas.getContext('2d');
const zoomScaleFactor = 1.1;
var lastX = canvas.width/2, lastY = canvas.height/2;
var dragStart, dragged;
// const wpImg = new Image; wpImg.src = 'wp.png'; // image of waypoint (filled green circle)

var totalZooms = 0;

var mode = "nav";

// OUR GRAPH
var WPs = [];


/*******************************************************/
/********************** FUNCTIONS **********************/
/*******************************************************/

function getXY(evt) {
	// apparent x and y
	const ax = evt.offsetX || (evt.pageX - canvas.offsetLeft);
	const ay = evt.offsetY || (evt.pageY - canvas.offsetTop );
	return ctx.transformedPoint(ax, ay);
}

// Clear the entire canvas
function clearCanvas() {
	var p1 = ctx.transformedPoint(0, 0);
	var p2 = ctx.transformedPoint(canvas.width, canvas.height);
	ctx.clearRect(p1.x, p1.y, p2.x-p1.x, p2.y-p1.y);
}

// draw one node
function drawNode(nd) {
	ctx.beginPath();
	ctx.fillStyle = '#080';
	ctx.arc(nd.x, nd.y, 5, 0, Math.PI * 2, true);
	ctx.strokeStyle = '#080';
	ctx.stroke();
	ctx.fill();
}

// Draw all nodes
function draw() {
	// WPs.forEach(wpc => { ctx.drawImage(wp, wpc.x, wpc.y ,10, 10) });
	WPs.forEach(wpc => {
		ctx.beginPath();
		ctx.fillStyle = '#080';
		ctx.arc(wpc.x, wpc.y, 5, 0, Math.PI * 2, true);
		ctx.strokeStyle = '#080';
		ctx.stroke();
		ctx.fill();
	});
}

function zoom(clicks) {
	var pt = ctx.transformedPoint(lastX, lastY);
	ctx.translate(pt.x, pt.y);
	var factor = Math.pow(zoomScaleFactor, clicks);
	ctx.scale(factor, factor);
	ctx.translate(-pt.x, -pt.y);
	clearCanvas();
	draw();
	totalZooms += clicks;
	document.getElementById("zoom_value").innerHTML = "<b>ZOOM:</b> "
		+ Math.pow(zoomScaleFactor, totalZooms).toFixed(4) + " (" + totalZooms + ")";
}


function mouseDownHandler(evt) {
	if (mode === "nav") {
		document.body.style.mozUserSelect = document.body.style.webkitUserSelect = document.body.style.userSelect = 'none';
		lastX = evt.offsetX || (evt.pageX - canvas.offsetLeft);
		lastY = evt.offsetY || (evt.pageY - canvas.offsetTop);
		dragStart = ctx.transformedPoint(lastX, lastY);
		dragged = false;
	}
	// do something else if mode === "node" || mode === "edge"
}

function mouseMoveHandler(evt) {
	lastX = evt.offsetX || (evt.pageX - canvas.offsetLeft);
	lastY = evt.offsetY || (evt.pageY - canvas.offsetTop);
	var pt = ctx.transformedPoint(lastX, lastY);

	document.getElementById("coordinates").innerHTML = "<b>X:</b> " + pt.x.toFixed(6) + ", " + "<b>Y:</b> " + pt.y.toFixed(6);

	if (mode === "nav") {		
		dragged = true;
		if (dragStart) {
			ctx.translate(pt.x-dragStart.x, pt.y-dragStart.y);
			clearCanvas();
			draw();
		}
	}
	// do something else if mode === "node" || mode === "edge"
}

function mouseUpHandler(evt) {
	if (mode === "nav") {
		dragStart = null;
	}
	// do something else if mode === "node" || mode === "edge"
}

function scrollHandler(evt) {
	if (mode === "nav") {
		var delta = evt.wheelDelta ? evt.wheelDelta/40 : evt.detail ? -evt.detail : 0;
		if (delta) zoom(delta);
		return evt.preventDefault() && false;
	}
	// do something else if mode === "node" or mode === "edge"
};

function doubleClickHandler(evt) {
	if (mode === "node") {
		const xy = getXY(evt);
		const newWP = { x : xy.x, y : xy.y };
		WPs.push(newWP);
		drawNode(newWP);
	}
	// do something else if mode === "nav" || mode === "edge"
}

/******** REGISTER EVENT LISTENERS FOR CANVAS ********/
canvas.addEventListener('mousedown', mouseDownHandler, false);
canvas.addEventListener('mousemove', mouseMoveHandler, false);
canvas.addEventListener('mouseup', mouseUpHandler, false);
canvas.addEventListener('DOMMouseScroll', scrollHandler, false);
canvas.addEventListener('mousewheel', scrollHandler, false);
canvas.addEventListener('dblclick', doubleClickHandler, false);

function homeTransform() {
	const factor = Math.pow(zoomScaleFactor, -totalZooms);
	ctx.scale(factor, factor);
	const ppt = ctx.transformedPoint(0, 0);
	ctx.translate(ppt.x, ppt.y);
	clearCanvas();
	draw();
}

document.addEventListener('keypress', (evt) => {
	const k = evt.key;
	switch(k) {
		case 'n': case 'N': document.getElementById("nav" ).checked = true; mode = "nav";  break;
		case 'w': case 'W': document.getElementById("node").checked = true; mode = "node"; break;
		case 'e': case 'E': document.getElementById("edge").checked = true; mode = "edge"; break;
	}
}, false);

function downloadPng() {
	window.open(canvas.toDataURL("image/png"));
}

function downloadJson() {
	var jsonData = { "waypoints" : WPs };
	var downloadAnchorNode = document.createElement('a');
	downloadAnchorNode.setAttribute("href", "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(jsonData)));
	downloadAnchorNode.setAttribute("download", "graph.json");
	document.body.appendChild(downloadAnchorNode); // required for firefox
	downloadAnchorNode.click();
	downloadAnchorNode.remove();
}


/**** Don't really know what this function does. Afraid to remove this. ****/
function trackTransforms() {

	// Adds ctx.getTransform() - returns an SVGMatrix
	// Adds ctx.transformedPoint(x,y) - returns an SVGPoint
	var svg = document.createElementNS("http://www.w3.org/2000/svg", 'svg');
	var xform = svg.createSVGMatrix();
	ctx.getTransform = function() { return xform; };
	
	var savedTransforms = [];
	var save = ctx.save;
	ctx.save = function() {
		savedTransforms.push(xform.translate(0, 0));
		return save.call(ctx);
	};

	var restore = ctx.restore;
	ctx.restore = function() {
		xform = savedTransforms.pop();
		return restore.call(ctx);
	};

	var scale = ctx.scale;
	ctx.scale = function(sx, sy) {
		xform = xform.scaleNonUniform(sx, sy);
		return scale.call(ctx, sx, sy);
	};

	var rotate = ctx.rotate;
	ctx.rotate = function(radians) {
		xform = xform.rotate(radians * 180 / Math.PI);
		return rotate.call(ctx, radians);
	};

	var translate = ctx.translate;
	ctx.translate = function(dx, dy) {
		xform = xform.translate(dx, dy);
		return translate.call(ctx, dx, dy);
	};

	var transform = ctx.transform;
	ctx.transform = function(a, b, c, d, e, f) {
		var m2 = svg.createSVGMatrix();
		m2.a = a; m2.b = b; m2.c = c; m2.d = d; m2.e = e; m2.f = f;
		xform = xform.multiply(m2);
		return transform.call(ctx, a, b, c, d, e, f);
	};
	
	var setTransform = ctx.setTransform;
	ctx.setTransform = function(a, b, c, d, e, f) {
		xform.a = a; xform.b = b;	xform.c = c; xform.d = d; xform.e = e; xform.f = f;
		return setTransform.call(ctx, a, b, c, d, e, f);
	};

	var pt = svg.createSVGPoint();
	ctx.transformedPoint = function(x, y) {
		pt.x = x; pt.y = y;
		return pt.matrixTransform(xform.inverse());
	}
}

trackTransforms();

// WINDOW ONLOAD (EVENT LISTENER BINDINGS IN THIS FUNCTION)
window.onload = function () {
	document.getElementById("nav").checked = true; // default checking of "Navigation" mode
	document.getElementById("homeBtn").addEventListener('click', homeTransform, false);
	document.getElementById("downloadPngBtn").addEventListener('click', downloadPng, false);
	document.getElementById("downloadJsonBtn").addEventListener('click', downloadJson, false);
	// radio mode changer
	document.querySelectorAll('input[type=radio][name="mode"]').forEach(radio => {
		radio.addEventListener('change', () => { mode = radio.value; });
	});
}

/**********************************************/
/********** BEGIN ACTUAL CODING HERE **********/
/**********************************************/

// random nodes
for (let i = 0; i < 10; i++) {
	WPs.push({ x : (Math.random() * 1000 + 100), y : (Math.random() * 500 + 100) });
}

draw();
