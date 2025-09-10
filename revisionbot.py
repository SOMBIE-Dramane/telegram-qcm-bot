# revisionbot.py

import os
#import nest_asyncio
import asyncio
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
)

# Appliquer nest_asyncio pour permettre l'exécution imbriquée des boucles asyncio
#nest_asyncio.apply()

# Charger le token depuis les variables d'environnement (à configurer sur Render)
TOKEN = os.getenv("BOT_TOKEN")

# ========================
# Données des QCM
# ========================
QCM = {
    "Troisième": [
        {"question": "Quel est le rôle des testicules ?", "options": ["A. Produire du sperme", "B. Produire des spermatozoïdes", "C. Produire des ovules", "D. Produire du sang"], "reponse": "B. Produire des spermatozoïdes"},
        {"question": "Où a lieu la fécondation chez l’être humain ?", "options": ["A. Dans l’utérus", "B. Dans le vagin", "C. Dans l’ovaire", "D. Dans la trompe de Fallope"], "reponse": "D. Dans la trompe de Fallope"},
        {"question": "À la puberté, que se passe-t-il chez les garçons ?", "options": ["A. Apparition des règles", "B. Développement de la poitrine", "C. Mue de la voix et apparition de poils", "D. Arrêt de la croissance"], "reponse": "C. Mue de la voix et apparition de poils"},
        {"question": "L’ADN se trouve principalement :", "options": ["A. Dans la membrane de la cellule", "B. Dans le noyau de la cellule", "C. Dans le cytoplasme", "D. Dans le sang"], "reponse": "B. Dans le noyau de la cellule"},
        {"question": "Combien de chromosomes possède une cellule humaine ?", "options": ["A. 23", "B. 46", "C. 22", "D. 92"], "reponse": "B. 46"},
        {"question": "Quel est le rôle de l’intestin grêle ?", "options": ["A. Produire des enzymes", "B. Digérer les protéines uniquement", "C. Absorber les nutriments", "D. Stocker les aliments"], "reponse": "C. Absorber les nutriments"},
        {"question": "Qui a proposé la théorie de la sélection naturelle ?", "options": ["A. Newton", "B. Darwin", "C. Pasteur", "D. Mendel"], "reponse": "B. Darwin"},
        {"question": "Un antibiotique agit uniquement contre :", "options": ["A. Les virus", "B. Les bactéries", "C. Les parasites", "D. Les champignons"], "reponse": "B. Les bactéries"},
        {"question": "Le centre de commande des mouvements volontaires est :", "options": ["A. Le cœur", "B. La moelle épinière", "C. Le cerveau", "D. Le foie"], "reponse": "C. Le cerveau"},
        {"question": "Quelle partie de la plante produit les graines ?", "options": ["A. Les racines", "B. Les feuilles", "C. Les fleurs", "D. Les tiges"], "reponse": "C. Les fleurs"}
    ],
    "Terminale": [
        {"question": "Quelle est l’unité de la résistance électrique ?", "options": ["A. Watt", "B. Volt", "C. Ohm", "D. Ampère"], "reponse": "C. Ohm"},
        {"question": "La loi d’Ohm s’écrit :", "options": ["A. U = I / R", "B. R = U / I", "C. I = R × U", "D. P = U / I"], "reponse": "B. R = U / I"},
        {"question": "La première loi de Newton concerne :", "options": ["A. L’accélération", "B. L’inertie", "C. La gravitation", "D. L’énergie cinétique"], "reponse": "B. L’inertie"},
        {"question": "La force gravitationnelle entre deux corps est :", "options": ["A. Proportionnelle au carré de leur distance", "B. Indépendante de la masse", "C. Inversement proportionnelle au carré de la distance", "D. Égale à leur produit vectoriel"], "reponse": "C. Inversement proportionnelle au carré de la distance"},
        {"question": "L’image donnée par un miroir plan est :", "options": ["A. Réelle et inversée", "B. Virtuelle et renversée", "C. Virtuelle et droite", "D. Réelle et droite"], "reponse": "C. Virtuelle et droite"},
        {"question": "La température est proportionnelle à :", "options": ["A. L’énergie chimique", "B. L’agitation des particules", "C. La densité", "D. La tension"], "reponse": "B. L’agitation des particules"},
        {"question": "Un atome est électriquement neutre car :", "options": ["A. Il possède autant d’électrons que de neutrons", "B. Il possède autant de protons que d’électrons", "C. Il n’a pas de charges", "D. Ses électrons tournent très vite"], "reponse": "B. Il possède autant de protons que d’électrons"},
        {"question": "Une réaction chimique respecte toujours :", "options": ["A. La conservation des volumes", "B. La conservation des masses", "C. La conservation de l’énergie cinétique", "D. La conservation de la pression"], "reponse": "B. La conservation des masses"}
    ]
}

eleves = {}

# ========================
# Fonctions de gestion
# ========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    boutons = [
        [InlineKeyboardButton("Troisième", callback_data="niveau:Troisième")],
        [InlineKeyboardButton("Terminale", callback_data="niveau:Terminale")]
    ]
    clavier = InlineKeyboardMarkup(boutons)
    await update.message.reply_text("Bienvenue ! Choisis ton niveau :", reply_markup=clavier)

async def choisir_niveau(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    niveau = query.data.split(":")[1]
    chat_id = query.message.chat_id
    eleves[chat_id] = {"niveau": niveau, "index": 0, "score": 0, "etat": "quiz"}
    await envoyer_question(update, context)

async def envoyer_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    data = eleves[chat_id]
    niveau = data["niveau"]
    index = data["index"]

    if index >= len(QCM[niveau]):
        score = data["score"]
        total = len(QCM[niveau])
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"🎉 Bravo ! Tu as terminé tous les QCM.\n📊 *Ta note : {score} / {total}*",
            parse_mode="Markdown"
        )
        data["etat"] = "fini"
        return

    question = QCM[niveau][index]
    boutons = [[InlineKeyboardButton(opt, callback_data=opt)] for opt in question["options"]]
    clavier = InlineKeyboardMarkup(boutons)
    await context.bot.send_message(chat_id=chat_id, text=f"❓ {question['question']}", reply_markup=clavier)

async def verifier_reponse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id
    reponse = query.data
    data = eleves.get(chat_id)

    if not data or data.get("etat") != "quiz":
        await context.bot.send_message(chat_id=chat_id, text="Merci d’utiliser /start pour commencer.")
        return

    niveau = data["niveau"]
    index = data["index"]
    question_data = QCM[niveau][index]
    bonne_reponse = question_data["reponse"]

    await query.edit_message_reply_markup(reply_markup=None)

    if reponse == bonne_reponse:
        msg = f"✅ *Bravo !* {reponse} est la bonne réponse ! *(+1 point)*"
        data["score"] += 1
    else:
        msg = f"❌ *Désolé*, ce n'est pas la bonne réponse.\nLa bonne réponse était *{bonne_reponse}*."

    await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode="Markdown")

    data["index"] += 1
    await envoyer_question(update, context)

# ========================
# Lancement du bot
# ========================
def main():
    print("🤖 Bot en cours d'exécution...")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(choisir_niveau, pattern="^niveau:"))
    app.add_handler(CallbackQueryHandler(verifier_reponse))

    app.run_polling()

if __name__ == "__main__":
    main()
   # asyncio.run(main())
