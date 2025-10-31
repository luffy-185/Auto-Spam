import asyncio
import random
import re
import os
from telethon import TelegramClient, events

# ==== CONFIG ====
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
SESSION = os.getenv('SESSION_STRING')
BOT_DM = "@Slave_waifu_bot"  # Target bot DM
ADMIN_ID = int(os.getenv('OWNER_ID'))

# ==== STATE ====
rdm_spamming = False
rdm_task = None

client = TelegramClient(SESSION, API_ID, API_HASH)

def generate_combinations(template):
    """Generate all combinations for (a-z) or (1-9) patterns"""
    # Pattern for letters: (a-z)
    letter_pattern = r'\(a-z\)'
    # Pattern for numbers: (1-9)
    number_pattern = r'\(1-9\)'

    if re.search(letter_pattern, template):
        # Generate all letters a-z and shuffle
        letters = [chr(i) for i in range(97, 123)]  # a to z
        random.shuffle(letters)
        combinations = [re.sub(letter_pattern, letter, template) for letter in letters]
        return combinations

    elif re.search(number_pattern, template):
        # Generate all numbers 1-9 and shuffle
        numbers = [str(i) for i in range(1, 10)]  # 1 to 9
        random.shuffle(numbers)
        combinations = [re.sub(number_pattern, num, template) for num in numbers]
        return combinations

    return []

async def rdm_spam_loop(template):
    """Main random spam loop"""
    global rdm_spamming

    combinations = generate_combinations(template)

    if not combinations:
        await client.send_message(BOT_DM, "âŒ Invalid pattern. Use (a-z) or (1-9)")
        rdm_spamming = False
        return

    total = len(combinations)
    sent = 0

    await client.send_message(ADMIN_ID, f"ðŸŽ² Starting random spam in DM: {total} combinations")

    for combo in combinations:
        if not rdm_spamming:
            break

        try:
            await client.send_message(BOT_DM, combo)
            sent += 1
            print(f"âœ… Sent to DM: {combo} ({sent}/{total})")

            # Very fast delay between 0.3-0.8 seconds
            delay = random.uniform(0.3, 0.8)
            await asyncio.sleep(delay)

        except Exception as e:
            print(f"âŒ Error sending {combo}: {e}")
            await asyncio.sleep(2)  # Longer delay on error

    if rdm_spamming:
        await client.send_message(ADMIN_ID, f"âœ… Random spam completed! Sent {sent}/{total} to DM")
    else:
        await client.send_message(ADMIN_ID, f"ðŸ›‘ Random spam stopped! Sent {sent}/{total} to DM")

    rdm_spamming = False

@client.on(events.NewMessage(from_users=ADMIN_ID, pattern='^/rdm'))
async def rdm_handler(event):
    global rdm_spamming, rdm_task

    if rdm_spamming:
        await event.reply("âŒ Random spam is already running. Use /rdmstop first.")
        return

    try:
        args = event.raw_text.split(maxsplit=1)
        if len(args) < 2:
            await event.reply("âŒ Usage: `/rdm <template>`\n\n"
                            "**Examples:**\n"
                            "â€¢ `/rdm /sredeem ZORO-(a-z)woc9`\n"
                            "â€¢ `/rdm /sredeem ZORO-awoc(1-9)`")
            return

        template = args[1]

        # Validate template
        if not ('(a-z)' in template or '(1-9)' in template):
            await event.reply("âŒ Template must contain (a-z) or (1-9) pattern")
            return

        rdm_spamming = True

        # Start the spam loop
        rdm_task = asyncio.create_task(rdm_spam_loop(template))

        if '(a-z)' in template:
            pattern_type = "letters (a-z)"
            total = 26
        else:
            pattern_type = "numbers (1-9)"
            total = 9

        await event.reply(f"ðŸŽ² **Random Spam Started in DM!**\n"
                         f"ðŸ“ Template: `{template}`\n"
                         f"ðŸ”¤ Pattern: `{pattern_type}`\n"
                         f"ðŸ“Š Total: `{total}` combinations\n"
                         f"â±ï¸ Delay: `0.3-0.8s` (Fast)\n"
                         f"ðŸ¤– Target: `{BOT_DM}`")

    except Exception as e:
        await event.reply(f"âŒ Error: {str(e)}")
        rdm_spamming = False

@client.on(events.NewMessage(from_users=ADMIN_ID, pattern='^/rdmstop$'))
async def rdm_stop_handler(event):
    global rdm_spamming, rdm_task
    if rdm_spamming:
        rdm_spamming = False
        if rdm_task:
            rdm_task.cancel()
        await event.reply("ðŸ›‘ Random spam stopped!")
    else:
        await event.reply("âŒ No random spam running.")

@client.on(events.NewMessage(from_users=ADMIN_ID, pattern='^/rdmstats$'))
async def rdm_stats_handler(event):
    status = "ðŸŸ¢ Running" if rdm_spamming else "ðŸ”´ Stopped"
    await event.reply(f"ðŸŽ² **Random Spam Status**\nâ€¢ Status: {status}\nâ€¢ Target: `{BOT_DM}`")

@client.on(events.NewMessage(from_users=ADMIN_ID, pattern='^/rdmtest'))
async def rdm_test_handler(event):
    """Test pattern without actually spamming"""
    try:
        args = event.raw_text.split(maxsplit=1)
        if len(args) < 2:
            await event.reply("âŒ Usage: `/rdmtest <template>`")
            return

        template = args[1]
        combinations = generate_combinations(template)

        if not combinations:
            await event.reply("âŒ Invalid pattern. Use (a-z) or (1-9)")
            return

        sample = combinations[:5]  # Show first 5 combinations
        sample_text = "\n".join([f"â€¢ `{combo}`" for combo in sample])

        if '(a-z)' in template:
            pattern_type = "letters (a-z)"
            total = 26
        else:
            pattern_type = "numbers (1-9)"
            total = 9

        await event.reply(f"ðŸ§ª **Pattern Test**\n"
                         f"ðŸ“ Template: `{template}`\n"
                         f"ðŸ”¤ Pattern: `{pattern_type}`\n"
                         f"ðŸ“Š Total combinations: `{total}`\n"
                         f"ðŸ¤– Target: `{BOT_DM}`\n"
                         f"ðŸŽ² Sample (first 5):\n{sample_text}")

    except Exception as e:
        await event.reply(f"âŒ Error: {str(e)}")

@client.on(events.NewMessage(from_users=ADMIN_ID, pattern='^/rdmfast'))
async def rdm_fast_handler(event):
    """Ultra fast mode - 0.1-0.3s delay"""
    global rdm_spamming, rdm_task

    if rdm_spamming:
        await event.reply("âŒ Random spam is already running. Use /rdmstop first.")
        return

    try:
        args = event.raw_text.split(maxsplit=1)
        if len(args) < 2:
            await event.reply("âŒ Usage: `/rdmfast <template>`")
            return

        template = args[1]

        # Validate template
        if not ('(a-z)' in template or '(1-9)' in template):
            await event.reply("âŒ Template must contain (a-z) or (1-9) pattern")
            return

        rdm_spamming = True

        # Start ultra fast spam
        asyncio.create_task(rdm_fast_spam_loop(template))

        if '(a-z)' in template:
            pattern_type = "letters (a-z)"
            total = 26
        else:
            pattern_type = "numbers (1-9)"
            total = 9

        await event.reply(f"âš¡ **ULTRA FAST Spam Started!**\n"
                         f"ðŸ“ Template: `{template}`\n"
                         f"ðŸ”¤ Pattern: `{pattern_type}`\n"
                         f"ðŸ“Š Total: `{total}` combinations\n"
                         f"â±ï¸ Delay: `0.1-0.3s` (Ultra Fast)\n"
                         f"ðŸ¤– Target: `{BOT_DM}`")

    except Exception as e:
        await event.reply(f"âŒ Error: {str(e)}")
        rdm_spamming = False

async def rdm_fast_spam_loop(template):
    """Ultra fast spam loop"""
    global rdm_spamming

    combinations = generate_combinations(template)

    if not combinations:
        await client.send_message(BOT_DM, "âŒ Invalid pattern. Use (a-z) or (1-9)")
        rdm_spamming = False
        return

    total = len(combinations)
    sent = 0

    await client.send_message(ADMIN_ID, f"âš¡ Starting ULTRA FAST spam in DM: {total} combinations")

    for combo in combinations:
        if not rdm_spamming:
            break

        try:
            await client.send_message(BOT_DM, combo)
            sent += 1
            print(f"âš¡ Sent to DM: {combo} ({sent}/{total})")

            # Ultra fast delay between 0.1-0.3 seconds
            delay = random.uniform(0.1, 0.3)
            await asyncio.sleep(delay)

        except Exception as e:
            print(f"âŒ Error sending {combo}: {e}")
            await asyncio.sleep(1)  # Longer delay on error

    if rdm_spamming:
        await client.send_message(ADMIN_ID, f"âœ… Ultra fast spam completed! Sent {sent}/{total} to DM")
    else:
        await client.send_message(ADMIN_ID, f"ðŸ›‘ Ultra fast spam stopped! Sent {sent}/{total} to DM")

    rdm_spamming = False

async def main():
    await client.start()
    print(f"âœ… Random Spam Bot Started!")
    print(f"ðŸ‘¤ Admin: {ADMIN_ID}")
    print(f"ðŸ¤– Target DM: {BOT_DM}")
    print(f"ðŸŽ² Ready for /rdm commands in any chat")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
