
import React from 'react';

interface CommandHistoryProps {
  commands: string[];
  mode: 'conversation' | 'coding';
}

export const CommandHistory: React.FC<CommandHistoryProps> = ({ commands, mode }) => {
  const themeColor = mode === 'conversation' ? 'text-jarvis-green' : 'text-jarvis-red';
  const borderColor = mode === 'conversation' ? 'border-jarvis-green' : 'border-jarvis-red';

  return (
    <div className={`h-full ${borderColor} border-2 rounded-lg p-4 animate-border-glow`}>
      <h3 className={`${themeColor} font-bold mb-4 text-lg animate-text-glow`}>
        COMMAND HISTORY
      </h3>
      <div className="space-y-2 max-h-full overflow-y-auto">
        {commands.map((command, index) => (
          <div
            key={index}
            className={`${themeColor} text-sm font-mono p-2 bg-current bg-opacity-10 rounded border-l-2 border-current animate-fade-in`}
            style={{ animationDelay: `${index * 0.1}s` }}
          >
            <span className="opacity-50">#{String(index + 1).padStart(3, '0')}</span> {command}
          </div>
        ))}
      </div>
    </div>
  );
};
