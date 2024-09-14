import './navbar.css';
import tcslogo from "../assets/tcslogo.png";
import rapidlabs from "../assets/rapidlabs.png";

function Navbar() {
    return (
      <div className="App">
        <h2> JnJ Cohort Rapid 2.O</h2>
          <div className="logo">
            <img src={tcslogo} alt="img"/>
            <img src={rapidlabs} alt="img"/>
            <ul>
            <li><a href="http://localhost:3000/efficacy">Efficacy</a></li>
            <li><a href="http://localhost:3000/AdverseEffect">AdverseEffect</a></li>
            </ul>
          </div>
          <label><b>Upload your file here :</b></label>
          <button type='input'>Upload</button>
      </div>
    );
  }
  
export default Navbar;