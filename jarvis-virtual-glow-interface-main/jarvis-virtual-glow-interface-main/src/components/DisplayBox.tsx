
import React, { useEffect, useRef } from 'react';

interface DisplayBoxProps {
  responses: string[];
  mode: 'conversation' | 'coding';
}

export const DisplayBox: React.FC<DisplayBoxProps> = ({ responses, mode }) => {
  const scrollRef = useRef<HTMLDivElement>(null);
  const themeColor = mode === 'conversation' ? 'text-jarvis-green' : 'text-jarvis-red';
  const borderColor = mode === 'conversation' ? 'border-jarvis-green' : 'border-jarvis-red';
  const bgColor = mode === 'conversation' ? 'bg-jarvis-green/5' : 'bg-jarvis-red/5';

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [responses]);

  return (
    <div className={`${borderColor} border-2 rounded-lg ${bgColor} p-6 animate-border-glow min-h-[400px] max-h-[500px]`}>
      <div className="flex items-center justify-between mb-4">
        <h2 className={`${themeColor} font-bold text-xl animate-text-glow`}>
          JARVIS DISPLAY
        </h2>
        <div className="flex space-x-2">
          <div className={`w-2 h-2 rounded-full ${themeColor} animate-pulse`}></div>
          <div className={`w-2 h-2 rounded-full ${themeColor} animate-pulse`} style={{ animationDelay: '0.5s' }}></div>
          <div className={`w-2 h-2 rounded-full ${themeColor} animate-pulse`} style={{ animationDelay: '1s' }}></div>
        </div>
      </div>
      
      <div ref={scrollRef} className="overflow-y-auto max-h-full space-y-3">
        {responses.map((response, index) => (
          <div
            key={index}
            className={`${themeColor} font-mono text-lg leading-relaxed animate-fade-in`}
            style={{ animationDelay: `${index * 0.2}s` }}
          >
            <span className="opacity-50">▸ </span>
            {response}
          </div>
        ))}
        <div className={`${themeColor} animate-pulse inline-block`}>█</div>
      </div>
    </div>
  );
};
