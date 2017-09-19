import asyncio
import discord
import markovify.text
import random

from time import time

class Messages(discord.Client):

	def __init__(self, bot):
		self.bot = bot

		self.magic_file = self.bot.config['messages']['file']
		self.response_whitelist = self.bot.config['messages']['response_whitelist'].split(' ')
		self.learn_whitelist = self.bot.config['messages']['learn_whitelist'].split(' ')
		self.phrase_channel = self.bot.config['messages']['phrase_channel']

		self.last_message_time = time()

		self._refresh_magic_file()

		bot.loop.create_task(self.phrase())

	async def phrase(self):
		await self.bot.wait_until_ready()

		while not self.bot.is_closed:
			await asyncio.sleep(3000)
			if time() - self.last_message_time < 300:
				self._refresh_magic_file()
				sentence = self.markov.make_sentence(tries=200)

				for channel in self.bot.get_all_channels():
					if self.phrase_channel in channel.name:
						await self.bot.send_typing(channel)
						await asyncio.sleep(0.1 * len(sentence))
						await self.bot.send_message(channel, sentence)

						print('Sent phrase "{0}"'.format(sentence))

						break


	def _refresh_magic_file(self):
		try:
			with open(self.magic_file, 'r', encoding='utf-8', errors='ignore') as magic_file:
				text = magic_file.read()

				self.markov = markovify.text.NewlineText(text)

		except Exception as e:
			print('Magic file doesn\'t exist. Creating..')
			open(self.magic_file, 'w+', encoding='utf-8', errors='ignore').close()

	def add_phrase(self, phrase):
		tokenized_phrase = phrase.split('. ')
		fixed_phrase = '\n'.join(tokenized_phrase).rstrip('.')

		try:
			with open(self.magic_file, 'a+', encoding='utf-8') as magic_file:
				magic_file.write('{0}\n'.format(fixed_phrase))

		except Exception as e:
			print('Error adding phrase!')
			print(e)

	async def _handle_message(self, message):
		if not self.bot.user.id in message.content:
			self.add_phrase(message.clean_content)
			print('Adding phrase {0} said by {1}'.format(message.clean_content, message.author.display_name))

		if not type(message.channel) is discord.PrivateChannel:
			if message.channel.name in self.response_whitelist and self.bot.user.id in message.content:
				self._refresh_magic_file()
				sentence = self.markov.make_sentence(tries=200)
				await asyncio.sleep(random.uniform(1,5))
				await self.bot.send_typing(message.channel)
				await asyncio.sleep(min(10, 0.1 * len(sentence)))
				await self.bot.send_message(message.channel, '{0}'.format(sentence))

	@asyncio.coroutine
	async def on_message(self, message):
		try:
			appropriate_medium = message.channel.name in self.learn_whitelist or message.channel.is_private

			if not message.content.startswith('$') and not message.author == self.bot.user \
				and	appropriate_medium and not message.author.bot:
				print('Received {0} from {1}'.format(message.content, message.author.display_name))

				await self._handle_message(message)

				self.last_message_time = time()

		except AttributeError as e:
			await self._handle_message(message)