"""
Esports Federation of Kazakhstan — Tournament Registration Bot
Connects to the same MongoDB as the web application.
Author: Bagdat Ayagan, SE-2407
"""

import os
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ConversationHandler, ContextTypes, filters,
)

load_dotenv()
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

# ── MongoDB ───────────────────────────────────
client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/test"))
db = client.get_database()

def get_open_tournaments():
    return list(db.tournaments.find({"status": "open"}))

def get_tournament_by_name(name):
    return db.tournaments.find_one({"name": name, "status": "open"})

def register_team(team_name, captain, contact, game, tournament_id):
    doc = {
        "teamName":    team_name,
        "captainName": captain,
        "contact":     contact,
        "game":        game,
        "players":     5,
        "tournament":  ObjectId(tournament_id),
        "source":      "telegram",
        "createdAt":   datetime.utcnow(),
        "updatedAt":   datetime.utcnow(),
    }
    db.teams.insert_one(doc)

def count_teams(tournament_id):
    return db.teams.count_documents({"tournament": ObjectId(tournament_id)})

# ── States ────────────────────────────────────
CHOOSE_TOURNAMENT, TEAM_NAME, CAPTAIN, CONFIRM = range(4)

# ── Main menu ─────────────────────────────────
def main_menu():
    kb = [
        ["🏆 Register Team", "📋 View Tournaments"],
        ["📊 My Registrations", "ℹ️ About"],
    ]
    return ReplyKeyboardMarkup(kb, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎮 *Esports Federation of Kazakhstan*\n\n"
        "Welcome! This bot allows you to register your team\n"
        "for official esports tournaments.\n\n"
        "Choose an option:",
        parse_mode="Markdown",
        reply_markup=main_menu(),
    )

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏅 *Esports Federation of Kazakhstan*\n\n"
        "Official body organizing esports competitions in Kazakhstan.\n"
        "📍 Astana, Kazakhstan\n"
        "🌐 Games: CS2 · Dota 2 · Valorant · Mobile Legends · FIFA\n\n"
        "_Built during industrial practice by Bagdat Ayagan, SE-2407, AITU_",
        parse_mode="Markdown",
    )

async def view_tournaments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tournaments = get_open_tournaments()
    if not tournaments:
        await update.message.reply_text("❌ No open tournaments at the moment.")
        return
    lines = ["🏆 *Open Tournaments*\n"]
    for t in tournaments:
        count = count_teams(str(t["_id"]))
        lines.append(
            f"*{t['name']}*\n"
            f"  🎮 {t['game']}  📅 {t['date']}\n"
            f"  💰 {t.get('prizePool','TBD')}  👥 {count}/{t.get('maxTeams',16)} teams\n"
        )
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

async def my_registrations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = f"@{update.effective_user.username}" if update.effective_user.username else None
    if not contact:
        await update.message.reply_text("Set a Telegram username to track your registrations.")
        return
    teams = list(db.teams.find({"contact": contact}))
    if not teams:
        await update.message.reply_text("You have no registered teams yet.")
        return
    lines = [f"📋 *Your Teams* ({len(teams)})\n"]
    for t in teams:
        tour = db.tournaments.find_one({"_id": t["tournament"]})
        tour_name = tour["name"] if tour else "Unknown"
        lines.append(f"• *{t['teamName']}* → {tour_name} ({t['game']})")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

async def register_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tournaments = get_open_tournaments()
    if not tournaments:
        await update.message.reply_text("❌ No open tournaments right now.")
        return ConversationHandler.END
    context.user_data["tournaments"] = {t["name"]: str(t["_id"]) for t in tournaments}
    kb = [[name] for name in context.user_data["tournaments"]]
    await update.message.reply_text(
        "📋 *Step 1/3* — Choose a tournament:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True, one_time_keyboard=True),
    )
    return CHOOSE_TOURNAMENT

async def choose_tournament(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    if name not in context.user_data["tournaments"]:
        await update.message.reply_text("❌ Please select from the list.")
        return CHOOSE_TOURNAMENT
    context.user_data["tournament_name"] = name
    context.user_data["tournament_id"]   = context.user_data["tournaments"][name]
    await update.message.reply_text(
        f"✅ Tournament: *{name}*\n\n*Step 2/3* — Enter your *team name*:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )
    return TEAM_NAME

async def get_team_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["team_name"] = update.message.text.strip()
    await update.message.reply_text(
        f"✅ Team: *{context.user_data['team_name']}*\n\n*Step 3/3* — Enter *captain's full name*:",
        parse_mode="Markdown",
    )
    return CAPTAIN

async def get_captain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["captain"] = update.message.text.strip()
    t = db.tournaments.find_one({"_id": ObjectId(context.user_data["tournament_id"])})
    game = t["game"] if t else "Unknown"
    context.user_data["game"] = game
    username = f"@{update.effective_user.username}" if update.effective_user.username else "N/A"
    context.user_data["contact"] = username
    summary = (
        f"📋 *Registration Summary*\n\n"
        f"🏆 Tournament: {context.user_data['tournament_name']}\n"
        f"👥 Team: {context.user_data['team_name']}\n"
        f"🎖️ Captain: {context.user_data['captain']}\n"
        f"🎮 Game: {game}\n"
        f"📱 Contact: {username}\n\n"
        f"Confirm registration?"
    )
    kb = [["✅ Confirm", "❌ Cancel"]]
    await update.message.reply_text(
        summary, parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True, one_time_keyboard=True),
    )
    return CONFIRM

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "✅ Confirm":
        register_team(
            team_name     = context.user_data["team_name"],
            captain       = context.user_data["captain"],
            contact       = context.user_data["contact"],
            game          = context.user_data["game"],
            tournament_id = context.user_data["tournament_id"],
        )
        await update.message.reply_text(
            f"🎉 *Registration Successful!*\n\n"
            f"Team *{context.user_data['team_name']}* is registered for "
            f"*{context.user_data['tournament_name']}*!\n\n"
            f"Good luck! 🏆",
            parse_mode="Markdown",
            reply_markup=main_menu(),
        )
    else:
        await update.message.reply_text("❌ Cancelled.", reply_markup=main_menu())
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Cancelled.", reply_markup=main_menu())
    return ConversationHandler.END

# ── Main ──────────────────────────────────────
async def main():
    token = os.getenv("BOT_TOKEN")
    if not token or token == "YOUR_BOT_TOKEN_HERE":
        print("❌ Set BOT_TOKEN in bot/.env")
        return

    app = Application.builder().token(token).build()

    conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🏆 Register Team$"), register_start)],
        states={
            CHOOSE_TOURNAMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_tournament)],
            TEAM_NAME:         [MessageHandler(filters.TEXT & ~filters.COMMAND, get_team_name)],
            CAPTAIN:           [MessageHandler(filters.TEXT & ~filters.COMMAND, get_captain)],
            CONFIRM:           [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv)
    app.add_handler(MessageHandler(filters.Regex("^📋 View Tournaments$"), view_tournaments))
    app.add_handler(MessageHandler(filters.Regex("^📊 My Registrations$"), my_registrations))
    app.add_handler(MessageHandler(filters.Regex("^ℹ️ About$"), about))

    print("🤖 Bot running...")
    async with app:
        await app.start()
        await app.updater.start_polling()
        await asyncio.Event().wait()
        await app.updater.stop()
        await app.stop()

if __name__ == "__main__":
    asyncio.run(main())