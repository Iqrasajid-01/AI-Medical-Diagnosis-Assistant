import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';

export default function ConfidenceBar({ value = 0, label, color = 'primary' }) {
  const [width, setWidth] = useState(0);

  useEffect(() => {
    const t = setTimeout(() => setWidth(value), 100);
    return () => clearTimeout(t);
  }, [value]);

  const colors = {
    primary: { bar: 'from-primary-500 to-primary-400', glow: 'rgba(6,182,212,0.4)' },
    danger: { bar: 'from-danger-500 to-danger-400', glow: 'rgba(244,63,94,0.4)' },
    success: { bar: 'from-success-500 to-success-400', glow: 'rgba(16,185,129,0.4)' },
    accent: { bar: 'from-accent-500 to-accent-400', glow: 'rgba(59,130,246,0.4)' },
  };

  const c = colors[color] || colors.primary;

  return (
    <div className="w-full">
      {label && (
        <div className="flex justify-between items-center mb-1.5">
          <span className="text-sm text-slate-400">{label}</span>
          <motion.span
            className="text-sm font-semibold text-white"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            {width.toFixed(1)}%
          </motion.span>
        </div>
      )}
      <div className="w-full h-3 rounded-full bg-white/5 overflow-hidden">
        <motion.div
          className={`h-full rounded-full bg-gradient-to-r ${c.bar}`}
          initial={{ width: 0 }}
          animate={{ width: `${width}%` }}
          transition={{ duration: 1, ease: 'easeOut' }}
          style={{ boxShadow: `0 0 12px ${c.glow}` }}
        />
      </div>
    </div>
  );
}
