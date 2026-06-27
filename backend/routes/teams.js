const router = require('express').Router();
const Team   = require('../models/Team');

// GET all teams (optionally filter by tournament)
router.get('/', async (req, res) => {
  try {
    const filter = req.query.tournament ? { tournament: req.query.tournament } : {};
    const teams  = await Team.find(filter).populate('tournament', 'name game date').sort({ createdAt: -1 });
    res.json(teams);
  } catch (e) { res.status(500).json({ error: e.message }); }
});

// POST register team
router.post('/', async (req, res) => {
  try {
    const team = await new Team(req.body).save();
    const populated = await team.populate('tournament', 'name game date');
    res.status(201).json(populated);
  } catch (e) { res.status(400).json({ error: e.message }); }
});

// DELETE team
router.delete('/:id', async (req, res) => {
  try {
    await Team.findByIdAndDelete(req.params.id);
    res.json({ message: 'Team removed' });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

module.exports = router;
