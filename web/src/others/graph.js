// AUM SHREEGANESHAAYA NAMAH||
const serverUri = "http://localhost:5000";

const canvas = document.querySelector('canvas');
const context = canvas.getContext('2d');

var nodes = [];

function resize() {
  canvas.width = window.innerWidth * 0.8;
  canvas.height = window.innerHeight * 0.8;
}

window.onresize = resize;
resize();

function drawNode(node) {
  context.beginPath();
  context.fillStyle = node.fillStyle;
  context.arc(node.x, node.y, node.radius, 0, Math.PI * 2, true);
  context.strokeStyle = node.strokeStyle;
  context.stroke();
  context.fill();
}

function zoom(x) {
  context.scale(x, x);
}

// Mouse Functions
function click(e) {
  let node = {
      x: e.x,
      y: e.y,
      radius: 10,
      fillStyle: '#22cccc',
      strokeStyle: '#009999'
  };
  nodes.push(node);
  drawNode(node);
}

window.onclick = click;

var selection = undefined;

function within(x, y) {
    return nodes.find(n => {
        return x > (n.x - n.radius) && 
            y > (n.y - n.radius) &&
            x < (n.x + n.radius) &&
            y < (n.y + n.radius);
    });
}

function move(e) {
    if (selection) {
        selection.x = e.x;
        selection.y = e.y;
        drawNode(selection);
    }
}

function down(e) {
    let target = within(e.x, e.y);
    if (target) {
        selection = target;
    }
}

function up(e) {
    selection = undefined;
}

window.onmousemove = move;
window.onmousedown = down;
window.onmouseup = up;



// function draw() {
//   const canvas = document.querySelector('#canvas');

//   if (!canvas.getContext) {
//       return;
//   }
//   const ctx = canvas.getContext('2d');

//   // set line stroke and line width
//   ctx.strokeStyle = 'red';
//   ctx.lineWidth = 5;

//   // draw a red line
//   ctx.beginPath();
//   ctx.moveTo(100, 100);
//   ctx.lineTo(300, 100);
//   ctx.stroke();
// }
// draw();

function getData() {
  fetch(serverUri).then(resp => resp.json()).then(
    success => { console.log("Success", success) },
    error => { console.log("Error", error) }
  )
}
