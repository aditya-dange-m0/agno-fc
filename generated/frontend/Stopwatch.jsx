import React from 'react';
import useStopwatch from './useStopwatch';

const Stopwatch = () => {
  const { seconds, isActive, start, pause, reset } = useStopwatch();

  return (
    <div className="flex flex-col items-center justify-center mt-10">
      <h1 className="text-4xl font-bold">Stopwatch</h1>
      <div className="text-2xl mt-4">{seconds}s</div>
      <div className="flex space-x-4 mt-4">
        <button onClick={start} className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">Start</button>
        <button onClick={pause} className="bg-yellow-500 text-white px-4 py-2 rounded hover:bg-yellow-600">Pause</button>
        <button onClick={reset} className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600">Reset</button>
      </div>
    </div>
  );
};

export default Stopwatch;