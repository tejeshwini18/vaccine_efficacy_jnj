import logo from './logo.svg';
import './App.css';
import Navbar from './components/navbar';
import Efficacy from './components/efficacy';
import AdverseEffect from './components/AdverseEffect';
import { Route, Router } from 'react-router-dom';

function App() {
  return (
    <div className="App"> 
      <Navbar/>
    </div>
  );
}

export default App;
