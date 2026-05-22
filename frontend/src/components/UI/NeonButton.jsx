import { motion } from 'framer-motion';

const variants = {
  primary: 'neon-btn',
  outline: 'neon-btn-outline',
  danger: 'neon-btn neon-btn-danger',
  success: 'neon-btn neon-btn-success',
};

export default function NeonButton({
  children,
  variant = 'primary',
  className = '',
  disabled = false,
  loading = false,
  onClick,
  type = 'button',
  ...props
}) {
  return (
    <motion.button
      type={type}
      className={`${variants[variant]} ${className} ${disabled || loading ? 'opacity-50 cursor-not-allowed' : ''}`}
      whileHover={!disabled && !loading ? { scale: 1.03 } : {}}
      whileTap={!disabled && !loading ? { scale: 0.97 } : {}}
      onClick={onClick}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <span className="flex items-center justify-center gap-2">
          <span className="spinner !w-5 !h-5 !border-2" />
          <span>Processing...</span>
        </span>
      ) : (
        children
      )}
    </motion.button>
  );
}
