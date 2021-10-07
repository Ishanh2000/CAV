// AUM SHREEGANESHAAYA NAMAH||
import React, { Component, createRef } from 'react';

class CAV extends Component {
  constructor(props) {
    super(props);
    this.state = {
      realNodes: [],
      nodes: [],
      currLocation: { x : 0, y : 0 },
    };
    this.ref = createRef();
  }

  drawNode = (node) => {
    const ctx = this.ref.current.getContext('2d');
    ctx.beginPath();
    ctx.fillStyle = '#22cccc';
    ctx.arc(node.x, node.y, 5, 0, Math.PI * 2, true);
    ctx.strokeStyle = '#009999';
    ctx.stroke();
    ctx.fill();
  }

  drawAllNodes = () => { this.state.nodes.forEach(node => { this.drawNode(node); }); }

  getXY = (event) => {
    const rect = this.ref.current.getBoundingClientRect();
    return { x : (event.clientX - rect.left), y : (event.clientY - rect.top) };
  }

  updateCurrLocation = (event) => { this.setState({ currLocation: this.getXY(event) }); }

  addNode = (event) => { this.setState({ nodes: [...this.state.nodes, this.getXY(event) ]}); }

  componentDidUpdate() { this.drawAllNodes(); }

  setCanvasDims = () => {
    const canvas = this.ref.current;
    // Set display size (css pixels).
    const h = window.innerHeight * 0.85, w = window.innerWidth * 0.85;
    canvas.style.width = w + "px";
    canvas.style.height = h + "px";

    // Set actual size in memory (scaled to account for extra pixel density).
    var scale = window.devicePixelRatio; // <--- Change to 1 on retina screens to see blurry canvas.
    canvas.width = w * scale;
    canvas.height = h * scale;
  }

  componentDidMount() {
    window.onresize = this.setCanvasDims;
    this.setCanvasDims();
    this.drawAllNodes();
  }
  
  render() {
    const { currLocation } = this.state;

    return (<>
      <center>
        <canvas ref={this.ref} style={styles.canvas}
          onDoubleClick={this.addNode}
          onMouseMove={this.updateCurrLocation}
        />
        <br />
        <b>x = {currLocation.x}, y = {currLocation.y}</b>
      </center>
      
      <ul>
        <li>Double click to add a point.</li>
      </ul>

    </>);
  }
}

export default CAV;

const styles = {
  canvas: {
    backgroundColor: "#d8ded4",
    // width: "85%", height: "85%",
    border: "2px solid #252d20",
    margin: "2rem",
  }
}
