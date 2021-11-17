// AUM SHREEGANESHAAYA NAMAH|| AUM SHREEHANUMATE NAMAH||

// Basics studied from: http://phrogz.net/tmp/canvas_zoom_to_cursor.html

/*******************************************************************/
/*********** GLOBAL VARIABLES (DECLARE BEFORE FUNCTIONS) ***********/
/*******************************************************************/

const docBgClr = { light : "#FFF", dark : "#000" }, docTxtClr = { light : "#000", dark : "#FFF" };
var useDarkMode;

// node related parameters
const nodeRadius = 5, nodeDetectRadius = 8, ndDefaultClr = "#080", ndSelectClr = "#F00";

// edge related parameters
const edgeWidth = 2, arrowHeadLength = 10, arrowHeadWidth = 10, edgeClr = "#080";
const wtStokeWidht = 1, wtClr = { light : "#000", dark: "#000" }, wtFont = "15px Arial", infWeight = 1000000; // milliseconds

// car related parameters
const carWidth = 150, carLength = 200, carDetectRadius = 100, carIdFont = "40px Arial", carDetailsFont = "30px Arial";
const lightCarClrs = [ "#FC0", "#3CF", "#3C3", "#FFF" ];

// destination star related paramters
const destStarExRadius = 20, destStarInRadius = 10, destStarSpokes = 5, destStarDetectRadius = 20;
const destStarTxtOffset = 20, destTxtClr = { light : "#000", dark: "#222" }, destCarIdFont = "15px Arial";

// canvar related parameters
const canvas = document.getElementById('cav_canvas');
canvas.width = window.innerWidth * 0.85; canvas.height = window.innerHeight * 0.85;
const ctx = canvas.getContext('2d');
const canvasBgClr = { light : "#EEE", dark : "#555" };

// other parameters
const zoomScaleFactor = 1.1;
var lastX = canvas.width/2, lastY = canvas.height/2;
var dragStart, dragged;
var totalZooms = 0;
var mode = "nav";
var edgeStart = -1; // index in WPs of the node which is start of an edge in progress
var speed = 10.0, acc = 0.0; // m/s, m/s2
var angle = 0.00;
var carColor = "#F00";
var showCars = true;
var isSimAndPlay = false;

// GRAPH
var WPs = []; // nodes / waypoints
var sectors = []; // 20 x 20 array of sectors - stores WP indices
for (let i = 0; i < 20; i++) {
	var tmp1 = [];
	for (let j = 0; j < 20; j++) tmp1.push([]);
	sectors.push(tmp1);
}
var NBs = []; // neighbours (edge data)

// CARS
var cars = [];
var carsSectors = []; // 20 x 20 array of sectors - stores cars' indices
for (let i = 0; i < 20; i++) {
	var tmp2 = [];
	for (let j = 0; j < 20; j++) tmp2.push([]);
	carsSectors.push(tmp2);
}
var carId = 0;

/*******************************************************/
/********************** FUNCTIONS **********************/
/*******************************************************/

function uuidv4() {
  return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
    (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
  );
}

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

function drawNode(nd) {
	ctx.beginPath();
	ctx.strokeStyle = ctx.fillStyle = nd.selected ? ndSelectClr : ndDefaultClr;
	ctx.arc(nd.x, nd.y, nodeRadius, 0, Math.PI * 2, true);
	ctx.stroke();
	ctx.fill();
}

function drawCar(car) {
	ctx.save();
	ctx.beginPath();
	ctx.translate(car.x, car.y); // move the rotation point to the center of the rect
	ctx.rotate(car.angle); // rotate the rect
	ctx.rect(-carLength/2, -carWidth/2, carLength, carWidth); // draw the rect on the transformed context
	ctx.fillStyle = car.color;
	ctx.fill();
	ctx.lineWidth = 5;
	ctx.moveTo(20 + (carLength/2), -3 - (carWidth/2));
	ctx.lineTo(20 + (carLength/2), 3 + (carWidth/2));
	ctx.strokeStyle = "#000";
	ctx.stroke();
	ctx.fillStyle = ctx.strokeStyle = (lightCarClrs.indexOf(car.color) < 0) ? "#FFF" : "#000"; // use white on dark-coloured cars
	ctx.font = carIdFont;
	ctx.strokeText(`${car.id}`, -15, -30);
	ctx.font = carDetailsFont;
	if (car.ts) ctx.strokeText(`${car.ts.toFixed(0)} ms`, -15, 30);
	ctx.strokeText(`${car.speed.toFixed(2)} m/s`, -15, 60);
	ctx.restore(); // restore the context to its untranslated/unrotated state
}

function draw() {
	// first draw destinations
	ctx.lineWidth = wtStokeWidht;
	ctx.font = destCarIdFont;
	if (showCars) cars.forEach(car => {
		if (car.dest === null) return;
		ctx.save();
    ctx.beginPath();
    ctx.translate(WPs[car.dest].x, WPs[car.dest].y);
    ctx.moveTo(0, -destStarExRadius);
    for (var i = 0; i < destStarSpokes; i++) {
			ctx.rotate(Math.PI / destStarSpokes);
			ctx.lineTo(0, -destStarInRadius);
			ctx.rotate(Math.PI / destStarSpokes);
			ctx.lineTo(0, -destStarExRadius);
    }
    ctx.closePath();
		ctx.fillStyle = car.color;
    ctx.fill();
		ctx.strokeStyle = ctx.fillStyle = destTxtClr[useDarkMode ? "dark" : "light"];
		ctx.strokeText(`(${car.id})`, destStarTxtOffset, -destStarTxtOffset);
    ctx.restore();
	});

	// then draw edges
	ctx.font = wtFont;
	ctx.textAlign = "center";
	NBs.forEach((nbsi, i) => {
		nbsi.forEach((nb) => {
			const x1 = WPs[i].x, y1 = WPs[i].y, x2 = WPs[nb.idx].x, y2 = WPs[nb.idx].y;
			ctx.lineWidth = edgeWidth;
			ctx.beginPath();
			ctx.moveTo(x1, y1); // x1, y1
			ctx.lineTo(x2, y2);
			ctx.strokeStyle = edgeClr;
			ctx.stroke();

			const b = (arrowHeadLength + nodeRadius), a = (arrowHeadWidth/2);
			const _d = dist(WPs[i], WPs[nb.idx]);
			ctx.beginPath();
			ctx.moveTo(((_d - nodeRadius)*x2 + nodeRadius*x1) / _d, ((_d - nodeRadius)*y2 + nodeRadius*y1) / _d);
			const _k = { x : ((y1 - y2) / _d), y : ((x2 - x1) / _d) }; // vector perpendicular to edge
			const _m = { x : (((_d - b)*x2 + b*x1) / _d), y : (((_d - b)*y2 + b*y1) / _d) }; // mid-point
			ctx.lineTo(_m.x + (a * _k.x), _m.y + (a * _k.y));
			ctx.lineTo(_m.x - (a * _k.x), _m.y - (a * _k.y));
			ctx.fillStyle = edgeClr;
			ctx.fill();

			ctx.strokeStyle = ctx.fillStyle = wtClr[useDarkMode ? "dark" : "light"];
			ctx.lineWidth = wtStokeWidht;
			ctx.strokeText(`${nb.wt.toFixed(2)}`, (WPs[i].x + WPs[nb.idx].x)/2, (WPs[i].y + WPs[nb.idx].y)/2);
		})
	});

	// then draw nodes
	WPs.forEach(wpc => { // WPs.forEach(wpc => { ctx.drawImage(wp, wpc.x, wpc.y ,10, 10) }); // alternatively
		ctx.beginPath();
		ctx.fillStyle = wpc.selected ? ndSelectClr : ndDefaultClr;
		ctx.arc(wpc.x, wpc.y, nodeRadius, 0, Math.PI * 2, true);
		ctx.strokeStyle = wpc.selected ? ndSelectClr : ndDefaultClr;
		ctx.stroke();
		ctx.fill();
	});

	// then the cars
	if (showCars) cars.forEach(car => drawCar(car)); // make this efficient later on
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
	const p = getXY(evt);
	const { ix, iy } = getSectorIndex(p);
	if (mode === "node") {
		if (evt.shiftKey) { // delete a "close-by" node
			const l = sectors[ix][iy].length;
			let delIndex = -1;
			for (let i = 0; i < l; i++) if (dist(p, WPs[sectors[ix][iy][i]]) <= nodeDetectRadius) { delIndex = i; break; } // find the "close-by" point
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
			for (let i = 0; i < 20; i++) for (let j = 0; j < 20; j++) {
				if ((i === ix) && (j === iy)) continue;
				const l_ij = sectors[i][j].length;
				for (let k = 0; k < l_ij; k++) if (sectors[i][j][k] > wp_index) sectors[i][j][k]--;
			}
			var sector_new = [];
			for (let i = 0; i < l; i++) { // index removed from sectors, greater indices decremented
				if (i === delIndex) continue;
				const val = sectors[ix][iy][i];
				if (val < wp_index) sector_new.push(val);
				else if (val > wp_index) sector_new.push(val-1);
			}
			sectors[ix][iy] = sector_new;
			/*****************************************/

			// must remove car destination
			const l_cars = cars.length;
			for (let i = 0; i < l_cars; i++) {
				if (cars[i].dest === wp_index) cars[i].dest = null;
				else if (cars[i].dest < wp_index) cars[i].dest--;
			}

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
	else if (mode === "cars") {
		if (evt.shiftKey) {
			const l = carsSectors[ix][iy].length;
			console.log(ix, iy);
			let delIndex = -1;
			for (let i = 0; i < l; i++) if (dist(p, cars[carsSectors[ix][iy][i]]) <= carDetectRadius) { delIndex = i; break; } // find the "close-by" car
			if (delIndex < 0) return; // no "close-by" car found
			const car_index = carsSectors[ix][iy][delIndex];
			cars.splice(car_index, 1); // removed from cars

			/***** DO NOT CHANGE STATEMENTS' ORDER *****/
			for (let i = 0; i < 20; i++) for (let j = 0; j < 20; j++) {
				if ((i === ix) && (j === iy)) continue;
				const l_ij = carsSectors[i][j].length;
				for (let k = 0; k < l_ij; k++) if (carsSectors[i][j][k] > car_index) carsSectors[i][j][k]--;
			}
			var carsSector_new = [];
			for (let i = 0; i < l; i++) { // index removed from sectors, greater indices decremented
				if (i === delIndex) continue;
				const val = carsSectors[ix][iy][i];
				if (val < car_index) carsSector_new.push(val);
				else if (val > car_index) carsSector_new.push(val-1);
			}
			carsSectors[ix][iy] = carsSector_new;
			/*****************************************/

			clearCanvas();
			draw(); // redrawing graph
		}
		else {
			const car = {
				id: carId++, color: carColor, dest: null,
				x : p.x, y : p.y, angle: ((angle * Math.PI) / 180.00), speed, acc
			};
			carsSectors[ix][iy].push(cars.length); // push index of car inside relevant sector
			cars.push(car);
			drawCar(car);
		}
	}
	else if (mode === "destinations") {
		if (evt.shiftKey) {
			const l_cars = cars.length;
			let carIndex = -1;
			for (let i = 0; i < l_cars; i++) if ((cars[i].dest !== null) && (dist(p, WPs[cars[i].dest]) <= destStarDetectRadius)) { carIndex = i; break; } // find the car whose destination is close by
			if (carIndex < 0) return; // no car whose destination is close by
			cars[carIndex].dest = null; // remove destination for this car an redraw graph
			clearCanvas();
			draw();
		}
		else {
			const l = sectors[ix][iy].length;
			let secIndex = -1;
			for (let i = 0; i < l; i++) if (dist(p, WPs[sectors[ix][iy][i]]) <= nodeDetectRadius) { secIndex = i; break; } // find the "close-by" point
			if (secIndex < 0) return; // no "close-by" point found

			const getCarIdStr = window.prompt("Please enter Car ID:"); // get the car id through prompt
			const getCarId = parseInt(getCarIdStr);
			var carIndex = -1;
			const l_cars = cars.length;
			for (let i = 0; i < l_cars; i++) if (cars[i].id === getCarId) { carIndex = i; break; }
			if (carIndex < 0) {
				window.alert(`No car found with ID = \"${getCarIdStr}\"`);
				return;
			}
			if (cars[carIndex].dest !== null) {
				window.alert(`A destination already exists for car with ID = \"${getCarIdStr}\". Please delete that destination first.`);
				return;
			}
			
			cars[carIndex].dest = sectors[ix][iy][secIndex]; // actual insertion of destination
			clearCanvas();
			draw();
		}
	}
	// do something else for other modes
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
			for (let i = 0; i < l; i++) if (dist(p, WPs[sectors[ix][iy][i]]) <= nodeDetectRadius) { secIndex = i; break; } // find the "close-by" point
			if (secIndex < 0) return; // no "close-by" point found - do nothing
			const ptIndex = sectors[ix][iy][secIndex];
			if (edgeStart < 0) { // new selection being made
				edgeStart = ptIndex;
				WPs[ptIndex].selected = true;
			} else { // must insert edge now and remove selection
				if ((edgeStart !== ptIndex) && (NBs[edgeStart].map(x => x.idx).indexOf(ptIndex) < 0)) {
					const wt = (speed > 0) ? ((10.0 * dist(WPs[edgeStart], WPs[ptIndex])) / speed) : infWeight; // milliseconds
					NBs[edgeStart].push({ idx : ptIndex, wt });
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
	cars = [];
	for (let i = 0; i < 20; i++) for (let j = 0; j < 20; j++) { sectors[i][j] = []; carsSectors[i][j] = []; }
	edgeStart = -1;
	carId = 0;
	homeTransform();
}

document.addEventListener('keypress', (evt) => {
	const k = evt.key.toLowerCase();
	switch(k) {
		case 'n': document.getElementById("nav").click(); break;
		case 'w': document.getElementById("node").click(); break;
		case 'e': document.getElementById("edge").click(); break;
		case 'c': document.getElementById("cars").click(); break;
		case 'd': document.getElementById("destinations").click(); break;
		case 'h': document.getElementById("homeBtn").click(); break;
		case 'x': document.getElementById("clearBtn").click(); break;
		case 'i': document.getElementById("importJsonBtn").click(); break;
		case 'p': document.getElementById("downloadPngBtn").click(); break;
		case 'j': document.getElementById("downloadJsonBtn").click(); break;
		case 's': document.getElementById("showCars").click(); break;
		case 'b': document.getElementById("darkMode").click(); break;
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
		"cars" : cars,
		"sectors" : sectors,
		"carsSectors" : carsSectors,
	};
	var dwnldNode = document.createElement('a');
	dwnldNode.setAttribute("href", "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(jsonData)));
	dwnldNode.setAttribute("download", "graph.json");
	document.body.appendChild(dwnldNode); // required for firefox
	dwnldNode.click();
	dwnldNode.remove();
}

async function importJson() {
	var confirmClear = window.prompt("Are you sure you wish to clear graph? This cannot be undone."
	+ "Type \"YES\" to confirm (won't clear if you type otherwise):");
	if (confirmClear !== "YES") return;
	var importNode = document.createElement('input');
	importNode.setAttribute("type", "file");
	importNode.addEventListener('change', (evt) => {
		if (evt.target.files.length < 1) return;
		var reader = new FileReader();
		reader.readAsText(evt.target.files[0], "UTF-8");
		reader.onload = (e) => {
			var jsonData;
			try {
				jsonData = JSON.parse(e.target.result); // assume success
				WPs = jsonData.waypoints;
				NBs = jsonData.neighbours;
				sectors = jsonData.sectors;
				cars = jsonData.cars;
				carsSectors = jsonData.carsSectors;
				carId = 0;
				cars.forEach(car => { if (car.id >= carId) carId = (car.id + 1); });
				homeTransform();
			}
			catch (ex) {
				corrId = uuidv4();
				alert(`Error in reading file. See console (Correlation ID: ${corrId}).`);
				console.error(`[${corrId}] Error in reading file:`, ex);
			}
		}
		reader.onerror = (evt) => {
			corrId = uuidv4();
			alert(`Error in reading file. See console (Correlation ID: ${corrId}).`);
			console.error(`[${corrId}] Error in reading file:`, evt);
		}
	});
	importNode.click();
}


const delay = ms => new Promise(res => setTimeout(res, ms)); // personalized delay function

class Player {
	data = {} // where car data is stored
	frames = [] // array[ { id : { ts, x, y, phi, v } } ]
	numFrames = -1;
	frameSize = 20.0;
	playRate = 0.5;
	
	setData (id, trajData) { // carId, array[ { ts, x, y, phi, v } ]
		this.data[id] = trajData;
	}

	interpolate() {
		let tsMax = -1;
		for (let id in this.data) {
			const tmp = Math.max(...(this.data[id].map(entry => entry.ts)));
			if (tmp > tsMax) tsMax = tmp;
		}
		this.numFrames = Math.ceil(tsMax / this.frameSize) + 1;
		if (this.numFrames < 1) {
			console.log("Error in computing number of time frames.");
			return; // can do nothing
		}

		this.frames = [];
		for (let i = 0; i < this.numFrames; i++) {
			let obj = {};
			for (let id in this.data) obj[id] = { x : 0, y : 0, phi : 0, v : 0 };
			this.frames.push(obj);
		}

		for (let id in this.data) {
			const arr = this.data[id];
			const l_arr = arr.length;
			if (l_arr > 0) {
				// for starting few frames, when first data entry has not yet arrived
				const fEnd = (Math.ceil(arr[0].ts / this.frameSize) - 1), fStart = Math.ceil(arr[l_arr-1].ts / this.frameSize);
				for (let j = 0; j <= fEnd; j++) {
					this.frames[j][id].x = arr[0].x; this.frames[j][id].y = arr[0].y;
				}
				// for ending few frames, when last data entry has already finished
				for (let j = fStart; j < this.numFrames; j++) {
					this.frames[j][id].x = arr[l_arr-1].x; this.frames[j][id].y = arr[l_arr-1].y;
				}
			}
			for (let i = 0; i < l_arr-1; i++) {
				const fStart = Math.ceil(arr[i].ts / this.frameSize);
				const fEnd = Math.ceil(arr[i+1].ts / this.frameSize) - 1;
				for (let j = fStart; j <= fEnd; j++) {
					const { ts, x, y, phi, v } = arr[i];
					this.frames[j][id].phi = phi; this.frames[j][id].v = v;
					const dt = (this.frameSize * j) - ts; // milliseconds
					this.frames[j][id].x = x + (v * dt * 0.1 * Math.cos(phi * Math.PI / 180.0));
					this.frames[j][id].y = y + (v * dt * 0.1 * Math.sin(phi * Math.PI / 180.0));
				}
			}
		}
	}

	async play() {
		const l_frames = this.frames.length;
		for (let i = 0; i < l_frames; i++) {
			// if (i > 200) return;
			for (let id in this.frames[i]) {
				const tmpCar = this.frames[i][id]; // { x, y, phi, v }
				// first find this car with carId = id
				const _idx = cars.findIndex(c => (c.id === parseInt(id)));
				if (_idx === -1) continue; // can do nothing

				const { ix, iy } = getSectorIndex(cars[_idx]);
				carsSectors[ix][iy] = carsSectors[ix][iy].filter(x => (x !== _idx)); // removed _idx from carsSectors
				
				const newIxIy = getSectorIndex(tmpCar);
				carsSectors[newIxIy.ix][newIxIy.iy].push(_idx);

				cars[_idx].ts = (this.frameSize * i);
				cars[_idx].x = tmpCar.x; cars[_idx].y = tmpCar.y;
				cars[_idx].angle = ((tmpCar.phi * Math.PI) / 180.00);
				cars[_idx].speed = tmpCar.v;
			}

			clearCanvas();
			draw();
			await delay(this.frameSize / this.playRate);
		}
	}

	next() {
		if (this.trace.length < 1) { console.log("NOTHING TO TRACE!!!"); return; }
		if (this.nextIdx == this.trace.length) {
			if (mode !== "rewind") { console.log("END OF TRACE!!!"); return; }
			else this.nextIdx = 0;
		}

		const tmpCar = this.trace[this.nextIdx]; // ts, id, x, y, phi, v

		// find car with id = tmpCar.id
		const _idx = cars.findIndex(c => (c.id === tmpCar.id));
		if (_idx === -1) return; // can do nothing
		
		const { ix, iy } = getSectorIndex(cars[_idx]);
		carsSectors[ix][iy] = carsSectors[ix][iy].filter(x => (x !== _idx)); // removed _idx from carsSectors
		
		const newIxIy = getSectorIndex(tmpCar);
		carsSectors[newIxIy.ix][newIxIy.iy].push(_idx);

		cars[_idx].ts = tmpCar.ts;
		cars[_idx].x = tmpCar.x; cars[_idx].y = tmpCar.y;
		cars[_idx].angle = ((tmpCar.phi * Math.PI) / 180.00);
		cars[_idx].speed = tmpCar.v;
		
		const prevShowCars = showCars;
		showCars = false; // for spoofing since we shall later manually draw the cars
		clearCanvas();
		draw();
		if (prevShowCars) {
			showCars = true;
			// now draw all cars except the one with id = tmpCar.id
			cars.forEach((car) => {
				if (car.id !== tmpCar.id) drawCar(car);
			});
			drawCar(cars[_idx]); // the last one for overlap
		}

		this.nextIdx++;
	}

	rewind() {
		this.nextIdx = 0;
	}
}


async function simulateAndPlay() {
	if (isSimAndPlay) return;
	isSimAndPlay = true;
	document.getElementById("simStatus").innerHTML = "Simulating...";
	await fetch("http://127.0.0.1:5000/simulate", {
		method: "POST",
		mode: "cors",
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({
			"waypoints" : WPs.map((p) => { return { x : p.x, y : p.y }; }), // necessary since WPs is Array of SVGPoint
			"neighbours" : NBs,
			"cars" : cars,
			"sectors" : sectors,
			"carsSectors" : carsSectors,
		})
	})
	.then(resp => resp.json())
	.then(
		async (trajData) => {
			document.getElementById("simStatus").innerHTML = "<b style=\"color: green;\">Now Playing...</b>";
			// here, enter code to play stuff (awaited playing)
			pl = new Player();
			for (_id in trajData) pl.setData(_id, trajData[_id]);
			pl.interpolate();
			pl.playRate = parseFloat(document.getElementById("playRate").value.trim());
			await pl.play();
			document.getElementById("simStatus").innerHTML = "<b style=\"color: yellow;\">NOTE: You will have to reimport the graph to replay.</b>";
		},
		(error) => {
			document.getElementById("simStatus").innerHTML = "<b style=\"color: red;\">Error in Simulation</b>";
			console.log(error);
		}
	);
	isSimAndPlay = false;
}

/**** Don't remove this function does as it keeps track of transforms in he form of a matrix. ****/
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
	document.getElementById("acc").value = 0.00; // default acceleration
	document.getElementById("angle").value = 0.00; // default angle
	document.getElementById("carColor").value = "#F00"; // default car color (red)
	document.getElementById("showCars").checked = true; // defualt "Show Cars"
	document.getElementById("homeBtn").addEventListener('click', homeTransform, false);
	document.getElementById("clearBtn").addEventListener('click', clearGraph, false);
	document.getElementById("importJsonBtn").addEventListener('click', importJson, false);
	document.getElementById("downloadPngBtn").addEventListener('click', downloadPng, false);
	document.getElementById("downloadJsonBtn").addEventListener('click', downloadJson, false);
	document.getElementById("speed").addEventListener('change', (evt) => { speed = parseFloat(evt.target.value.trim()); }, false);
	document.getElementById("acc").addEventListener('change', (evt) => { acc = parseFloat(evt.target.value.trim()); }, false);
	document.getElementById("angle").addEventListener('change', (evt) => { angle = parseFloat(evt.target.value.trim()); }, false);
	document.getElementById("carColor").addEventListener('change', (evt) => { carColor = evt.target.value.trim(); }, false);
	document.getElementById("showCars").addEventListener('change', () => {
		showCars = document.getElementById("showCars").checked;
		clearCanvas();
		draw();
	}, false);
	document.getElementById("darkMode").addEventListener('change', () => {
		useDarkMode = document.getElementById("darkMode").checked;
		const modeName = useDarkMode ? "dark" : "light";
		document.body.style.backgroundColor = docBgClr[modeName];
		document.body.style.color = docTxtClr[modeName];
		canvas.style.backgroundColor = canvasBgClr[modeName];
	}, false);
	document.getElementById("darkMode").checked = false;
	document.getElementById("darkMode").click();
	// radio mode changer
	document.querySelectorAll('input[type=radio][name="mode"]').forEach(radio => {
		radio.addEventListener('change', () => { mode = radio.value; });
	});
	document.getElementById("playBtn").addEventListener('click', simulateAndPlay, false);
}

window.onbeforeunload = function() { // not satisfactory
	return "Are you sure you wish to leave? Graph cannot be retrieved. Type \"YES\" to leave (won't leave if you type otherwise):";
}

window.onresize = function() {
	clearCanvas();
	canvas.width = window.innerWidth * 0.85; canvas.height = window.innerHeight * 0.85;
	draw();
}

/**********************************************/
/********** BEGIN ACTUAL CODING HERE **********/
/**********************************************/

class Tracer {
	data = {} // where car data is stored
	nextIdx = 0 // index in this.trace to be shown
	trace = [] // { ts, id, x, y, phi, v }
	mode = "" // or "rewind"

	setData (id, trajData) { // carId, array[ { ts, x, y, phi, v } ]
		this.data[id] = trajData;
		trajData.forEach((entry) => {
			this.trace.push({ ...entry, id });
		});
		this.trace.sort((a, b) => (a.ts - b.ts));
		this.nextIdx = 0;
	}

	next() {
		if (this.trace.length < 1) { console.log("NOTHING TO TRACE!!!"); return; }
		if (this.nextIdx == this.trace.length) {
			if (mode !== "rewind") { console.log("END OF TRACE!!!"); return; }
			else this.nextIdx = 0;
		}

		const tmpCar = this.trace[this.nextIdx]; // ts, id, x, y, phi, v

		// find car with id = tmpCar.id
		const _idx = cars.findIndex(c => (c.id === tmpCar.id));
		if (_idx === -1) {
			this.nextIdx++;
			return; // can do nothing
		}
		
		const { ix, iy } = getSectorIndex(cars[_idx]);
		carsSectors[ix][iy] = carsSectors[ix][iy].filter(x => (x !== _idx)); // removed _idx from carsSectors
		
		const newIxIy = getSectorIndex(tmpCar);
		carsSectors[newIxIy.ix][newIxIy.iy].push(_idx);

		cars[_idx].ts = tmpCar.ts;
		cars[_idx].x = tmpCar.x; cars[_idx].y = tmpCar.y;
		cars[_idx].angle = ((tmpCar.phi * Math.PI) / 180.00);
		cars[_idx].speed = tmpCar.v;
		
		const prevShowCars = showCars;
		showCars = false; // for spoofing since we shall later manually draw the cars
		clearCanvas();
		draw();
		if (prevShowCars) {
			showCars = true;
			// now draw all cars except the one with id = tmpCar.id
			cars.forEach((car) => {
				if (car.id !== tmpCar.id) drawCar(car);
			});
			drawCar(cars[_idx]); // the last one for overlap
		}

		this.nextIdx++;
	}

	rewind() {
		this.nextIdx = 0;
	}
}
