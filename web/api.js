// AUM SHREEGANESHAAYA NAMAH|| AUM SHREEHANUMATE NAMAH||
// const serverUri = "http://localhost:5000";


class Hello extends React.Component {
  render() {
    return <h1>herro</h1>;
  }
}

ReactDOM.render(<Hello />, document.getElementById('main'));

function getData() {
  fetch(serverUri).then(resp => resp.json()).then(
    success => { console.log("Success", success) },
    error => { console.log("Error", error) }
  )
}
