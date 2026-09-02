import logging
import os
import sqlite3
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8594676233:AAF_Jl38ATSLUouYpN0ZLKAy9W77kbBi5nw"

# ዳታቤዝ በቀላሉ በአንድ ላይ ማዘጋጃ
DATA_DIR = "/var/data" if os.path.exists("/var/data") else "."
DB_NAME = os.path.join(DATA_DIR, "bot_database.db")

def init_db():
    conn = sqlite3.connect(DB_NAME, timeout=30.0)
    cursor = conn.cursor()
    cursor.execute('PRAGMA journal_mode=WAL;')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name TEXT DEFAULT 'አልተመዘገበም'
        )
    ''')
    conn.commit()
    conn.close()

# Render ሰርቨር እንዳይዘጋ የሚያደርግ ክፍል
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ተጠቃሚው /start ሲሉ የሚሰራው
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # ተጠቃሚውን ዳታቤዝ ውስጥ መመዝገብ
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()
    
    keyboard = [[InlineKeyboardButton("📝 ምዝገባ (Register)", callback_data='register')]]
    text = "እንኳን ደህና መጡ! አዲሱ ቦት በንጹህ ሁኔታ ተጀምሯል።"
    
    if update.message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

if __name__ == '__main__':
    # ሰርቨሩን ማስጀመር
    threading.Thread(target=run_health_server, daemon=True).start()
    init_db()

    # ቦቱን ማስጀመር
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    print("🚀 ንጹሁ ቦት በስራ ላይ ውሏል...")
    app.run_polling(drop_pending_updates=True)
