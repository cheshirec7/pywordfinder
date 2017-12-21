import time
import math
# import itertools

from google.appengine.ext import ndb
from google.appengine.api import memcache

ASCII_a = 97
ASCII_z = 122
	
class WordLists(ndb.Model):
	words = ndb.TextProperty()
	
class search_model():

	def __init__(self):
		self.total_time = 0
		self.total_compares = 0
		self.total_found = 0
		self.total_cached = 0
		self.result_str = ''
		self.footer_str = ''
		self.list_words_list = []
			
	def load_ndb(self):
		for word_len in range(2,25):
			wordlist = WordLists(id=word_len)
			f = open('wordlists/wl_'+str(word_len)+'.txt','r')
			wordlist.words = f.read()
			f.close()
			wordlist.put()
		return 'complete'
	
	def find_words(self, letters_len, letter_counts_arr, search_mode, return_type):
		
		start_time = time.clock()
		
		for word_len in reversed(range(2, letters_len+1)):
			word_len_str = str(word_len)
			word_list = memcache.get('wl_'+word_len_str)
			if word_list is None:
				if search_mode == 'files':
					f = open('wordlists/wl_'+word_len_str+'.txt','r')
					word_list = f.read().split('*')
					f.close()
				else: #ndb
					word_list = WordLists().get_by_id(word_len).words.split('*')
				memcache.add('wl_'+word_len_str, word_list)
			else:
				self.total_cached += 1
				
			temp_str = ''
			for i in range(len(word_list)):
				local_letter_counts_arr = list(letter_counts_arr)
				word = word_list[i]
				for j in range(word_len):
					self.total_compares += 1
					idx = ord(word[j])-ASCII_a
					if local_letter_counts_arr[idx] == 0:
						word_list[i] = None
						break
					local_letter_counts_arr[idx] -= 1

				if return_type != 'json':
					if word_list[i]:
						temp_str += '<div>'+word+'</div>'
						self.total_found += 1
						
			if return_type == 'json':
				word_list = filter(bool, word_list) #word_list = list(itertools.ifilter(None, word_list))
				word_list_len = len(word_list)
				if word_list_len > 0:
					self.total_found += word_list_len
					self.list_words_list.append(word_list)
			else:
				if temp_str:
					self.result_str += '<p>'+word_len_str+' Letter Words</p><div class="wordcontainer">'+temp_str+'</div>'
				
		self.total_time = math.ceil((time.clock()-start_time)*1000)/1000 
		self.footer_str = 'Compares: '+str(self.total_compares)+'. Results: '+ str(self.total_found) +' in '+ str(self.total_time)+'s. Memcached: '+str(self.total_cached)
		return self
		
	def find_words_wild(self, letters_len, letter_counts_arr, wild_count, search_mode, return_type):
		start_time = time.clock()

		for word_len in reversed(range(2, letters_len+1)):
			word_len_str = str(word_len)
			word_list = memcache.get('wl_'+word_len_str)
			if word_list is None:
				if search_mode == 'files':
					f = open('wordlists/wl_'+word_len_str+'.txt','r')
					word_list = f.read().split('*')
					f.close()
				else: #ndb
					word_list = WordLists().get_by_id(word_len).words.split('*')
				memcache.add('wl_'+word_len_str, word_list)
			else:
				self.total_cached += 1
				
			if word_len > wild_count:
				temp_str = ''
				for i in range(len(word_list)):
					local_letter_counts_arr = list(letter_counts_arr)
					wild_avail = wild_count
					word = word_list[i]
					for j in range(word_len):
						self.total_compares += 1
						idx = ord(word[j])-ASCII_a
						if local_letter_counts_arr[idx] == 0:
							if wild_avail == 0:
								word_list[i] = None
								break
							else:
								wild_avail -= 1
						else:
							local_letter_counts_arr[idx] -= 1

					if return_type != 'json':
						if word_list[i]:
							temp_str += '<div>'+word+'</div>'
							self.total_found += 1
										
				if return_type == 'json':		
					word_list = filter(bool, word_list) # word_list = list(itertools.ifilter(None, word_list))
					word_list_len = len(word_list)
					if word_list_len > 0:
						self.total_found += word_list_len
						self.list_words_list.append(word_list)
				else:
					if temp_str:
						self.result_str += '<p>'+word_len_str+' Letter Words</p><div class="wordcontainer">'+temp_str+'</div>'
			else:
				if return_type == 'json':
					self.list_words_list.append(word_list)
				else:
					temp_str = ''
					for j in range(len(word_list)):
						temp_str += '<div>'+word_list[j]+'</div>'
					
					self.total_found += len(word_list)	
					self.result_str += '<p>'+word_len_str+' Letter Words</p><div class="wordcontainer">'+temp_str+'</div>'
							
		self.total_time = math.ceil((time.clock()-start_time)*1000)/1000
		self.footer_str = 'Compares: '+str(self.total_compares)+'. Results: '+ str(self.total_found) +' in '+ str(self.total_time)+'s. Memcached: '+str(self.total_cached)
		return self
	