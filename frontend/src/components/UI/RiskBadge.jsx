export default function RiskBadge({ level }) {
  const config = {
    low: { label: 'Low Risk', classes: 'bg-success-500/15 text-success-400 border-success-500/30' },
    moderate: { label: 'Moderate Risk', classes: 'bg-yellow-500/15 text-yellow-400 border-yellow-500/30' },
    high: { label: 'High Risk', classes: 'bg-danger-500/15 text-danger-400 border-danger-500/30' },
    positive: { label: 'Positive', classes: 'bg-danger-500/15 text-danger-400 border-danger-500/30' },
    negative: { label: 'Negative', classes: 'bg-success-500/15 text-success-400 border-success-500/30' },
  };

  const c = config[level] || config.low;

  return (
    <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold border ${c.classes}`}>
      <span className={`w-1.5 h-1.5 rounded-full mr-1.5 ${
        level === 'low' || level === 'negative' ? 'bg-success-400' :
        level === 'moderate' ? 'bg-yellow-400' : 'bg-danger-400'
      }`} />
      {c.label}
    </span>
  );
}
