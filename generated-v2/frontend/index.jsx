import React from 'react';
import ReactDOM from 'react-dom';
import Stopwatch from './Stopwatch';
import '../styles/globals.css';

const App = () => {
  return <Stopwatch />;
};

ReactDOM.render(<App />, document.getElementById('root'));