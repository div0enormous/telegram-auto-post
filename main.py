from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ParseMode
import logging
import requests
from urllib.parse import quote
import json
from config import API_ID, API_HASH, BOT_TOKEN, SHORTENER_API, ADMINS
from database import Database

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize database
db = Database()

# User data storage (temporary)
user_data = {}

# Initialize bot
app = Client(
    "multi_channel_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ============== HELPER FUNCTIONS ==============

def shorten_url(long_url):
    """Shorten URL using ShrinkEarn API"""
    try:
        encoded_url = quote(long_url)
        api_url = f"https://shrinkearn.com/api?api={SHORTENER_API}&url={encoded_url}&format=text"
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200 and response.text.strip():
            return response.text.strip()
        return long_url
    except Exception as e:
        logger.error(f"URL shortening failed: {e}")
        return long_url

def is_admin(user_id):
    """Check if user is admin"""
    return user_id in ADMINS

async def send_post_to_user(client, user_id, post_id):
    """Sends a specific post to a user."""
    post = db.get_post(post_id)
    if not post:
        await client.send_message(user_id, "❌ Post not found.")
        return

    content, media_type, media_file_id, buttons_json = post
    buttons = json.loads(buttons_json) if buttons_json else []
    
    keyboard = []
    for btn in buttons:
        keyboard.append([InlineKeyboardButton(btn['text'], url=btn['url'])])
    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None

    try:
        if media_type == 'photo':
            await client.send_photo(
                chat_id=user_id,
                photo=media_file_id,
                caption=content,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        elif media_type == 'video':
            await client.send_video(
                chat_id=user_id,
                video=media_file_id,
                caption=content,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        else:
            await client.send_message(
                chat_id=user_id,
                text=content,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
    except Exception as e:
        logger.error(f"Failed to send post {post_id} to user {user_id}: {e}")
        await client.send_message(user_id, f"❌ An error occurred while fetching the post: {e}")


# ============== START & HELP COMMANDS ==============

@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message: Message):
    user_id = message.from_user.id
    
    # Deep linking for posts
    if len(message.command) > 1:
        post_id = message.command[1].replace('post_', '')
        await send_post_to_user(client, user_id, post_id)
        return

    if is_admin(user_id):
        welcome_text = """
🤖 **Welcome Admin!**

This is your control panel for the Multi-Channel Post Bot.

**Available Commands:**
/newpost - Create a new post
/editpost - Edit an existing post
/listposts - View all saved posts
/deletepost - Delete a post
/repost - Repost from saved posts

/addchannel - Add a channel/group
/listchannels - View all channels
/removechannel - Remove a channel

/help - Show this message
        """
    else:
        welcome_text = """
👋 **Welcome to the Bot!**

You can use me to search for posts.

**Available Commands:**
/search - Search for a post by name
/help - Show this message
        """
    await message.reply_text(welcome_text)

@app.on_message(filters.command("help") & filters.private)
async def help_command(client, message: Message):
    # This is an alias for the start command without arguments
    await start_command(client, message)


# ============== USER COMMANDS ==============

@app.on_message(filters.command("search") & filters.private)
async def search_command(client, message: Message):
    user_id = message.from_user.id
    user_data[user_id] = {'awaiting': 'search_query'}
    await message.reply_text("🔎 **What are you looking for?**\n\Send me the name to search for.")


# ============== ADMIN: CHANNEL MANAGEMENT ==============

@app.on_message(filters.command("addchannel") & filters.private)
async def add_channel_command(client, message: Message):
    if not is_admin(message.from_user.id):
        await message.reply_text("⛔ You are not authorized for this command.")
        return
    
    await message.reply_text(
        "📢 **Forward a message from the channel/group** or send the channel ID (e.g., -1001234567890)"
    )
    user_data[message.from_user.id] = {'awaiting': 'channel_id'}


@app.on_message(filters.command("listchannels") & filters.private)
async def list_channels_command(client, message: Message):
    if not is_admin(message.from_user.id): return
    channels = db.get_all_channels()
    if not channels:
        await message.reply_text("📭 No channels added yet.")
        return
    text = "📢 **Your Channels:**\n\n"
    for channel_id, channel_name in channels:
        text += f"• {channel_name} (`{channel_id}`)\n"
    await message.reply_text(text)


@app.on_message(filters.command("removechannel") & filters.private)
async def remove_channel_command(client, message: Message):
    if not is_admin(message.from_user.id): return
    channels = db.get_all_channels()
    if not channels:
        await message.reply_text("📭 No channels to remove.")
        return
    buttons = []
    for channel_id, channel_name in channels:
        buttons.append([InlineKeyboardButton(f"❌ {channel_name}", callback_data=f"remove_ch_{channel_id}")])
    await message.reply_text("Select a channel to remove:", reply_markup=InlineKeyboardMarkup(buttons))


# ============== ADMIN: POST MANAGEMENT ==============

@app.on_message(filters.command("newpost") & filters.private)
async def new_post_command(client, message: Message):
    if not is_admin(message.from_user.id): return
    await message.reply_text(
        "📝 **Creating New Post**\n\n"
        "Send me your post content with optional media (photo/video). "
        "You can use **Markdown** for formatting.\n\n"
        "After that, send buttons in this format:\n"
        "`Button Text | URL`\n"
        "One button per line.\n\n"
        "Send /done when finished."
    )
    user_data[message.from_user.id] = {'state': 'creating_post', 'post_data': {}}


@app.on_message(filters.command("listposts") & filters.private)
async def list_posts_command(client, message: Message):
    if not is_admin(message.from_user.id): return
    posts = db.get_all_posts()
    if not posts:
        await message.reply_text("📭 No posts saved yet.")
        return
    text = "📝 **Your Saved Posts:**\n\n"
    for post_id, title, created_at in posts:
        text += f"• **Post #{post_id}**: {title}\n  *Created*: {created_at}\n\n"
    await message.reply_text(text)


@app.on_message(filters.command("deletepost") & filters.private)
async def delete_post_command(client, message: Message):
    if not is_admin(message.from_user.id): return
    posts = db.get_all_posts()
    if not posts:
        await message.reply_text("📭 No posts to delete.")
        return
    buttons = [[InlineKeyboardButton(f"🗑 {title}", callback_data=f"delete_post_{post_id}")] for post_id, title, _ in posts]
    await message.reply_text("Select a post to delete:", reply_markup=InlineKeyboardMarkup(buttons))


@app.on_message(filters.command("repost") & filters.private)
async def repost_command(client, message: Message):
    if not is_admin(message.from_user.id): return
    posts = db.get_all_posts()
    if not posts:
        await message.reply_text("📭 No posts to repost.")
        return
    buttons = [[InlineKeyboardButton(f"📤 {title}", callback_data=f"repost_{post_id}")] for post_id, title, _ in posts]
    await message.reply_text("Select a post to repost:", reply_markup=InlineKeyboardMarkup(buttons))


@app.on_message(filters.command("editpost") & filters.private)
async def edit_post_command(client, message: Message):
    if not is_admin(message.from_user.id): return
    posts = db.get_all_posts()
    if not posts:
        await message.reply_text("📭 No posts to edit.")
        return
    buttons = [[InlineKeyboardButton(f"✏️ {title}", callback_data=f"edit_post_{post_id}")] for post_id, title, _ in posts]
    await message.reply_text("Select a post to edit:", reply_markup=InlineKeyboardMarkup(buttons))


@app.on_message(filters.command("done") & filters.private)
async def done_command(client, message: Message):
    user_id = message.from_user.id
    if not is_admin(user_id): return
    
    if user_id not in user_data or user_data[user_id].get('state') not in ['creating_post', 'editing_post']:
        await message.reply_text("❌ No post creation or editing in progress.")
        return

    post_data = user_data[user_id]['post_data']
    state = user_data[user_id]['state']

    title = (post_data.get('content') or "Untitled Post")[:50]
    
    if state == 'creating_post':
        post_id = db.add_post(
            title,
            post_data.get('content', ''),
            post_data.get('media_type'),
            post_data.get('media_file_id'),
            post_data.get('buttons', [])
        )
        bot_username = (await client.get_me()).username
        share_link = f"https://t.me/{bot_username}?start=post_{post_id}"
        
        await message.reply_text(
            f"✅ Post saved as **Post #{post_id}**!\n\n"
            f"🔗 **Shareable Link:**\n`{share_link}`\n\n"
            "What would you like to do next?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📤 Publish Now", callback_data=f"publish_{post_id}")],
                [InlineKeyboardButton("💾 Save Only", callback_data="save_only")]
            ])
        )

    elif state == 'editing_post':
        post_id = user_data[user_id]['post_id']
        db.update_post(
            post_id, title,
            post_data.get('content', ''),
            post_data.get('media_type'),
            post_data.get('media_file_id'),
            post_data.get('buttons', [])
        )
        await message.reply_text(
            f"✅ Post #{post_id} updated successfully!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📤 Repost Now", callback_data=f"repost_{post_id}")]
            ])
        )
    
    user_data.pop(user_id, None)


# ============== MESSAGE HANDLER ==============

@app.on_message(filters.private & ~filters.command())
async def handle_messages(client, message: Message):
    user_id = message.from_user.id
    if user_id not in user_data: return

    # User searching for a post
    if user_data[user_id].get('awaiting') == 'search_query':
        query = message.text
        results = db.search_posts(query)
        if not results:
            await message.reply_text("😕 No results found for your query.")
        else:
            buttons = [[InlineKeyboardButton(title, callback_data=f"view_post_{post_id}")] for post_id, title in results]
            await message.reply_text("🔎 **Here are the search results:**", reply_markup=InlineKeyboardMarkup(buttons))
        user_data.pop(user_id, None)
        return

    if not is_admin(user_id): return
    
    # Admin adding a channel
    if user_data[user_id].get('awaiting') == 'channel_id':
        if message.forward_from_chat:
            channel_id = str(message.forward_from_chat.id)
            channel_name = message.forward_from_chat.title
        else:
            try:
                channel_id = int(message.text.strip())
                chat = await client.get_chat(channel_id)
                channel_name = chat.title
            except Exception as e:
                await message.reply_text(f"❌ Invalid channel ID or I don't have access. Error: {e}")
                return
        
        db.add_channel(channel_id, channel_name)
        await message.reply_text(f"✅ Channel **{channel_name}** (`{channel_id}`) added successfully!")
        user_data.pop(user_id, None)
        return

    # Admin creating/editing a post
    state = user_data[user_id].get('state')
    if state in ['creating_post', 'editing_post']:
        post_data = user_data[user_id]['post_data']
        
        # Capture content and media
        if not post_data.get('content_set'):
            post_data['content'] = message.text or message.caption or ""
            if message.photo:
                post_data['media_type'] = 'photo'
                post_data['media_file_id'] = message.photo.file_id
            elif message.video:
                post_data['media_type'] = 'video'
                post_data['media_file_id'] = message.video.file_id
            
            post_data['content_set'] = True
            await message.reply_text(
                "✅ Content saved! Now send buttons (one per line) in `Text | URL` format, or /done to finish."
            )
        # Capture buttons
        else:
            lines = message.text.strip().split('\n')
            buttons = post_data.get('buttons', [])
            new_buttons = 0
            for line in lines:
                if '|' in line:
                    parts = line.split('|', 1)
                    btn_text = parts[0].strip()
                    btn_url = parts[1].strip()
                    short_url = shorten_url(btn_url)
                    buttons.append({'text': btn_text, 'url': short_url})
                    new_buttons += 1
            
            post_data['buttons'] = buttons
            await message.reply_text(f"✅ Added {new_buttons} button(s)! Send more or use /done.")


# ============== CALLBACK HANDLERS ==============

@app.on_callback_query()
async def handle_callback_queries(client, callback_query: CallbackQuery):
    data = callback_query.data
    user_id = callback_query.from_user.id
    
    # User viewing a search result
    if data.startswith("view_post_"):
        post_id = data.split('_')[2]
        await send_post_to_user(client, user_id, post_id)
        await callback_query.answer()
        return

    # Admin Callbacks
    if not is_admin(user_id):
        await callback_query.answer("⛔ You are not authorized.", show_alert=True)
        return
    
    # Channel Removal
    if data.startswith("remove_ch_"):
        channel_id = data.replace('remove_ch_', '')
        db.remove_channel(channel_id)
        await callback_query.answer("✅ Channel removed!", show_alert=True)
        await callback_query.message.edit_text("✅ Channel removed successfully!")

    # Post Deletion
    elif data.startswith("delete_post_"):
        post_id = data.replace('delete_post_', '')
        db.delete_post(post_id)
        await callback_query.answer("✅ Post deleted!", show_alert=True)
        await callback_query.message.edit_text("✅ Post deleted successfully!")
    
    # Edit Post Selection
    elif data.startswith("edit_post_"):
        post_id = data.replace('edit_post_', '')
        post = db.get_post(post_id)
        if not post:
            await callback_query.answer("❌ Post not found!", show_alert=True)
            return

        content, media_type, media_file_id, buttons_json = post
        buttons = json.loads(buttons_json) if buttons_json else []
        
        user_data[user_id] = {
            'state': 'editing_post',
            'post_id': post_id,
            'post_data': {
                'content': content,
                'media_type': media_type,
                'media_file_id': media_file_id,
                'buttons': buttons,
                'content_set': False # This will allow re-capturing content
            }
        }
        await callback_query.message.edit_text(
            f"✏️ **Editing Post #{post_id}**\n\n"
            "Send the new content/media. The current content is pre-filled.\n"
            "Then, send new buttons or /done to keep the old ones and save."
        )

    # Publish/Repost - Step 1: Show channel list
    elif data.startswith("publish_") or data.startswith("repost_"):
        post_id = data.split('_')[1]
        channels = db.get_all_channels()
        if not channels:
            await callback_query.answer("❌ No channels added!", show_alert=True)
            return

        user_data[user_id] = {'selecting_channels': {'post_id': post_id, 'selected': []}}
        
        buttons = []
        for channel_id, channel_name in channels:
            buttons.append([InlineKeyboardButton(f"🔲 {channel_name}", callback_data=f"toggle_ch_{channel_id}")])
        buttons.append([InlineKeyboardButton("✅ Publish to Selected", callback_data="confirm_publish")])
        
        await callback_query.message.edit_text(
            f"**Select channels to publish Post #{post_id} to:**",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    # Publish/Repost - Step 2: Toggle channel selection
    elif data.startswith("toggle_ch_"):
        channel_id = data.replace('toggle_ch_', '')
        selection_data = user_data[user_id]['selecting_channels']
        selected_channels = selection_data['selected']
        
        if channel_id in selected_channels:
            selected_channels.remove(channel_id)
        else:
            selected_channels.append(channel_id)
        
        buttons = []
        for cid, cname in db.get_all_channels():
            status = "✅" if str(cid) in selected_channels else "🔲"
            buttons.append([InlineKeyboardButton(f"{status} {cname}", callback_data=f"toggle_ch_{cid}")])
        buttons.append([InlineKeyboardButton("✅ Publish to Selected", callback_data="confirm_publish")])
        
        await callback_query.message.edit_reply_markup(InlineKeyboardMarkup(buttons))

    # Publish/Repost - Step 3: Confirm and post
    elif data == "confirm_publish":
        selection_data = user_data[user_id]['selecting_channels']
        post_id = selection_data['post_id']
        selected_channels = selection_data['selected']

        if not selected_channels:
            await callback_query.answer("⚠️ Please select at least one channel!", show_alert=True)
            return

        post = db.get_post(post_id)
        if not post:
            await callback_query.answer("❌ Post not found!", show_alert=True)
            return

        content, media_type, media_file_id, buttons_json = post
        buttons = json.loads(buttons_json) if buttons_json else []
        keyboard = [[InlineKeyboardButton(b['text'], url=b['url'])] for b in buttons]
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        
        success_count = 0
        await callback_query.message.edit_text("🚀 **Publishing...**")

        for channel_id in selected_channels:
            try:
                if media_type == 'photo':
                    await client.send_photo(int(channel_id), media_file_id, caption=content, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
                elif media_type == 'video':
                    await client.send_video(int(channel_id), media_file_id, caption=content, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
                else:
                    await client.send_message(int(channel_id), content, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to post to {channel_id}: {e}")

        await callback_query.message.edit_text(
            f"✅ **Published!**\n\nPosted to {success_count}/{len(selected_channels)} selected channels."
        )
        user_data.pop(user_id, None)

    # Save Only
    elif data == "save_only":
        await callback_query.answer("✅ Saved!")
        await callback_query.message.edit_text("✅ Post saved! Use /repost to publish later.")

    else:
        await callback_query.answer()


# ============== RUN BOT ==============

if __name__ == "__main__":
    print("🤖 Bot started successfully!")
    app.run()```
