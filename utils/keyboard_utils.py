from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def create_content_list_keyboard(results, page, total_pages, command_type):
    buttons = []
    for item in results:
        title = item.get("title") or item.get("name")
        release_date = item.get("release_date") or item.get(
            "first_air_date", "")
        year = release_date[:4] if release_date else "N/A"

        if "first_air_date" in item:
            media_type = "tv"
        elif "release_date" in item:
            media_type = "movie"
        else:
            media_type = item.get("media_type", "movie")

        text = f"{title} ({year})"
        callback_data = f"title_{item['id']}_{media_type}"
        buttons.append([InlineKeyboardButton(
            text, callback_data=callback_data)])

    nav_buttons = []
    if page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                "⬅️ Previous",
                callback_data=f"{command_type}_page_{page-1}"
            )
        )
    if page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(
                "Next ➡️",
                callback_data=f"{command_type}_page_{page+1}"
            )
        )

    if nav_buttons:
        buttons.append(nav_buttons)

    buttons.append([InlineKeyboardButton(
        "❌ Cancel", callback_data="cancel_search")])
    return InlineKeyboardMarkup(buttons)

