const router = require('express').Router();
const jwt    = require('jsonwebtoken');
const User   = require('../models/User');

const SECRET = process.env.JWT_SECRET || 'esports_kz_secret_2026';

// Middleware — verify token
function auth(req, res, next) {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'No token' });
  try {
    req.user = jwt.verify(token, SECRET);
    next();
  } catch { res.status(401).json({ error: 'Invalid token' }); }
}

// Middleware — admin only
function adminOnly(req, res, next) {
  if (req.user?.role !== 'admin') return res.status(403).json({ error: 'Admins only' });
  next();
}

// POST /api/auth/register
router.post('/register', async (req, res) => {
  try {
    const { username, email, password } = req.body;
    if (!username || !email || !password)
      return res.status(400).json({ error: 'All fields required' });
    if (password.length < 6)
      return res.status(400).json({ error: 'Password must be at least 6 characters' });

    const exists = await User.findOne({ $or: [{ email }, { username }] });
    if (exists) return res.status(400).json({ error: 'Username or email already taken' });

    const user  = await new User({ username, email, password }).save();
    const token = jwt.sign({ id: user._id, username: user.username, role: user.role }, SECRET, { expiresIn: '7d' });
    res.status(201).json({ token, user: { id: user._id, username: user.username, role: user.role } });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

// POST /api/auth/login
router.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    const user = await User.findOne({ email });
    if (!user || !(await user.comparePassword(password)))
      return res.status(401).json({ error: 'Invalid email or password' });

    const token = jwt.sign({ id: user._id, username: user.username, role: user.role }, SECRET, { expiresIn: '7d' });
    res.json({ token, user: { id: user._id, username: user.username, role: user.role } });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

// GET /api/auth/me — get current user
router.get('/me', auth, async (req, res) => {
  const user = await User.findById(req.user.id).select('-password');
  res.json(user);
});

module.exports = { router, auth, adminOnly };
