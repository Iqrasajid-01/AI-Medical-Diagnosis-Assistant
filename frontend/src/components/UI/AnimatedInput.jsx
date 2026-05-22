import { useState } from 'react';

export default function AnimatedInput({
  label,
  type = 'text',
  value,
  onChange,
  placeholder,
  required = false,
  tooltip,
  error,
  className = '',
  ...props
}) {
  const [focused, setFocused] = useState(false);

  return (
    <div className={`relative ${className}`}>
      <div className="flex items-center justify-between mb-1.5">
        {label && (
          <label className={`text-sm font-medium transition-colors duration-200 ${
            focused ? 'text-primary-400' : 'text-slate-400'
          }`}>
            {label}
            {required && <span className="text-danger-400 ml-0.5">*</span>}
          </label>
        )}
        {tooltip && (
          <div className="relative group">
            <span className="text-slate-500 hover:text-primary-400 cursor-help transition-colors text-xs">
              ℹ️
            </span>
            <div className="absolute bottom-full right-0 mb-2 w-56 p-2.5 rounded-lg bg-dark-800 border border-white/10 text-xs text-slate-300 opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-50 shadow-xl">
              {tooltip}
            </div>
          </div>
        )}
      </div>
      <input
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        required={required}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        className="input-glow"
        {...props}
      />
      {error && (
        <p className="mt-1 text-xs text-danger-400">{error}</p>
      )}
    </div>
  );
}
