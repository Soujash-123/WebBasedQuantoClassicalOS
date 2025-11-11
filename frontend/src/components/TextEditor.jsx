import React, { useState, useEffect, useRef } from 'react';

const TextEditor = ({ content, onSave, onCancel }) => {
  const [text, setText] = useState(content || '');
  const textareaRef = useRef(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  }, []);

  const handleKeyDown = (e) => {
    // Handle Ctrl+S to save
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
      e.preventDefault();
      handleSave();
    }
    // Handle Escape to cancel
    else if (e.key === 'Escape') {
      handleCancel();
    }
  };

  const handleSave = () => {
    onSave(text);
  };

  const handleCancel = () => {
    onCancel();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center p-4 z-50">
      <div className="bg-gray-900 rounded-lg shadow-xl w-full max-w-4xl h-[80vh] flex flex-col">
        <div className="bg-gray-800 px-4 py-2 flex justify-between items-center border-b border-gray-700">
          <h3 className="text-white font-mono">Nano Editor</h3>
          <div className="flex space-x-2">
            <button 
              onClick={handleSave}
              className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
            >
              Save (Ctrl+S)
            </button>
            <button 
              onClick={handleCancel}
              className="px-3 py-1 bg-gray-600 text-white rounded hover:bg-gray-700 text-sm"
            >
              Cancel (Esc)
            </button>
          </div>
        </div>
        <div className="flex-1 overflow-auto">
          <textarea
            ref={textareaRef}
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            className="w-full h-full p-4 font-mono text-white bg-gray-900 border-0 focus:outline-none resize-none"
            spellCheck="false"
          />
        </div>
        <div className="bg-gray-800 px-4 py-2 text-xs text-gray-400 border-t border-gray-700">
          [ Ctrl+S: Save | Esc: Cancel ]
        </div>
      </div>
    </div>
  );
};

export default TextEditor;
