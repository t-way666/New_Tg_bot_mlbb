from handlers import start, help, winrate_correction, season_progress, rank, my_stars

def handle_commands(bot, message):
    if message.text == '/start':
        start.send_start(bot)(message)
    elif message.text == '/help':
        help.send_help(bot)(message)
    elif message.text == '/winrate_correction':
        winrate_correction.send_winrate_correction(bot)(message)
    elif message.text == '/season_progress':
        season_progress.send_season_progress(bot)(message)
    elif message.text == '/rank':
        rank.send_rank(bot)(message)
    elif message.text == '/my_stars':
        my_stars.send_my_stars(bot)(message)