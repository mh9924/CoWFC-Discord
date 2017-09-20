import requests

from bs4 import BeautifulSoup
from discord.ext import commands

class Info:

	def __init__(self, bot):
		self.bot = bot

	@commands.command(pass_context=True)
	async def stats(self):
		r = requests.get(self.bot.config['info']['dwc_stats_page'])
		soup = BeautifulSoup(r.content, "html.parser")
		lastupdate = soup.find('i').getText()
		if soup.find('center') is None:
			numusers = '0'
		else:
			numusers = soup.find('center').getText()
		message = "There are currently "+numusers+" out of max 12 players online. ("+lastupdate+")"
		await self.bot.say(message)
		
	@commands.command(pass_context=True)
	async def errors(self):
		r = requests.get(self.bot.config['info']['errors_page'])
		soup = BeautifulSoup(r.content, "html.parser")
		message = ''
		for error in soup.findAll('li', attrs={'id':'error'}):
			message += error.getText()+'\n'
		await self.bot.say(message)