import { useState, useEffect } from 'react';

const useStopwatch = () => {
  const [seconds, setSeconds] = useState(0);
  const [isActive, setIsActive] = useState(false);
  
  useEffect(() => {
    let interval = null;
    if (isActive) {
      interval = setInterval(() => {
        setSeconds(prevSeconds => prevSeconds + 1);
      }, 1000);
    } else if (!isActive && seconds !== 0) {
      clearInterval(interval);
    }
    return () => clearInterval(interval);
  }, [isActive, seconds]);

  const start = () => setIsActive(true);
  const pause = () => setIsActive(false);
  const reset = () => {
    setIsActive(false);
    setSeconds(0);
  };
  
  return { seconds, isActive, start, pause, reset };
};

export default useStopwatch;