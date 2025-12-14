import os
import shutil

from stem.control import Controller




print(' * Connecting to tor')

with Controller.from_port() as controller:
  controller.authenticate()

  # All hidden services have a directory on disk. Lets put ours in tor's data
  # directory.
  current_dir = os.path.abspath(os.getcwd())
  hidden_service_dir = os.path.join(current_dir, 'data')


  # Create a hidden service where visitors of port 80 get redirected to local

  print(" * Creating our hidden service in %s" % hidden_service_dir)
  result = controller.create_hidden_service(hidden_service_dir, 80, target_port = 5000)

  # The hostname is only available when we can read the hidden service
  # directory. This requires us to be running with the same user as tor.

  if result.hostname:
    print(" * Our service is available at %s, press ctrl+c to quit" % result.hostname)
  else:
    print(" * Unable to determine our service's hostname, probably due to being unable to read the hidden service directory")

