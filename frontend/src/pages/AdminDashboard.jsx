import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { adminGetUsers, adminGetPredictions, adminRetrain, adminUploadDataset } from '../services/api';
import GlassCard from '../components/UI/GlassCard';
import NeonButton from '../components/UI/NeonButton';
import LoadingSpinner from '../components/UI/LoadingSpinner';
import RiskBadge from '../components/UI/RiskBadge';

const DISEASES = ['diabetes', 'heart', 'parkinsons'];
const DISEASE_LABELS = { diabetes: 'Diabetes', heart: 'Heart Disease', parkinsons: "Parkinson's" };

export default function AdminDashboard() {
  const [tab, setTab] = useState('overview');
  const [users, setUsers] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [retraining, setRetraining] = useState(null);
  const [uploading, setUploading] = useState(null);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const fetchData = () => {
    setLoading(true);
    setError('');
    Promise.all([adminGetUsers(), adminGetPredictions()])
      .then(([uRes, pRes]) => {
        setUsers(uRes.data.users || []);
        setPredictions(pRes.data.predictions || []);
      })
      .catch(err => setError(err.response?.data?.error || 'Failed to load admin data'))
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchData(); }, []);

  const handleRetrain = async (disease) => {
    setRetraining(disease);
    setMessage('');
    setError('');
    try {
      const res = await adminRetrain(disease);
      setMessage(`✅ ${DISEASE_LABELS[disease]} model retrained. Accuracy: ${(res.data.accuracy * 100).toFixed(2)}%`);
    } catch (err) {
      setError(err.response?.data?.error || `Failed to retrain ${disease}`);
    } finally {
      setRetraining(null);
    }
  };

  const handleUpload = async (disease, file) => {
    if (!file) return;
    setUploading(disease);
    setMessage('');
    setError('');
    try {
      const formData = new FormData();
      formData.append('file', file);
      await adminUploadDataset(disease, formData);
      setMessage(`✅ Dataset uploaded for ${DISEASE_LABELS[disease]}. Use retrain to update model.`);
    } catch (err) {
      setError(err.response?.data?.error || `Failed to upload dataset`);
    } finally {
      setUploading(null);
    }
  };

  const tabs = [
    { key: 'overview', label: 'Overview', icon: '📊' },
    { key: 'models', label: 'Model Management', icon: '🧠' },
    { key: 'users', label: 'Users', icon: '👥' },
    { key: 'data', label: 'Datasets', icon: '📁' },
  ];

  const stats = [
    { label: 'Total Users', value: users.length, color: 'from-primary-500 to-accent-500' },
    { label: 'Total Predictions', value: predictions.length, color: 'from-accent-500 to-primary-500' },
    { label: 'High Risk Cases', value: predictions.filter(p => p.prediction_result === 1).length, color: 'from-danger-500 to-danger-400' },
    { label: 'Models Active', value: 3, color: 'from-success-500 to-success-400' },
  ];

  if (loading) return <LoadingSpinner className="py-20" />;

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-3xl font-bold text-white mb-2">Admin Dashboard</h1>
        <p className="text-slate-400">Manage users, models, and datasets</p>
      </motion.div>

      <div className="flex gap-2 p-1 rounded-xl bg-white/5 border border-white/5 w-fit">
        {tabs.map(t => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              tab === t.key ? 'bg-primary-500/20 text-primary-400 shadow-sm' : 'text-slate-400 hover:text-white'
            }`}
          >
            <span>{t.icon}</span>
            {t.label}
          </button>
        ))}
      </div>

      {message && (
        <div className="p-3 rounded-lg bg-success-500/10 border border-success-500/20 text-success-400 text-sm">{message}</div>
      )}
      {error && (
        <div className="p-3 rounded-lg bg-danger-500/10 border border-danger-500/20 text-danger-400 text-sm">{error}</div>
      )}

      {tab === 'overview' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {stats.map((s, i) => (
              <motion.div key={s.label} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}>
                <GlassCard>
                  <p className="text-3xl font-bold text-white">{s.value}</p>
                  <p className="text-xs text-slate-500 mt-1">{s.label}</p>
                </GlassCard>
              </motion.div>
            ))}
          </div>

          <GlassCard>
            <h2 className="text-lg font-semibold text-white mb-4">Recent Predictions</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-slate-500 border-b border-white/5">
                    <th className="pb-3 font-medium">User</th>
                    <th className="pb-3 font-medium">Disease</th>
                    <th className="pb-3 font-medium">Result</th>
                    <th className="pb-3 font-medium">Confidence</th>
                    <th className="pb-3 font-medium">Date</th>
                  </tr>
                </thead>
                <tbody>
                  {predictions.slice(0, 10).map(p => (
                    <tr key={p.id} className="border-b border-white/5">
                      <td className="py-3 text-white">{p.username || `User #${p.user_id}`}</td>
                      <td className="py-3 text-slate-300 capitalize">{p.disease_type}</td>
                      <td className="py-3"><RiskBadge level={p.prediction_result === 1 ? 'positive' : 'negative'} /></td>
                      <td className="py-3 text-slate-300">{(p.confidence * 100).toFixed(1)}%</td>
                      <td className="py-3 text-slate-500">{new Date(p.created_at).toLocaleDateString()}</td>
                    </tr>
                  ))}
                  {predictions.length === 0 && (
                    <tr><td colSpan={5} className="py-8 text-center text-slate-500">No predictions yet</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </GlassCard>
        </div>
      )}

      {tab === 'models' && (
        <div className="grid md:grid-cols-3 gap-4">
          {DISEASES.map(d => (
            <GlassCard key={d}>
              <div className="text-center">
                <div className="text-4xl mb-3">{d === 'diabetes' ? '🩸' : d === 'heart' ? '❤️' : '🧠'}</div>
                <h3 className="text-lg font-semibold text-white mb-1 capitalize">{DISEASE_LABELS[d]}</h3>
                <p className="text-xs text-slate-500 mb-4">ANN Model</p>
                <NeonButton
                  onClick={() => handleRetrain(d)}
                  loading={retraining === d}
                  className="w-full text-sm"
                >
                  Retrain Model
                </NeonButton>
              </div>
            </GlassCard>
          ))}
        </div>
      )}

      {tab === 'users' && (
        <GlassCard>
          <h2 className="text-lg font-semibold text-white mb-4">All Users ({users.length})</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-slate-500 border-b border-white/5">
                  <th className="pb-3 font-medium">ID</th>
                  <th className="pb-3 font-medium">Username</th>
                  <th className="pb-3 font-medium">Email</th>
                  <th className="pb-3 font-medium">Role</th>
                  <th className="pb-3 font-medium">Joined</th>
                </tr>
              </thead>
              <tbody>
                {users.map(u => (
                  <tr key={u.id} className="border-b border-white/5">
                    <td className="py-3 text-slate-400">#{u.id}</td>
                    <td className="py-3 text-white font-medium">{u.username}</td>
                    <td className="py-3 text-slate-300">{u.email}</td>
                    <td className="py-3">
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                        u.role === 'admin' ? 'bg-primary-500/15 text-primary-400' : 'bg-slate-500/15 text-slate-400'
                      }`}>
                        {u.role}
                      </span>
                    </td>
                    <td className="py-3 text-slate-500">{new Date(u.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </GlassCard>
      )}

      {tab === 'data' && (
        <div className="grid md:grid-cols-3 gap-4">
          {DISEASES.map(d => (
            <GlassCard key={d}>
              <div className="text-center">
                <div className="text-4xl mb-3">📁</div>
                <h3 className="text-lg font-semibold text-white mb-1 capitalize">{DISEASE_LABELS[d]}</h3>
                <p className="text-xs text-slate-500 mb-4">Upload new CSV dataset</p>
                <label className={`neon-btn-outline inline-block cursor-pointer text-sm w-full text-center ${uploading === d ? 'opacity-50' : ''}`}>
                  {uploading === d ? 'Uploading...' : 'Choose CSV'}
                  <input
                    type="file"
                    accept=".csv"
                    className="hidden"
                    disabled={uploading === d}
                    onChange={(e) => {
                      const file = e.target.files[0];
                      if (file) handleUpload(d, file);
                      e.target.value = '';
                    }}
                  />
                </label>
              </div>
            </GlassCard>
          ))}
        </div>
      )}
    </div>
  );
}
