const mongoose = require('mongoose');

const teamSchema = new mongoose.Schema({
  teamName:    { type: String, required: true, trim: true },
  captainName: { type: String, required: true, trim: true },
  contact:     { type: String, required: true, trim: true }, // telegram @username or phone
  game:        {
    type: String,
    enum: ['CS2', 'Dota 2', 'Valorant', 'Mobile Legends', 'FIFA'],
    required: true,
  },
  players:     { type: Number, min: 1, max: 10, default: 5 },
  tournament:  { type: mongoose.Schema.Types.ObjectId, ref: 'Tournament', required: true },
  source:      { type: String, enum: ['web', 'telegram'], default: 'web' },
}, { timestamps: true });

module.exports = mongoose.model('Team', teamSchema);
