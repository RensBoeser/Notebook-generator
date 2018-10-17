# -*- coding: utf-8 -*-
import os, json, re

def dateSortKey(entry):
	date = entry['date'].split('-')
	if len(date) == 3:
		return int(date[2].zfill(4) + date[1].zfill(2) + date[0].zfill(2))
	else:
		print(date)
		return 1

def htmlify(text):
	return text.replace('µ', '&mu;').replace('é', '&eacute;').replace('°', '&deg;').replace('\u200B', '').replace('\u03bc', '&mu;').replace('º', '&deg;').replace('è', '&egrave;').replace('\u2248', '&asymp;')

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
		"making competent neb10beta cells": "Loraine Nelson | Jos Veldscholte",
		"pcr": "Randall de Waard | Elise Grootscholten",
		"preparing dna for submission": "Dustin Vermeulen | Elise Grootscholten | Randall de Waard"
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

	<div class="text-container">
		<p>
			As a team with only one computer scientist (and one electrical engineer who can program),
			we wanted a notebook that automatically updates whenever someone adds something to our lab journal.
			Luckily, we gained a sponsor that gave use an electronic lab journal as sponsorship.
			With this, we can use their API to download specific sections from our lab journal and display them on or wiki.
			But, as a multidisciplinary team we have multiple kinds of notebook entries: Software, Hardware and Wetlab.
			Therefore we also used the Google Drive RESTful API for downloading software and hardware entries from google sheets files.
		</p>
		<a class="nav-button" href="http://2018.igem.org/Team:Rotterdam_HR/Software">More info about the notebook generator</a>
	</div>

	<input type="checkbox" class="wetlab-filter" checked><span>show wetlab entries<br></span></input>
	<input type="checkbox" class="hardware-filter" checked><span>show hardware entries<br></span></input>
	<input type="checkbox" class="software-filter"><span>show software entries<br></span></input>
	<div class="cards">\n
		'''
		self.Footer = '''
		</div>
		<div class="text-container relevant">
  <h1>Relevant pages</h1>
  <div class="nav-cards">
    <a href="http://2018.igem.org/Team:Rotterdam_HR/Results" class="nav-card">
      <h2>Results</h2>
			<svg viewBox="0 0 24 24">
				<path d="M19,3H14.82C14.4,1.84 13.3,1 12,1C10.7,1 9.6,1.84 9.18,3H5A2,2 0 0,0 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V5A2,2 0 0,0 19,3M12,3A1,1 0 0,1 13,4A1,1 0 0,1 12,5A1,1 0 0,1 11,4A1,1 0 0,1 12,3M7,7H17V5H19V19H5V5H7V7M7.5,13.5L9,12L11,14L15.5,9.5L17,11L11,17L7.5,13.5Z" />
			</svg>
    </a>
    <a href="http://2018.igem.org/Team:Rotterdam_HR/Hardware" class="nav-card">
      <h2>Hardware</h2>
      <svg viewBox="0 0 24 24">
        <path d="M15.9,18.45C17.25,18.45 18.35,17.35 18.35,16C18.35,14.65 17.25,13.55 15.9,13.55C14.54,13.55 13.45,14.65 13.45,16C13.45,17.35 14.54,18.45 15.9,18.45M21.1,16.68L22.58,17.84C22.71,17.95 22.75,18.13 22.66,18.29L21.26,20.71C21.17,20.86 21,20.92 20.83,20.86L19.09,20.16C18.73,20.44 18.33,20.67 17.91,20.85L17.64,22.7C17.62,22.87 17.47,23 17.3,23H14.5C14.32,23 14.18,22.87 14.15,22.7L13.89,20.85C13.46,20.67 13.07,20.44 12.71,20.16L10.96,20.86C10.81,20.92 10.62,20.86 10.54,20.71L9.14,18.29C9.05,18.13 9.09,17.95 9.22,17.84L10.7,16.68L10.65,16L10.7,15.31L9.22,14.16C9.09,14.05 9.05,13.86 9.14,13.71L10.54,11.29C10.62,11.13 10.81,11.07 10.96,11.13L12.71,11.84C13.07,11.56 13.46,11.32 13.89,11.15L14.15,9.29C14.18,9.13 14.32,9 14.5,9H17.3C17.47,9 17.62,9.13 17.64,9.29L17.91,11.15C18.33,11.32 18.73,11.56 19.09,11.84L20.83,11.13C21,11.07 21.17,11.13 21.26,11.29L22.66,13.71C22.75,13.86 22.71,14.05 22.58,14.16L21.1,15.31L21.15,16L21.1,16.68M6.69,8.07C7.56,8.07 8.26,7.37 8.26,6.5C8.26,5.63 7.56,4.92 6.69,4.92A1.58,1.58 0 0,0 5.11,6.5C5.11,7.37 5.82,8.07 6.69,8.07M10.03,6.94L11,7.68C11.07,7.75 11.09,7.87 11.03,7.97L10.13,9.53C10.08,9.63 9.96,9.67 9.86,9.63L8.74,9.18L8,9.62L7.81,10.81C7.79,10.92 7.7,11 7.59,11H5.79C5.67,11 5.58,10.92 5.56,10.81L5.4,9.62L4.64,9.18L3.5,9.63C3.41,9.67 3.3,9.63 3.24,9.53L2.34,7.97C2.28,7.87 2.31,7.75 2.39,7.68L3.34,6.94L3.31,6.5L3.34,6.06L2.39,5.32C2.31,5.25 2.28,5.13 2.34,5.03L3.24,3.47C3.3,3.37 3.41,3.33 3.5,3.37L4.63,3.82L5.4,3.38L5.56,2.19C5.58,2.08 5.67,2 5.79,2H7.59C7.7,2 7.79,2.08 7.81,2.19L8,3.38L8.74,3.82L9.86,3.37C9.96,3.33 10.08,3.37 10.13,3.47L11.03,5.03C11.09,5.13 11.07,5.25 11,5.32L10.03,6.06L10.06,6.5L10.03,6.94Z"></path>
      </svg>
    </a>
    <a href="http://2018.igem.org/Team:Rotterdam_HR/Software" class="nav-card">
      <h2>Software</h2>
			<svg viewBox="0 0 24 24">
				<path d="M14.6,16.6L19.2,12L14.6,7.4L16,6L22,12L16,18L14.6,16.6M9.4,16.6L4.8,12L9.4,7.4L8,6L2,12L8,18L9.4,16.6Z"></path>
			</svg>
    </a>
    <a href="http://2018.igem.org/Team:Rotterdam_HR/Experiments" class="nav-card">
      <h2>Experiment</h2>
			<svg viewBox="0 0 24 24">
				<path d="M7,2V4H8V18A4,4 0 0,0 12,22A4,4 0 0,0 16,18V4H17V2H7M11,16C10.4,16 10,15.6 10,15C10,14.4 10.4,14 11,14C11.6,14 12,14.4 12,15C12,15.6 11.6,16 11,16M13,12C12.4,12 12,11.6 12,11C12,10.4 12.4,10 13,10C13.6,10 14,10.4 14,11C14,11.6 13.6,12 13,12M14,7H10V4H14V7Z" />
			</svg>
    </a>
  </div>
</div>
		'''

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
																		 icon,
																		 entry['experiment'] if 'experiment' in entry else "")
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

			# instances = [m.start() for m in re.finditer('°', entry['description'])]
			# print(entry['title'] + ': ', end="")
			# print(instances)

			generatedEntries = generatedEntries + (self.GenerateEntry(entry, id))
			id = id + 1
		
		page = self.Style + self.Header + generatedEntries + self.Footer
		self.WritePage(page)
	
	def WritePage(self, page):
		with open(self._outputdir + 'project' + '-' + self.PageName.lower() + '.html', 'w') as f: # TODO: remove the hardcoded 'project' category
			page = htmlify(page)
			f.write(page)

if __name__ == '__main__': #Debug code
	print('Start debug code')
	with open('./input.json', 'r') as entries:
		data = entries.read()
		outputdir = os.path.dirname(os.path.realpath(__file__)) + '/output/'
		gen = NotebookGenerator([data, data], outputdir, './lib/', 'test')
	gen.GeneratePage()