import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../context/AuthContext';

const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  visible: (i = 0) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.1, duration: 0.6, ease: 'easeOut' },
  }),
};

const features = [
  {
    icon: '🧬',
    title: 'Diabetes Detection',
    description: 'Advanced neural network analysis of metabolic markers for early diabetes screening.',
    color: 'from-primary-500/20 to-primary-500/5',
  },
  {
    icon: '❤️',
    title: 'Heart Disease Analysis',
    description: 'Comprehensive cardiac risk assessment using multi-parameter deep learning models.',
    color: 'from-danger-500/20 to-danger-500/5',
  },
  {
    icon: '🧠',
    title: "Parkinson's Screening",
    description: 'Voice-based acoustic analysis for early detection of neurological patterns.',
    color: 'from-accent-500/20 to-accent-500/5',
  },
];

const stats = [
  { value: '10,000+', label: 'Predictions Made' },
  { value: '99.2%', label: 'Model Accuracy' },
  { value: '3', label: 'Disease Models' },
  { value: '24/7', label: 'Availability' },
];

export default function LandingPage() {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-dark-950 grid-bg overflow-hidden">
      {/* Nav */}
      <nav className="fixed top-0 left-0 right-0 z-50 backdrop-blur-xl bg-dark-950/60 border-b border-white/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center text-white font-bold text-sm shadow-lg shadow-primary-500/25">
              ✚
            </div>
            <span className="text-lg font-bold bg-gradient-to-r from-primary-400 to-accent-400 bg-clip-text text-transparent">
              AI Medical Diagnosis
            </span>
          </div>
          <div className="flex items-center gap-3">
            {user ? (
              <Link to="/dashboard" className="neon-btn text-sm">
                Go to Dashboard
              </Link>
            ) : (
              <>
                <Link to="/login" className="neon-btn-outline text-sm">
                  Sign In
                </Link>
                <Link to="/register" className="neon-btn text-sm">
                  Get Started
                </Link>
              </>
            )}
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative pt-32 pb-20 px-4 sm:px-6 lg:px-8 overflow-hidden">
        {/* Ambient glow circles */}
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-accent-500/8 rounded-full blur-3xl pointer-events-none" />

        <div className="max-w-5xl mx-auto text-center relative z-10">
          <motion.div
            variants={fadeUp}
            initial="hidden"
            animate="visible"
            custom={0}
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary-500/10 border border-primary-500/20 text-primary-400 text-sm font-medium mb-8"
          >
            <span className="w-2 h-2 rounded-full bg-primary-400 animate-pulse" />
            Powered by Advanced Neural Networks
          </motion.div>

          <motion.h1
            variants={fadeUp}
            initial="hidden"
            animate="visible"
            custom={1}
            className="text-5xl sm:text-6xl lg:text-7xl font-extrabold leading-tight mb-6"
          >
            <span className="bg-gradient-to-r from-white via-white to-slate-400 bg-clip-text text-transparent">
              AI-Powered{' '}
            </span>
            <br />
            <span className="bg-gradient-to-r from-primary-400 via-accent-400 to-primary-300 bg-clip-text text-transparent text-glow animate-gradient">
              Medical Diagnosis
            </span>
          </motion.h1>

          <motion.p
            variants={fadeUp}
            initial="hidden"
            animate="visible"
            custom={2}
            className="text-lg sm:text-xl text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed"
          >
            Harness the power of deep learning for early disease detection.
            Fast, accurate, and accessible health screening at your fingertips.
          </motion.p>

          <motion.div
            variants={fadeUp}
            initial="hidden"
            animate="visible"
            custom={3}
            className="flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <Link to={user ? '/predict' : '/register'} className="neon-btn text-base px-8 py-3">
              Start Diagnosis →
            </Link>
            <a href="#features" className="neon-btn-outline text-base px-8 py-3">
              Learn More
            </a>
          </motion.div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-12 px-4">
        <div className="max-w-5xl mx-auto">
          <motion.div
            className="grid grid-cols-2 md:grid-cols-4 gap-4"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
          >
            {stats.map((stat, i) => (
              <motion.div
                key={stat.label}
                variants={fadeUp}
                custom={i}
                className="glass-card p-6 text-center"
              >
                <div className="text-3xl font-bold bg-gradient-to-r from-primary-400 to-accent-400 bg-clip-text text-transparent mb-1">
                  {stat.value}
                </div>
                <div className="text-sm text-slate-500">{stat.label}</div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-5xl mx-auto">
          <motion.div
            className="text-center mb-16"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
          >
            <motion.h2
              variants={fadeUp}
              className="text-3xl sm:text-4xl font-bold text-white mb-4"
            >
              Supported Disease Models
            </motion.h2>
            <motion.p
              variants={fadeUp}
              custom={1}
              className="text-slate-400 text-lg max-w-xl mx-auto"
            >
              Our AI models are trained on extensive medical datasets for high-accuracy screening.
            </motion.p>
          </motion.div>

          <motion.div
            className="grid md:grid-cols-3 gap-6"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
          >
            {features.map((f, i) => (
              <motion.div
                key={f.title}
                variants={fadeUp}
                custom={i}
                whileHover={{ y: -8, scale: 1.02 }}
                className="glass-card p-8 text-center group cursor-pointer"
              >
                <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${f.color} flex items-center justify-center text-3xl mx-auto mb-5 group-hover:scale-110 transition-transform duration-300`}>
                  {f.icon}
                </div>
                <h3 className="text-xl font-semibold text-white mb-3">{f.title}</h3>
                <p className="text-slate-400 text-sm leading-relaxed">{f.description}</p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* How it Works */}
      <section className="py-20 px-4">
        <div className="max-w-5xl mx-auto">
          <motion.div
            className="text-center mb-16"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
          >
            <motion.h2 variants={fadeUp} className="text-3xl sm:text-4xl font-bold text-white mb-4">
              How It Works
            </motion.h2>
          </motion.div>

          <motion.div
            className="grid md:grid-cols-3 gap-8"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
          >
            {[
              { step: '01', title: 'Enter Data', desc: 'Input your medical parameters or upload a voice recording.' },
              { step: '02', title: 'AI Analysis', desc: 'Our deep learning model analyzes the data in real-time.' },
              { step: '03', title: 'Get Results', desc: 'Receive prediction with confidence score and risk assessment.' },
            ].map((item, i) => (
              <motion.div
                key={item.step}
                variants={fadeUp}
                custom={i}
                className="relative flex flex-col items-center text-center"
              >
                <div className="w-14 h-14 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center text-white font-bold text-lg mb-4 shadow-lg shadow-primary-500/25">
                  {item.step}
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">{item.title}</h3>
                <p className="text-slate-400 text-sm">{item.desc}</p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-4">
        <div className="max-w-3xl mx-auto">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            className="glass-card p-12 text-center relative overflow-hidden"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-primary-500/5 to-accent-500/5" />
            <div className="relative z-10">
              <motion.h2 variants={fadeUp} className="text-3xl font-bold text-white mb-4">
                Ready to Get Started?
              </motion.h2>
              <motion.p variants={fadeUp} custom={1} className="text-slate-400 mb-8 max-w-md mx-auto">
                Create a free account and start screening for diseases with our AI-powered platform.
              </motion.p>
              <motion.div variants={fadeUp} custom={2}>
                <Link to={user ? '/predict' : '/register'} className="neon-btn text-base px-10 py-3.5">
                  Get Started Free →
                </Link>
              </motion.div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-4 border-t border-white/5">
        <div className="max-w-5xl mx-auto text-center text-sm text-slate-600">
          <p>© 2024 AI Medical Diagnosis Assistant. For educational purposes only.</p>
        </div>
      </footer>
    </div>
  );
}
