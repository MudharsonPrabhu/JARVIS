
import React, { useState, useEffect } from 'react';
import { Mic, MicOff, X, Volume2, VolumeX } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { SystemInfo } from './SystemInfo';
import { CommandHistory } from './CommandHistory';
import { DisplayBox } from './DisplayBox';
import { VideoBackground } from './VideoBackground';

export const JarvisInterface = () => {
  const [mode, setMode] = useState<'conversation' | 'coding'>('conversation');
  const [inputValue, setInputValue] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [audioEnabled, setAudioEnabled] = useState(true);
  const [responses, setResponses] = useState<string[]>([
    'JARVIS AI Assistant initialized...',
    'All systems online and ready.',
  ]);
  const [commands, setCommands] = useState<string[]>([
    'System initialization complete',
    'Neural networks active',
    'Voice recognition enabled',
  ]);

  const themeColors = {
    conversation: {
      primary: 'text-jarvis-green',
      glow: 'shadow-jarvis-green-glow',
      border: 'border-jarvis-green',
      bg: 'bg-jarvis-green/10'
    },
    coding: {
      primary: 'text-jarvis-red',
      glow: 'shadow-jarvis-red-glow',
      border: 'border-jarvis-red',
      bg: 'bg-jarvis-red/10'
    }
  };

  const currentTheme = themeColors[mode];

  const handleModeToggle = () => {
    setMode(mode === 'conversation' ? 'coding' : 'conversation');
    const newResponse = mode === 'conversation' 
      ? 'Switching to Coding Mode... Development tools activated.'
      : 'Switching to Conversation Mode... Standard interface activated.';
    setResponses(prev => [...prev, newResponse]);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim()) {
      setCommands(prev => [...prev, inputValue]);
      setResponses(prev => [...prev, `Processing: ${inputValue}`]);
      setInputValue('');
    }
  };

  const toggleMicrophone = () => {
    setIsListening(!isListening);
    const status = !isListening ? 'Voice input activated' : 'Voice input deactivated';
    setCommands(prev => [...prev, status]);
  };

  return (
    <div className="fixed inset-0 bg-black text-white overflow-hidden font-orbitron">
      <VideoBackground mode={mode} />
      
      {/* Overlay with grid pattern */}
      <div className="absolute inset-0 bg-black/70" 
           style={{
             backgroundImage: `radial-gradient(circle at 1px 1px, ${mode === 'conversation' ? '#00ff4120' : '#ff333320'} 1px, transparent 0)`,
             backgroundSize: '20px 20px'
           }}>
      </div>

      {/* Main Container */}
      <div className="relative z-10 h-full flex flex-col">
        {/* Header */}
        <header className="flex justify-between items-center p-6 border-b border-current">
          <div className="flex items-center space-x-4">
            <div className={`w-3 h-3 rounded-full ${currentTheme.primary} animate-pulse-glow`}></div>
            <div>
              <h1 className={`text-2xl md:text-3xl font-bold ${currentTheme.primary} animate-text-glow`}>
                JARVIS VIRTUAL ASSISTANT
              </h1>
              <p className={`text-sm ${currentTheme.primary} opacity-70`}>
                Advanced AI Interface v3.0
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <Button
              onClick={() => setAudioEnabled(!audioEnabled)}
              variant="outline"
              size="sm"
              className={`${currentTheme.border} ${currentTheme.primary} bg-transparent hover:${currentTheme.bg} animate-border-glow`}
            >
              {audioEnabled ? <Volume2 size={16} /> : <VolumeX size={16} />}
            </Button>
            <SystemInfo mode={mode} />
          </div>
        </header>

        {/* Main Content Area */}
        <div className="flex-1 flex">
          {/* Left Sidebar - Command History */}
          <aside className="w-80 border-r border-current p-4 hidden md:block">
            <CommandHistory commands={commands} mode={mode} />
          </aside>

          {/* Center - Display Box */}
          <main className="flex-1 p-6 flex flex-col justify-center">
            <DisplayBox responses={responses} mode={mode} />
            
            {/* Mode Toggle */}
            <div className="flex justify-center mt-8">
              <Button
                onClick={handleModeToggle}
                className={`${currentTheme.primary} ${currentTheme.border} bg-transparent hover:${currentTheme.bg} animate-border-glow px-8 py-3 text-lg font-bold`}
                variant="outline"
              >
                {mode === 'conversation' ? 'SWITCH TO CODING MODE' : 'SWITCH TO CONVERSATION MODE'}
              </Button>
            </div>
          </main>
        </div>

        {/* Bottom Input Area */}
        <footer className="p-6 border-t border-current">
          <div className="flex items-center space-x-4">
            <form onSubmit={handleSubmit} className="flex-1">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder={mode === 'conversation' ? 'Ask JARVIS anything...' : 'Enter code command...'}
                className={`w-full bg-transparent border-2 ${currentTheme.border} ${currentTheme.primary} p-4 rounded-lg placeholder-current placeholder-opacity-50 animate-border-glow focus:outline-none focus:ring-2 focus:ring-current`}
              />
            </form>

            <div className="flex space-x-3">
              <Button
                onClick={toggleMicrophone}
                variant="outline"
                size="lg"
                className={`${currentTheme.border} ${isListening ? currentTheme.bg : 'bg-transparent'} ${currentTheme.primary} hover:${currentTheme.bg} animate-border-glow p-4`}
              >
                {isListening ? <Mic size={24} /> : <MicOff size={24} />}
              </Button>

              <Button
                onClick={() => {
                  setInputValue('');
                  setCommands(prev => [...prev, 'Input cleared']);
                }}
                variant="outline"
                size="lg"
                className={`${currentTheme.border} ${currentTheme.primary} bg-transparent hover:${currentTheme.bg} animate-border-glow p-4`}
              >
                <X size={24} />
              </Button>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
};
