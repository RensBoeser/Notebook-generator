import os, json, re

def dateSortKey(entry):
	date = entry['date'].split('-')
	if len(date) == 3:
		return int(date[2].zfill(4) + date[1].zfill(2) + date[0].zfill(2))
	else:
		print(date)
		return 1

def fillAttendees(entry):
	# eLabJournal does not allow contributor names to be sent over the API due to missing functionalities.
	# This is hardcoded for all the experiments we have on our notebook.
	attendees = {
		"assessing cooa production": "Dustin van der Meulen",
		"assessing gas production biobricks in e.coli": "Elise Grootscholten | Randall de Waard",
		"transformation": "Loraine Nelson | Elise Grootscholten | Paul Reusink",
		"testing gas production": "Elise Grootscholten | Paul Reusink",
		"urea and sodium pyruvate test for resistance e.coli": "Randall de Waard | Elise Grootscholten",
		"chemo competent cells": "Dustin van der Meulen | Jos Veldscholte | Loraine Nelson",
		"making competent neB10beta cells": "Dustin van der Meulen | Jos Veldscholte",
		"pcr": "Randall de Waard | Elise Grootscholten"
	}
	if entry['attendees'] == "UNKNOWN":
		entry['attendees'] = attendees.get(entry['title'].lower())
	return entry['attendees']

class NotebookGenerator:
	def __init__(self, inputJSON, outputdir, libdir, pageName='notebook'):
		self._libdir = libdir
		self._outputdir = outputdir
		self.PageName = pageName

		self.Style  = '<style> \n{0}\n</style>'.format(open(self._libdir + 'notebook.css').read())
		self.Header = '''
	<h1 class="title">Notebook</h1>

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
		self.EntryList = sorted(self.EntryList, key=dateSortKey)
		
	
	def GenerateEntry(self, entry, id):
		# Identifier needed for the checkbox hack in html
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
																		 id,
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

		id = 1
		generatedEntries = ''
		for entry in self.EntryList:
			splitdate = entry['date'].split('-')
			# entryMonth = month.get(splitdate[1])
			entry['dateformatted'] = str(month.get(int(splitdate[1]))) + " " + str(int(splitdate[0]))
			entry['attendees'] = fillAttendees(entry)

			entry['description'] = entry['description'].replace('µ', '&mu;').replace('é', 'e&#769;').replace('°', '&deg;')
			# instances = [m.start() for m in re.finditer('°', entry['description'])]
			# print(entry['title'] + ': ', end="")
			# print(instances)

			generatedEntries = generatedEntries + (self.GenerateEntry(entry, id))
			id = id + 1
		
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