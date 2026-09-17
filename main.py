async def setup_security_channels(guild: discord.Guild):

    trap_channel = discord.utils.get(
        guild.text_channels,
        name=TRAP_CHANNEL_NAME
    )

    log_channel = discord.utils.get(
        guild.text_channels,
        name=LOG_CHANNEL_NAME
    )

    category = discord.utils.get(
        guild.categories,
        name="🛡️・БЕЗОПАСНОСТЬ"
    )

    if category is None:
        category = await guild.create_category(
            "🛡️・БЕЗОПАСНОСТЬ"
        )

    if log_channel is None:

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(
                view_channel=False
            )
        }

        for role in guild.roles:

            if role.permissions.administrator:

                overwrites[role] = discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True
                )

        log_channel = await guild.create_text_channel(
            LOG_CHANNEL_NAME,
            category=category,
            overwrites=overwrites,
            topic="Логи автоматических банов"
        )

    if trap_channel is None:

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                add_reactions=False,
                attach_files=False,
                embed_links=False
            )
        }

        trap_channel = await guild.create_text_channel(
            TRAP_CHANNEL_NAME,
            category=category,
            overwrites=overwrites,
            topic="Антифишинг / антискам ловушка"
        )

        embed = discord.Embed(
            title="🚨 ЛОВУШКА ДЛЯ ФИШИНГА И СКАМА",
            description=(
                "⚠️ **ВНИМАНИЕ!**\n\n"
                "Любое сообщение, отправленное в этот канал, "
                "будет автоматически удалено.\n\n"
                "🔨 **За отправку любого сообщения участник "
                "получает бан с сервера.**\n\n"
                "Этот канал создан специально для обнаружения:\n"
                "• фишинг-ссылок\n"
                "• скам-сообщений\n"
                "• скам-картинок\n"
                "• вредоносных вложений\n\n"
                "❗ **Не отправляйте сюда сообщения.**"
            ),
            color=discord.Color.red(),
            timestamp=datetime.now()
        )

        embed.set_footer(
            text="Автоматическая система защиты сервера"
        )

        await trap_channel.send(
            embed=embed
        )

    return trap_channel, log_channel

@bot.event
async def on_guild_join(guild):

    try:

        trap_channel, log_channel = (
            await setup_security_channels(guild)
        )

        embed = discord.Embed(
            title="🛡️ Система защиты активирована",
            description=(
                "Антифишинг и антискам система успешно "
                "активирована на сервере.\n\n"
                f"🚨 Ловушка: {trap_channel.mention}\n"
                f"📋 Логи: {log_channel.mention}"
            ),
            color=discord.Color.green(),
            timestamp=datetime.now()
        )

        await log_channel.send(embed=embed)

    except Exception as e:

        print(
            f"Ошибка при настройке нового сервера: {e}"
        )

    await update_bot_status()

@bot.event
async def on_guild_remove(guild):

    await update_bot_status()

    print(
        f"Бот покинул сервер: {guild.name}"
    )


@bot.event
async def on_message(message):

    # Игнорируем ботов
    if message.author.bot:
        return

    # Только серверные сообщения
    if message.guild is None:
        return

    # Проверяем канал-ловушку
    if message.channel.name != TRAP_CHANNEL_NAME:
        await bot.process_commands(message)
        return


    if message.author.guild_permissions.administrator:

        try:
            await message.delete()
        except:
            pass

        return


    message_content = message.content

    if not message_content:
        message_content = "[Вложение / изображение / файл]"

    attachments = []

    for attachment in message.attachments:
        attachments.append(attachment.url)


    try:

        await message.delete()

    except Exception as e:

        print(f"Не удалось удалить сообщение: {e}")


    guild_settings = get_guild_settings(
        message.guild.id
    )

    punishment = guild_settings.get(
        "punishment",
        "ban"
    )

    punishment_success = False
    punishment_name = ""


    if punishment == "ban":

        punishment_name = "🔨 Бан"

        try:

            await message.guild.ban(
                message.author,
                reason="Антискам: сообщение в канале-ловушке",
                delete_message_seconds=86400
            )

            punishment_success = True

        except Exception as e:

            print(f"Ошибка бана: {e}")


    elif punishment == "kick":

        punishment_name = "👢 Кик"

        try:

            await message.guild.kick(
                message.author,
                reason="Антискам: сообщение в канале-ловушке"
            )

            punishment_success = True

        except Exception as e:

            print(f"Ошибка кика: {e}")


    elif punishment == "timeout":

        duration = guild_settings.get(
            "timeout_minutes",
            10
        )

        punishment_name = (
            f"⏱️ Тайм-аут ({duration} мин.)"
        )

        try:

            until = discord.utils.utcnow() + timedelta(
                minutes=duration
            )

            await message.author.timeout(
                until,
                reason="Антискам: сообщение в канале-ловушке"
            )

            punishment_success = True

        except Exception as e:

            print(f"Ошибка тайм-аута: {e}")

    log_channel = discord.utils.get(
        message.guild.text_channels,
        name=LOG_CHANNEL_NAME
    )

    if log_channel is None:
        return

    if punishment_success:

        embed = discord.Embed(
            title="🚨 АВТОМАТИЧЕСКОЕ НАКАЗАНИЕ",
            description=(
                "Участник отправил сообщение "
                "в канал-ловушку."
            ),
            color=discord.Color.red(),
            timestamp=datetime.now()
        )

        embed.add_field(
            name="👤 Нарушитель",
            value=(
                f"{message.author.mention}\n"
                f"`{message.author}`"
            ),
            inline=False
        )

        embed.add_field(
            name="🆔 ID пользователя",
            value=f"`{message.author.id}`",
            inline=True
        )

        embed.add_field(
            name="⚖️ Наказание",
            value=punishment_name,
            inline=True
        )

        embed.add_field(
            name="📍 Канал",
            value=message.channel.mention,
            inline=True
        )

        embed.add_field(
            name="💬 Сообщение",
            value=f"```{message_content[:1000]}```",
            inline=False
        )

        if attachments:

            embed.add_field(
                name="📎 Вложения",
                value="\n".join(attachments)[:1000],
                inline=False
            )

        embed.set_thumbnail(
            url=message.author.display_avatar.url
        )

        embed.set_footer(
            text="Anti-Scam Security System"
        )

        await log_channel.send(
            embed=embed
        )

    else:

        embed = discord.Embed(
            title="⚠️ НЕ УДАЛОСЬ НАКАЗАТЬ",
            description=(
                "Пользователь отправил сообщение "
                "в канал-ловушку, но бот не смог "
                "применить выбранное наказание."
            ),
            color=discord.Color.orange(),
            timestamp=datetime.now()
        )

        embed.add_field(
            name="👤 Пользователь",
            value=(
                f"{message.author.mention}\n"
                f"`{message.author.id}`"
            ),
            inline=False
        )

        embed.add_field(
            name="⚖️ Выбранное наказание",
            value=punishment_name,
            inline=False
        )

        embed.add_field(
            name="💬 Сообщение",
            value=f"```{message_content[:1000]}```",
            inline=False
        )

        await log_channel.send(
            embed=embed
        )
