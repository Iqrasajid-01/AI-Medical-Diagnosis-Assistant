import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { getHistory } from '../services/api';
import { useAuth } from '../context/AuthContext';
import GlassCard from '../components/UI/GlassCard';
import RiskBadge from '../components/UI/RiskBadge';
import LoadingSpinner from '../components/UI/LoadingSpinner';

export default function Dashboard() {
  const { user } = useAuth();
  const [recent, setRecent] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getHistory().then(res => {
      setRecent((res.data.predictions || []).slice(0, 5));
    }).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const diseaseIcons = {
    diabetes: '🩸',
    heart: '❤️',
    parkinsons: '🧠',
  };

  const stats = [
    { label: 'Total Predictions', value: recent.length, icon: '📊', color: 'from-primary-500 to-accent-500' },
    { label: 'High Risk Flags', value: recent.filter(r => r.prediction_result === 1).length, icon: '⚠️', color: 'from-danger-500 to-danger-400' },
    { label: 'Low Risk', value: recent.filter(r => r.prediction_result === 0).length, icon: '✅', color: 'from-success-500 to-success-400' },
    { label: 'Member Since', value: user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'Today', icon: '🕐', color: 'from-accent-500 to-primary-500' },
  ];

  return (
    <div className="space-y-8">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-3xl font-bold text-white mb-2">Dashboard</h1>
        <p className="text-slate-400">Welcome back, {user?.username}</p>
      </motion.div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((s, i) => (
          <motion.div key={s.label} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}>
            <GlassCard className="flex items-center gap-4">
              <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${s.color} flex items-center justify-center text-xl`}>
                {s.icon}
              </div>
              <div>
                <p className="text-2xl font-bold text-white">{s.value}</p>
                <p className="text-xs text-slate-500">{s.label}</p>
              </div>
            </GlassCard>
          </motion.div>
        ))}
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <GlassCard>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-white">Quick Actions</h2>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <Link to="/predict" className="p-4 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-500/5 border border-primary-500/20 hover:border-primary-500/40 transition-all text-center group">
              <span className="text-2xl block mb-2 group-hover:scale-110 transition-transform">🩸</span>
              <span className="text-sm font-medium text-white">Diabetes</span>
              <span className="text-xs text-slate-500 block mt-1">Check risk</span>
            </Link>
            <Link to="/predict" className="p-4 rounded-xl bg-gradient-to-br from-danger-500/10 to-danger-500/5 border border-danger-500/20 hover:border-danger-500/40 transition-all text-center group">
              <span className="text-2xl block mb-2 group-hover:scale-110 transition-transform">❤️</span>
              <span className="text-sm font-medium text-white">Heart Disease</span>
              <span className="text-xs text-slate-500 block mt-1">Check risk</span>
            </Link>
            <Link to="/predict" className="p-4 rounded-xl bg-gradient-to-br from-accent-500/10 to-accent-500/5 border border-accent-500/20 hover:border-accent-500/40 transition-all text-center group">
              <span className="text-2xl block mb-2 group-hover:scale-110 transition-transform">🧠</span>
              <span className="text-sm font-medium text-white">Parkinson's</span>
              <span className="text-xs text-slate-500 block mt-1">Voice analysis</span>
            </Link>
          </div>
        </GlassCard>

        <GlassCard>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-white">Recent Predictions</h2>
            <Link to="/history" className="text-xs text-primary-400 hover:text-primary-300 transition-colors">View all</Link>
          </div>
          {loading ? (
            <LoadingSpinner size="sm" className="py-8" />
          ) : recent.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-slate-500 text-sm mb-3">No predictions yet</p>
              <Link to="/predict" className="neon-btn text-sm inline-block">Start Diagnosis</Link>
            </div>
          ) : (
            <div className="space-y-2">
              {recent.map(r => (
                <div key={r.id} className="flex items-center justify-between p-3 rounded-lg bg-white/5">
                  <div className="flex items-center gap-3">
                    <span className="text-lg">{diseaseIcons[r.disease_type] || '🔬'}</span>
                    <div>
                      <p className="text-sm font-medium text-white capitalize">{r.disease_type}</p>
                      <p className="text-xs text-slate-500">{new Date(r.created_at).toLocaleDateString()}</p>
                    </div>
                  </div>
                  <RiskBadge level={r.prediction_result === 1 ? 'high' : 'low'} />
                </div>
              ))}
            </div>
          )}
        </GlassCard>
      </div>
    </div>
  );
}
