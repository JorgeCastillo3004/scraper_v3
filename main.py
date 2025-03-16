import concurrent.futures
# import sys
# sys.path.append('modules')
from main1 import *
from main2 import *

database_enable = CONFIG['DATA_BASE']
if database_enable:
	con = getdb()


if __name__ == "__main__":

	with concurrent.futures.ThreadPoolExecutor() as executor:
		# Submit the functions for execution
		future1 = executor.submit(main_others)
		future2 = executor.submit(main_live)

		# Wait for both functions to complete
		concurrent.futures.wait([future1, future2])

		# Check if any exceptions occurred during execution
		for future in [future1, future2]:
			if future.exception():
				print(f"Exception occurred: {future.exception()}")