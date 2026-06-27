const router     = require('express').Router();
const Tournament = require('../models/Tournament');
const Team       = require('../models/Team');

// GET all tournaments
router.get('/', async (_req, res) => {
  try {
    const list = await Tournament.find().sort({ createdAt: -1 });
    res.json(list);
  } catch (e) { res.status(500).json({ error: e.message }); }
});

// GET single tournament with registered teams count
router.get('/:id', async (req, res) => {
  try {
    const t     = await Tournament.findById(req.params.id);
    if (!t) return res.status(404).json({ error: 'Not found' });
    const count = await Team.countDocuments({ tournament: req.params.id });
    res.json({ ...t.toObject(), registeredTeams: count });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

// POST create tournament
router.post('/', async (req, res) => {
  try {
    const t = await new Tournament(req.body).save();
    res.status(201).json(t);
  } catch (e) { res.status(400).json({ error: e.message }); }
});

// DELETE tournament
router.delete('/:id', async (req, res) => {
  try {
    await Tournament.findByIdAndDelete(req.params.id);
    await Team.deleteMany({ tournament: req.params.id });
    res.json({ message: 'Deleted' });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

// GET stats
router.get('/stats/summary', async (_req, res) => {
  try {
    const tournaments = await Tournament.countDocuments();
    const open        = await Tournament.countDocuments({ status: 'open' });
    const teams       = await Team.countDocuments();
    const byGame      = await Team.aggregate([
      { $group: { _id: '$game', count: { $sum: 1 } } }
    ]);
    res.json({ tournaments, open, teams, byGame });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

module.exports = router;
