from my_genki_wave.asyncio_runner import run_asyncio_bluetooth
from my_genki_wave.callbacks import ButtonAndDataPrint

#from Folder1.pyscript1 import methodname

callbacks = [ButtonAndDataPrint(print_data_every_n_seconds=.1)]
ble_address = "EF:AA:3B:81:E7:D7"  # Address of the Wave ring, found in the previous step
test = run_asyncio_bluetooth(callbacks, ble_address)

#if i accidentally end with ctr z
#bluetoothctl
#(whatever the end command is [serial#])