
import React, { useState, useEffect } from 'react';

interface SystemInfoProps {
  mode: 'conversation' | 'coding';
}

export const SystemInfo: React.FC<SystemInfoProps> = ({ mode }) => {
  const [currentTime, setCurrentTime] = useState(new Date());
  const [battery] = useState(87); // Simulated battery level

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const themeColor = mode === 'conversation' ? 'text-jarvis-green' : 'text-jarvis-red';

  return (
    <div className={`${themeColor} text-right text-sm space-y-1 font-mono`}>
      <div className="animate-text-glow">
        {currentTime.toLocaleTimeString()}
      </div>
      <div className={`${themeColor} opacity-70`}>
        {currentTime.toLocaleDateString()}
      </div>
      <div className="flex items-center justify-end space-x-2">
        <span className="text-xs">PWR</span>
        <div className={`w-6 h-2 border border-current rounded-sm ${themeColor}`}>
          <div 
            className={`h-full bg-current rounded-sm transition-all duration-300`}
            style={{ width: `${battery}%` }}
          ></div>
        </div>
        <span className="text-xs">{battery}%</span>
      </div>
    </div>
  );
};
