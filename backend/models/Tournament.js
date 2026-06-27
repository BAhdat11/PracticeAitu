const mongoose = require('mongoose');

const tournamentSchema = new mongoose.Schema({
  name: { type: String, required: true, trim: true },
  game: {
    type: String,
    enum: ['CS2', 'Dota 2', 'Valorant', 'Mobile Legends', 'FIFA'],
    required: true,
  },
  date:        { type: String, required: true },
  prizePool:   { type: String, default: 'TBD' },
  maxTeams:    { type: Number, default: 16 },
  status:      { type: String, enum: ['open', 'closed', 'finished'], default: 'open' },
}, { timestamps: true });

module.exports = mongoose.model('Tournament', tournamentSchema);
