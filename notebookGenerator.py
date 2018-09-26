import os, csv, random, operator, json

def dateSortKey(entry):
	date = entry['date'].split('-')
	if len(date) == 3:
		return int(date[2]) * 10000 + int(date[1]) * 100 + int(date[0])
	else:
		print(date)
		return 1

class NotebookGenerator:
	def __init__(self, inputJSON, outputdir, libdir, pageName='notebook'):
		self._libdir = libdir
		self._outputdir = outputdir
		self.PageName = pageName

		self.Style  = '<style> \n{0}\n</style>'.format(open(self._libdir + 'notebook.css').read())
		self.Header = '''
	<input type="checkbox" class="wetlab-filter" checked><span>show wetlab entries<br></span></input>
	<input type="checkbox" class="hardware-filter" checked><span>show hardware entries<br></span></input>
	<input type="checkbox" class="software-filter"><span>show software entries<br></span></input>
	<div class="cards">\n
		'''
		self.Footer = '</div>'

		self.EntryTemplate = open(self._libdir + 'entryTemplate.txt').read()
		
		self.EntryList = list()
		# Reading entries from input.json and adds them to a list
		for i in inputJSON:
			data = json.loads(i)
			for row in data['entries']:
				if row['date']:
					self.EntryList.append(row)
		# Sort entries on date | TODO: THIS SORTS ON DAYS ONLY
		self.EntryList = sorted(self.EntryList, key=dateSortKey)
		
	
	def GenerateEntry(self, entry):
		# Identifier needed for the checkbox hack in html
		identifier = random.randint(00000000, 99999999)
		# Get the right svg file for the entry
		if 	 entry['category'] == 'hardware': icon = open(self._libdir + 'hardware_icon.html').read()
		elif entry['category'] == 'wetlab': 	icon = open(self._libdir + 'wetlab_icon.html').read()
		else: 																icon = open(self._libdir + 'software_icon.html').read()
		# Adding all variables to the template string for finalized entry html code
		return self.EntryTemplate.format(entry['title'],
																		 entry['dateformatted'],
																		 entry['attendees'],
																		 entry['description'],
																		 entry['experimentday'],
																		 entry['category'],
																		 identifier,
																		 icon)
	def GeneratePage(self):
		month = {
			1: "January",
			2: "February",
			3: "March",
			4: "April",
			5: "May",
			6: "June",
			7: "July",
			8: "August",
			9: "September",
			10: "October",
			11: "November",
			12: "December"
		}

		generatedEntries = ''
		currentMonth = ''
		for entry in self.EntryList:
			splitdate = entry['date'].split('-')
			entryMonth = month.get(splitdate[1]) # beautiful code I must say! 1. Get date from entry['date'] 2. Get month from that date 4. Get monthname form
			entry['dateformatted'] = str(month.get(int(splitdate[1]))) + " " + str(int(splitdate[0]))
			generatedEntries = generatedEntries + (self.GenerateEntry(entry))
		
		page = self.Style + self.Header + generatedEntries + self.Footer
		self.WritePage(page)
	
	def WritePage(self, page):
		with open(self._outputdir + 'project' + '-' + self.PageName.lower() + '.html', 'w') as f: # TODO: remove the hardcoded 'project' category
			page = page.replace('\u200B', '')
			f.write(page)

if __name__ == '__main__': #Debug code
	print('Start debug code')
	with open('./input.json', 'r') as entries:
		data = entries.read()
		outputdir = os.path.dirname(os.path.realpath(__file__)) + '/output/'
		gen = NotebookGenerator([data, data], outputdir, './lib/', 'test')
	gen.GeneratePage()