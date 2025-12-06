# Multi-Channel Telegram Post Manager Bot

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pyrogram](https://img.shields.io/badge/Pyrogram-2.0.106-0088cc?style=for-the-badge&logo=telegram&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

A powerful Telegram bot for managing and publishing posts across multiple channels with built-in URL shortening, rich media support, and an intuitive admin interface.

---

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage Guide](#usage-guide)
  - [Admin Commands](#admin-commands)
  - [Creating Posts](#creating-posts)
  - [Managing Channels](#managing-channels)
  - [Publishing Posts](#publishing-posts)
- [Post Formatting](#post-formatting)
- [User Search Feature](#user-search-feature)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## Features

**Content Management**
- Create, edit, and delete posts with rich text formatting
- Support for photos and videos with captions
- Inline button support with automatic URL shortening via ShrinkEarn
- Save posts for later use with shareable deep links
- Search posts by title or content

**Multi-Channel Publishing**
- Add and manage multiple channels/groups
- Selective channel publishing with checkbox interface
- Batch publish to multiple channels simultaneously
- Channel verification and access validation

**User Experience**
- Admin control panel with intuitive commands
- Non-admin users can search and view posts
- Markdown formatting support for rich text
- Organized button layouts (2 buttons per row)

**Technical Features**
- SQLite database for persistent storage
- Structured logging for debugging
- Session-based state management
- Error handling and fallback mechanisms

---

## Prerequisites

Before setting up the bot, ensure you have:

1. **Python 3.8 or higher** installed on your system
2. **Telegram API credentials** (API ID and API Hash)
   - Obtain from [my.telegram.org](https://my.telegram.org)
3. **Bot Token** from [@BotFather](https://t.me/BotFather)
4. **ShrinkEarn API Key** (optional, for URL shortening)
   - Register at [ShrinkEarn](https://shrinkearn.com)
5. **Your Telegram User ID**
   - Get from [@userinfobot](https://t.me/userinfobot)

---

## Installation

### Step 1: Clone or Download the Project

```bash
git clone <your-repository-url>
cd telegram-multi-channel-bot
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

The required packages are:
- `pyrogram==2.0.106` - Telegram MTProto API framework
- `tgcrypto==1.2.5` - Encryption for Pyrogram
- `requests==2.31.0` - HTTP library for URL shortening
- `aiohttp==3.9.5` - Async HTTP client
- `pyrofork==2.3.41` - Fork of Pyrogram with additional features

### Step 3: Configure the Bot

Edit `config.py` with your credentials:

```python
API_ID = 12345678  # Your API ID from my.telegram.org
API_HASH = "your_api_hash_here"  # Your API Hash
BOT_TOKEN = "123456:ABCdefGHIjklMNOpqrsTUVwxyz"  # From @BotFather

# ShrinkEarn API key (optional)
SHORTENER_API = "your_shrinkearn_api_key"

# Admin user IDs (can be multiple)
ADMINS = [123456789, 987654321]  # Your Telegram user ID(s)
```

### Step 4: Run the Bot

```bash
python main.py
```

You should see: **"Bot started successfully!"**

---

## Configuration

### config.py Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `API_ID` | Integer | Yes | Telegram API ID from my.telegram.org |
| `API_HASH` | String | Yes | Telegram API Hash from my.telegram.org |
| `BOT_TOKEN` | String | Yes | Bot token from @BotFather |
| `SHORTENER_API` | String | No | ShrinkEarn API key for URL shortening |
| `ADMINS` | List | Yes | List of Telegram user IDs with admin access |

### Database

The bot automatically creates `bot_data.db` with two tables:
- **posts**: Stores all created posts with metadata
- **channels**: Stores registered channels/groups

---

## Usage Guide

### Admin Commands

Once configured, admins have access to these commands:

#### Post Management
- `/newpost` - Create a new post
- `/editpost` - Edit an existing post
- `/listposts` - View all saved posts
- `/deletepost` - Delete a post
- `/repost` - Republish a saved post

#### Channel Management
- `/addchannel` - Add a channel or group
- `/listchannels` - View all registered channels
- `/removechannel` - Remove a channel

#### General
- `/start` - Show welcome message and command list
- `/help` - Display help information

---

### Creating Posts

#### Step 1: Start Post Creation

Send `/newpost` to the bot. You'll see:

```
📝 Creating New Post

Send me your post content with optional media (photo/video).
You can use Telegram's built-in tools for formatting.

After that, send buttons in this format:
Button Text | URL

To shorten a link, add {url} at the end:
Button Text | http://mylink.com{url}

Send /done when finished.
```

#### Step 2: Send Content

Send your message with optional photo or video. The bot preserves:
- **Bold** text
- *Italic* text
- `Code` formatting
- Links

**Example:**
```
🎉 New Product Launch!

Check out our latest **premium features**:
- Advanced analytics
- Real-time updates
- Custom integrations

Visit our website for more details!
```

#### Step 3: Add Buttons (Optional)

Send buttons one per line in the format: `Button Text | URL`

**Example:**
```
📱 Download App | https://example.com/app{url}
🌐 Visit Website | https://example.com
💬 Contact Support | https://t.me/support
```

**Note:** Adding `{url}` at the end of a URL triggers automatic shortening via ShrinkEarn.

#### Step 4: Finish Post

Send `/done` to save the post. The bot will generate:
- A unique Post ID
- A shareable link (e.g., `https://t.me/YourBot?start=post_123`)
- Options to publish immediately or save for later

#### Post Preview Structure

Your post will appear with a clean, professional layout:

**Post Structure:**
- **Header Image/Video**: Media is displayed at the top (full width)
- **Title**: Post title appears prominently below the media
- **Content**: Body text with preserved Markdown formatting
- **Metadata**: Additional information (ratings, quality, genres, etc.)
- **Action Buttons**: Arranged in a 2-column grid layout for easy access
- **Footer**: Posted by information and view count

**Example Post Layout:**

```
┌─────────────────────────────────────┐
│                                     │
│      [Featured Image/Video]         │
│                                     │
├─────────────────────────────────────┤
│  Twilight Vampire 2008              │
│                                     │
│  👉 Audio: English, Hindi           │
│  👉 Ratings: 5.4/10                 │
│  👉 Quality: 720p, 1080p            │
│  👉 Genres: Romance, Fantasy        │
│                                     │
│  ✅ Posted by - Search Channel Bot  │
│  👁 29 views | edited 10:24         │
│                                     │
├─────────────────────────────────────┤
│  [  Download ↗  ] [  Premium ↗  ]  │
└─────────────────────────────────────┘
```

**Button Layout:** Buttons are automatically arranged in rows of 2 for optimal mobile viewing and easy thumb access.

---

### Managing Channels

#### Adding a Channel

**Method 1: Forward a Message**
1. Send `/addchannel`
2. Forward any message from the target channel to the bot
3. The bot extracts channel ID and name automatically

**Method 2: Send Channel ID**
1. Send `/addchannel`
2. Send the channel ID (e.g., `-1001234567890`)
3. The bot verifies access and retrieves channel name

**Important:** Make sure the bot is added as an administrator in the channel with posting permissions.

#### Listing Channels

Send `/listchannels` to see all registered channels:

```
📢 Your Channels:

• Tech News Channel (-1001234567890)
• Product Updates (-1009876543210)
• Community Group (-1005555555555)
```

#### Removing a Channel

1. Send `/removechannel`
2. Select the channel from the button list
3. Confirm removal

---

### Publishing Posts

#### Option 1: Publish During Creation

After sending `/done`, choose **"Publish Now"**:
1. Select target channels from the checkbox list
2. Click channels to toggle selection (✅ = selected)
3. Press **"Publish to Selected"**
4. The bot posts to all selected channels

#### Option 2: Republish Saved Posts

1. Send `/repost`
2. Select the post from the list
3. Choose target channels
4. Confirm publication

#### Publishing Process

```
📤 Publishing...

✅ Posted to Tech News Channel
✅ Posted to Product Updates
❌ Failed: Community Group (Permission denied)

✅ Published!
Posted to 2/3 selected channels.
```

---

## Post Formatting

The bot supports Telegram's Markdown formatting:

| Style | Syntax | Example |
|-------|--------|---------|
| Bold | `**text**` | **bold text** |
| Italic | `*text*` | *italic text* |
| Code | `` `text` `` | `code` |
| Links | `[text](url)` | [link](https://example.com) |

**Note:** Formatting is preserved from the original message using Pyrogram's `.markdown` property.

---

## User Search Feature

Non-admin users can search for posts:

1. Send any text message to the bot
2. The bot searches titles and content
3. Results appear as clickable buttons
4. Clicking a button displays the full post with media and buttons

**Example:**
```
User: product launch
Bot: 🔍 Here are the search results:
     [🎉 New Product Launch]
     [📱 Product Update v2.0]
```

---

## Project Structure

```
telegram-multi-channel-bot/
│
├── main.py              # Main bot logic and handlers
├── database.py          # SQLite database operations
├── config.py            # Configuration file
├── requirements.txt     # Python dependencies
├── bot_data.db          # SQLite database (auto-generated)
└── README.md            # This file
```

### Key Components

**main.py**
- Command handlers for all bot operations
- Message processing for post creation
- Callback query handlers for inline buttons
- Channel and post management logic

**database.py**
- Database initialization and schema
- CRUD operations for posts and channels
- Search functionality

**config.py**
- API credentials
- Admin user IDs
- URL shortener configuration

---

## Troubleshooting

### Bot Not Responding

**Check:**
- Bot token is correct in `config.py`
- Bot is running (`python main.py`)
- Check console for error messages

### Cannot Add Channel

**Solutions:**
- Ensure bot is added as admin to the channel
- Verify channel ID format (should start with `-100`)
- Check bot has posting permissions

### URL Shortening Not Working

**Solutions:**
- Verify ShrinkEarn API key is valid
- Check internet connection
- Ensure URL ends with `{url}` tag

### Posts Not Publishing

**Check:**
- Bot has admin rights in target channels
- Bot can post messages in channels
- Channel IDs are correct in database

### Formatting Lost in Posts

**Solution:**
- Use Telegram's native formatting tools when composing
- Avoid plain text editors that strip formatting
- Test with `/newpost` to verify

---

## Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit your changes** (`git commit -m 'Add some AmazingFeature'`)
4. **Push to the branch** (`git push origin feature/AmazingFeature`)
5. **Open a Pull Request**

### Ideas for Contributions

- Scheduled posting functionality
- Multi-language support
- Advanced analytics dashboard
- Custom button layouts
- Post templates
- Media gallery management

---

## License

This project is open source and available under the MIT License.

---

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact the maintainer via Telegram

---

## Acknowledgments

Built with:
- [Pyrogram](https://docs.pyrogram.org/) - Telegram MTProto API Framework
- [ShrinkEarn](https://shrinkearn.com) - URL Shortening Service
- SQLite - Lightweight database engine

---

**Made with ☕ and Python**