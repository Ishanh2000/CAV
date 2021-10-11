// AUM SHREEGANESHAAYA NAMAH|| AUM SHREEHANUMATE NAMAH||

/*******************************************************************/
/*********** GLOBAL VARIABLES (DECLARE BEFORE FUNCTIONS) ***********/
/*******************************************************************/

const ndDefaultClr = "#080", ndSelectClr = "#F00", edgeClr = "#080", wtClr = "#000";
const canvas = document.getElementById('cav_canvas');
canvas.width = window.innerWidth * 0.85; canvas.height = window.innerHeight * 0.85;
const ctx = canvas.getContext('2d');
const zoomScaleFactor = 1.1;
var lastX = canvas.width/2, lastY = canvas.height/2;
var dragStart, dragged;
// const wpImg = new Image; wpImg.src = 'wp.png'; // image of waypoint (filled green circle)
var totalZooms = 0;
var mode = "nav";
var edgeStart = -1; // index in WPs of the node which is start of an edge in progress
var speed = 10.0;

// OUR GRAPH
var WPs = []; // nodes / waypoints
var sectors = []; // 20 x 20 array of sectors - stores WP indices
for (let i = 0; i < 20; i++) {
	var tmp = [];
	for (let j = 0; j < 20; j++) tmp.push([]);
	sectors.push(tmp);
}
var NBs = []; // neighbours (edge data)

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

// Draw one node
function drawNode(nd) {
	ctx.beginPath();
	ctx.fillStyle = nd.selected ? ndSelectClr : ndDefaultClr; // red if selected
	ctx.arc(nd.x, nd.y, 5, 0, Math.PI * 2, true);
	ctx.strokeStyle = nd.selected ? ndSelectClr : ndDefaultClr; // red if selected
	ctx.stroke();
	ctx.fill();
}

// Draw an edge
function drawEdge(start, end) {
	ctx.beginPath();
	ctx.lineWidth = 2;
	ctx.moveTo(start.x, start.y);
	ctx.lineTo(end.x, end.y);
	ctx.strokeStyle = edgeClr;
	ctx.stroke();
}

// Draw all nodes
function draw() {
	// first draw edges
	ctx.lineWidth = 2;
	ctx.font = "15px Arial";
	ctx.textAlign = "center";
	ctx.fillStyle = wtClr;
	NBs.forEach((nbsi, i) => {
		nbsi.forEach((nb) => {
			if (i < nb.idx) {
				ctx.beginPath();
				ctx.moveTo(WPs[i].x, WPs[i].y);
				ctx.lineTo(WPs[nb.idx].x, WPs[nb.idx].y);
				ctx.strokeStyle = edgeClr;
				ctx.stroke();
				ctx.strokeStyle = wtClr;
				ctx.strokeText(`${nb.wt.toFixed(2)}`, (WPs[i].x + WPs[nb.idx].x)/2, (WPs[i].y + WPs[nb.idx].y)/2);
			}
		})
	});
	
	// then draw nodes
	WPs.forEach(wpc => { // WPs.forEach(wpc => { ctx.drawImage(wp, wpc.x, wpc.y ,10, 10) }); // alternatively
		ctx.beginPath();
		ctx.fillStyle = wpc.selected ? ndSelectClr : ndDefaultClr;
		ctx.arc(wpc.x, wpc.y, 5, 0, Math.PI * 2, true);
		ctx.strokeStyle = wpc.selected ? ndSelectClr : ndDefaultClr;
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

function getSectorIndex(p) {
	return { ix : Math.floor((p.x + 10000) / 1000), iy : Math.floor((p.y + 10000) / 1000) };
}

function dist(p, q) {
	return Math.sqrt(((p.x - q.x) * (p.x - q.x)) + ((p.y - q.y) * (p.y - q.y)));
}

function doubleClickHandler(evt) {
	if (mode === "node") {
		const p = getXY(evt);
		const { ix, iy } = getSectorIndex(p);
		if (evt.shiftKey) { // delete a "close-by" node
			const l = sectors[ix][iy].length;
			let delIndex = -1;
			for (let i = 0; i < l; i++) if (dist(p, WPs[sectors[ix][iy][i]]) <= 5) { delIndex = i; break; } // find the "close-by" point
			if (delIndex < 0) return; // no "close-by" point found
			const wp_index = sectors[ix][iy][delIndex];
			if (edgeStart === wp_index) edgeStart = -1;

			/***** DO NOT CHANGE STATEMENT ORDER *****/
			const l_NBs = NBs.length; // also WP.length
			var NBs_new = [];
			for (let i = 0; i < l_NBs; i++) {
				if (i === wp_index) continue;
				var nbsi = [];
				const l_NBsi = NBs[i].length;
				for (let j = 0; j < l_NBsi; j++) {
					const { idx, wt } = NBs[i][j];
					if (idx < wp_index) nbsi.push({ idx, wt });
					else if (idx > wp_index) nbsi.push({ idx: (idx - 1), wt });
				}
				NBs_new.push(nbsi);
			}
			NBs = NBs_new;
			/*****************************************/
			
			WPs.splice(wp_index, 1); // removed from waypoints

			/***** DO NOT CHANGE STATEMENT ORDER *****/
			var sector_new = [];
			for (let i = 0; i < l; i++) { // index removed from sectors, greater indices decremented
				if (i === delIndex) continue;
				const val = sectors[ix][iy][i];
				if (val < wp_index) sector_new.push(val);
				else if (val > wp_index) sector_new.push(val-1);
			}
			sectors[ix][iy] = sector_new;
			/*****************************************/

			clearCanvas();
			draw(); // redrawing graph
		}
		else {
			sectors[ix][iy].push(WPs.length); // push index of node inside relevant sector
			WPs.push(p);
			NBs.push([]);
			drawNode(p);
		}
	}
	// do something else if mode === "nav" || mode === "edge"
}

function clickHandler(evt) {
	if (mode === "edge") {
		const p = getXY(evt);
		const { ix, iy } = getSectorIndex(p);

		if (evt.shiftKey) {
			console.log(`Will remove an edge near (${p.x}, ${p.y})`);
			
		} else {
			// find a close-by point
			const l = sectors[ix][iy].length;
			let secIndex = -1;
			for (let i = 0; i < l; i++) if (dist(p, WPs[sectors[ix][iy][i]]) <= 5) { secIndex = i; break; } // find the "close-by" point
			if (secIndex < 0) return; // no "close-by" point found - do nothing
			const ptIndex = sectors[ix][iy][secIndex];
			if (edgeStart < 0) { // new selection being made
				edgeStart = ptIndex;
				WPs[ptIndex].selected = true;
			} else { // must insert edge now and remove selection
				if ((edgeStart !== ptIndex) && (NBs[edgeStart].map(x => x.idx).indexOf(ptIndex) < 0)) {
					const wt = (speed > 0) ? ((10.0 * dist(WPs[edgeStart], WPs[ptIndex])) / speed) : 1000000; // milliseconds
					NBs[edgeStart].push({ idx : ptIndex, wt });
					NBs[ptIndex].push({ idx : edgeStart, wt });
				}
				WPs[edgeStart].selected = false;
				edgeStart = -1;
			}
			clearCanvas();
			draw();
		}
	}
	// do something else if mode === "nav" || mode === "node"
}

/******** REGISTER EVENT LISTENERS FOR CANVAS ********/
canvas.addEventListener('mousedown', mouseDownHandler, false);
canvas.addEventListener('mousemove', mouseMoveHandler, false);
canvas.addEventListener('mouseup', mouseUpHandler, false);
canvas.addEventListener('DOMMouseScroll', scrollHandler, false);
canvas.addEventListener('mousewheel', scrollHandler, false);
canvas.addEventListener('dblclick', doubleClickHandler, false);
canvas.addEventListener('click', clickHandler, false);

function homeTransform() {
	const factor = Math.pow(zoomScaleFactor, -totalZooms);
	totalZooms = 0;
	ctx.scale(factor, factor);
	const ppt = ctx.transformedPoint(0, 0);
	ctx.translate(ppt.x, ppt.y);
	document.getElementById("zoom_value").innerHTML = "<b>ZOOM:</b> 1.0 (0)";
	clearCanvas();
	draw();
}

function clearGraph() {
	var confirmClear = window.prompt("Are you sure you wish to clear graph? This cannot be undone."
	+ "Type \"YES\" to confirm (won't clear if you type otherwise):");
	if (confirmClear !== "YES") return;
	WPs = [];
	NBs = [];
	edgeStart = -1;
	homeTransform();
}

document.addEventListener('keypress', (evt) => {
	const k = evt.key;
	switch(k) {
		case 'n': case 'N': document.getElementById("nav").click(); break;
		case 'w': case 'W': document.getElementById("node").click(); break;
		case 'e': case 'E': document.getElementById("edge").click(); break;
		case 'h': case 'H': document.getElementById("homeBtn").click(); break;
		case 'x': case 'X': document.getElementById("clearBtn").click(); break;		
	}
}, false);

document.addEventListener('keydown', (evt) => {
	if ((evt.key === "Escape") && (mode === "edge") && (edgeStart > -1)) {
		WPs[edgeStart].selected = false;
		edgeStart = -1;
		clearCanvas();
		draw();
	}
}, false);

function downloadPng() {
	window.open(canvas.toDataURL("image/png"));
}

function downloadJson() {
	var jsonData = {
		"waypoints" : WPs.map((p) => { return { x : p.x, y : p.y }; }), // necessary since WPs is Array of SVGPoint
		"neighbours" : NBs,
		"sectors" : sectors,
	};
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
	document.getElementById("speed").value = 10.00; // default speed
	document.getElementById("homeBtn").addEventListener('click', homeTransform, false);
	document.getElementById("clearBtn").addEventListener('click', clearGraph, false);
	document.getElementById("downloadPngBtn").addEventListener('click', downloadPng, false);
	document.getElementById("downloadJsonBtn").addEventListener('click', downloadJson, false);
	document.getElementById("speed").addEventListener('change', (evt) => { speed = parseFloat(evt.target.value.trim()) }, false);
	// radio mode changer
	document.querySelectorAll('input[type=radio][name="mode"]').forEach(radio => {
		radio.addEventListener('change', () => { mode = radio.value; });
	});
}

window.onbeforeunload = function() { // not satisfactory
	return "Are you sure you wish to leave? Graph cannot be retrieved. Type \"YES\" to leave (won't leave if you type otherwise):";
}

/**********************************************/
/********** BEGIN ACTUAL CODING HERE **********/
/**********************************************/

