export default function DisclaimerBanner({ className = '' }) {
  return (
    <div className={`rounded-xl border border-yellow-500/20 bg-yellow-500/5 p-4 ${className}`}>
      <div className="flex gap-3">
        <span className="text-yellow-400 text-lg flex-shrink-0">⚠️</span>
        <div>
          <h4 className="text-sm font-semibold text-yellow-400 mb-1">Medical Disclaimer</h4>
          <p className="text-xs text-slate-400 leading-relaxed">
            This AI-powered tool is designed for educational and screening purposes only.
            It does <strong className="text-slate-300">not</strong> replace professional medical diagnosis.
            Always consult a qualified healthcare provider for medical advice, diagnosis, and treatment.
          </p>
        </div>
      </div>
    </div>
  );
}
