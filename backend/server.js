const express  = require('express');
const mongoose = require('mongoose');
const cors     = require('cors');
const path     = require('path');
require('dotenv').config();

const teamRoutes       = require('./routes/teams');
const tournamentRoutes = require('./routes/tournaments');
const { router: authRoutes } = require('./routes/auth');

const app = express();

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '../frontend')));

// Routes
app.use('/api/auth',        authRoutes);
app.use('/api/teams',       teamRoutes);
app.use('/api/tournaments', tournamentRoutes);

app.get('/api/health', (_req, res) => {
  res.json({ status: 'OK', service: 'Esports Tournament API', time: new Date() });
});

// Connect & start
const PORT      = process.env.PORT      || 3000;
const MONGO_URI = process.env.MONGO_URI || 'mongodb://localhost:27017/esports';

mongoose
  .connect(MONGO_URI)
  .then(() => {
    console.log('✅ MongoDB connected');
    app.listen(PORT, () => console.log(`🚀 Server → http://localhost:${PORT}`));
  })
  .catch(err => { console.error('❌ DB error:', err.message); process.exit(1); });
