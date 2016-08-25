import datetime

class Logger():
	def __init__(self):
		self.logfile = open('./logs/NaiveChess_log_' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M') + '.csv', 'w')
		self.logfile.write('function, start_timestamp\n')

	def log(self, function_name):
		self.logfile.write(function_name + '\n')

	def return_timestamp(self):
		time = datetime.datetime.now()
		return time.hour * 60 * 60 * 1000 + time.minute * 60 * 1000 + time.second * 1000 + time.microsecond/1000

global logger 
logger = Logger()