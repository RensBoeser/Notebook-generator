import os, csv, random, operator

class NotebookGenerator:
	def __init__(self, outputdir, libdir, pageName):
		self._libdir = libdir
		self._outputdir = outputdir
		self.PageName = pageName

		self.Style  = '<style> \n{0}\n</style>'.format(open(self._libdir + 'notebook.css').read())
		self.Header = '''
	<input type="checkbox" class="wetlab-filter" checked><span>show wetlab entries<br></span></input>
	<input type="checkbox" class="hardware-filter" checked><span>show hardware entries<br></span></input>
	<input type="checkbox" class="software-filter"><span>show software entries<br></span></input>
		'''
		self.Footer = '</div>'

		self.EntryTemplate = open(self._libdir + 'entryTemplate.txt').read()
		
		self.EntryList = list()
		# Reading entries from entries.csv and adds them to a list
		with open(self._libdir + 'entries.csv', newline='') as entries:
			reader = csv.DictReader(entries)
			for row in reader:
				self.EntryList.append(row)
		# Sort entries on date | TODO: THIS SORTS ON DAYS ONLY
		# self.EntryList = sorted(self.EntryList, key=lambda entry: entry['date'])
		
	
	def GenerateEntry(self, entry):
		# Identifier needed for the checkbox hack in html
		identifier = random.randint(00000000, 99999999)
		# Get the right svg file for the entry
		if 	 entry['category'] == 'hardware': icon = open(self._libdir + 'hardware_icon.html').read()
		elif entry['category'] == 'wetlab': 	icon = open(self._libdir + 'wetlab_icon.html').read()
		else: 																icon = open(self._libdir + 'software_icon.html').read()
		# Adding all variables to the template string for finalized entry html code
		return self.EntryTemplate.format(entry['title'],
																		 entry['date'],
																		 entry['attendees'],
																		 entry['description'],
																		 entry['experimentday'],
																		 entry['category'],
																		 identifier,
																		 icon)
	def GeneratePage(self):
		month = {
			'1': "January",
			'2': "February",
			'3': "March",
			'4': "April",
			'5': "May",
			'6': "June",
			'7': "July",
			'8': "August",
			'9': "September",
			'10': "October",
			'11': "November",
			'12': "December"
		}

		generatedEntries = ''
		currentMonth = ''
		for entry in self.EntryList:
			entryMonth = month.get(entry['date'].split('-')[1]) # beautiful code I must say! 1. Get date from entry['date'] 2. Get month from that date 4. Get monthname form
			if currentMonth != entryMonth: # If a new month starts
				currentMonth = entryMonth
				if generatedEntries != '': # If it is not the first month
					generatedEntries = generatedEntries + '</div>\n'
				generatedEntries = generatedEntries + '\n<h1 class="month">{0}</h1>\n<div class="cards">\n'.format(entryMonth) # Adds the monthname to the page

			generatedEntries = generatedEntries + (self.GenerateEntry(entry))
		
		page = self.Style + self.Header + generatedEntries + self.Footer
		self.WritePage(page)
	
	def WritePage(self, page):
		with open(self._outputdir + 'project' + '-' + self.PageName.lower() + '.html', 'w') as f: # TODO: remove the hardcoded 'project' category
			f.write(page)

if __name__ == '__main__': #Debug code
	print('Start debug code')
	gen = NotebookGenerator('./output/', './lib/', 'test')
	gen.GeneratePage()