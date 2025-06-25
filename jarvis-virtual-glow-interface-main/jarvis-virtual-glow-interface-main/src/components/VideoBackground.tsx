
import React from 'react';

interface VideoBackgroundProps {
  mode: 'conversation' | 'coding';
}

export const VideoBackground: React.FC<VideoBackgroundProps> = ({ mode }) => {
  // Since we don't have actual video files, we'll create animated CSS backgrounds
  const backgroundClass = mode === 'conversation' 
    ? 'bg-gradient-to-br from-green-900/20 via-black to-green-800/20' 
    : 'bg-gradient-to-br from-red-900/20 via-black to-red-800/20';

  return (
    <div className={`absolute inset-0 ${backgroundClass}`}>
      {/* Animated particles effect */}
      <div className="absolute inset-0">
        {[...Array(20)].map((_, i) => (
          <div
            key={i}
            className={`absolute w-1 h-1 rounded-full ${mode === 'conversation' ? 'bg-jarvis-green' : 'bg-jarvis-red'} opacity-30`}
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animation: `pulse-glow ${2 + Math.random() * 3}s infinite`,
              animationDelay: `${Math.random() * 2}s`
            }}
          />
        ))}
      </div>
      
      {/* Circuit board pattern overlay */}
      <div 
        className="absolute inset-0 opacity-10"
        style={{
          backgroundImage: `
            linear-gradient(90deg, ${mode === 'conversation' ? '#00ff41' : '#ff3333'} 1px, transparent 1px),
            linear-gradient(${mode === 'conversation' ? '#00ff41' : '#ff3333'} 1px, transparent 1px)
          `,
          backgroundSize: '50px 50px',
          backgroundPosition: '0 0, 25px 25px'
        }}
      />
    </div>
  );
};
