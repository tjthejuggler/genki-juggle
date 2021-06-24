import argparse
import time
from typing import Union
from genki_wave.data.organization import ButtonEvent
from genki_wave.discover import run_discover_bluetooth
from genki_wave.threading_runner import ReaderThreadBluetooth, ReaderThreadSerial
from tkinter import *
from threading import Thread
from time import sleep
from socket import *
import struct

udp_header = struct.pack("!bIBH", 66, 0, 0, 0)
s = socket(AF_INET, SOCK_DGRAM)

class Sleeper:
	def __init__(self, sleep_for_x_seconds: float):
		self._last_time = None
		self._sleep_for_x_seconds = sleep_for_x_seconds

	def sleep(self):
		curr_time = time.time()
		sleep_time = max(0.0, self._sleep_for_x_seconds - (self.last_time - curr_time))
		time.sleep(sleep_time)
		self._last_time = time.time()

	@property
	def last_time(self):
		if self._last_time is None:
			self._last_time = time.time()
		return self._last_time

def change_virtual_color(color):
	canvas.delete("all")
	canvas.pack(padx=15, anchor = 'w')
	canvas.create_oval(0, 0, 210, 210, fill = color)

def main(reader_thread: Union[ReaderThreadBluetooth, ReaderThreadSerial], fetch_data_every_x_seconds: float):
	root = Tk()

	def send_color_change(value, *args):
		my_but['text'] = value
		rgb = (value, 255-value, 0)
		hex_code = '#{:02x}{:02x}{:02x}'.format(*rgb)
		my_but['bg'] = hex_code
		change_real_color(value)    	

	def euler_pitch_var_changed(self, *args):
		print('euler_pitch_var_raw',euler_pitch_var.get())
		value = min(255,abs(int(float(euler_pitch_var.get())*85)))
		print('euler_pitch_var_clean', value)
		send_color_change('172', value)

	gyro_x_var = StringVar()
	gyro_x_var.trace(mode="w", callback=gyro_x_var_changed)
	euler_pitch_var = StringVar()
	euler_pitch_var.trace(mode="w", callback=euler_pitch_var_changed)
	l = Label(root)
	l.pack()
	e = Entry(root)
	e.pack()
	
	def submit():
		l.configure(text = e.get())

	my_but = Button(text='',command=submit)
	my_but.pack()

	def change_real_color(ipnumber, value):
		#rgb = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
		#data = struct.pack("!BBBB", 0x0a, rgb[0], rgb[1], rgb[2])
		data = struct.pack("!BBBB", 0x0a, value, 255-value, 0)
		s.sendto(udp_header+data, ('192.168.43.' + ipnumber, 41412));

	def get_ring_data_thread(arg):
		s = Sleeper(fetch_data_every_x_seconds)
		with reader_thread as wave:
			while True:
				val = wave.queue.pop_all()
				if val:
					# for v in val:
					#     if isinstance(v, ButtonEvent):
					#         print('vvvvvvvvvvv',v)
					# print('gyroX',val[-1].gyro.x)                      #range +-250
					#print('accelX', val[-1].accel.x)                   #range +- 1.000000
																		#changes a lot with juggling, but pretty sporadic
					#print('magX', val[-1].mag.x)                         # getting all 0
					# print('raw_poseX', val[-1].raw_pose.x)              #range +- 1.000000     --works very nicely
					#print('current_poseX', val[-1].current_pose.x)    #very similar to raw_pose, cant tell difference
					#print('eulerRoll', val[-1].euler.roll)              #range +-3.0000000
																		#smooth, but doesn't change much with juggling
					print('eulerPitch', val[-1].euler.pitch)          #divide 255 by 1.5 instead of 3*****
					# print('eulerYaw', val[-1].euler.yaw)              #smooth, changes pretty well with juggling, could probably be 
																		#modified a bit to make it better
					# print('linearX', val[-1].linear.x)

					#print('val[-1]', val[-1])

					#var.set(val[-1].gyro.x)
					#var.set(val[-1].accel.x*255)
					#var.set(val[-1].mag.x*255)
					#var.set(val[-1].raw_pose.x*255)
					#var.set(val[-1].current_pose.x*255)
					#var.set(val[-1].euler.roll*85)
					euler_pitch_var.set(val[-1].euler.pitch)
					#var.set(val[-1].euler.yaw*85)


				s.sleep()
	thread = Thread(target = get_ring_data_thread, args = (12,))
	thread.start()
	root.mainloop()

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--ble-address", type=str)
	parser.add_argument("--use-serial", action="store_true")
	parser.add_argument("--fetch-data-every-x-seconds", type=float, default=.01)
	args = parser.parse_args()

	if args.use_serial:
		main(ReaderThreadSerial.from_port(), args.fetch_data_every_x_seconds)
	else:
		if args.ble_address is None:
			print("No bluetooth address (--ble-address) supplied, searching for devices...")
			run_discover_bluetooth()
		else:
			print("Turn off using Ctrl + C (`KeyboardInterrupt`)")
			main(ReaderThreadBluetooth.from_address(args.ble_address), args.fetch_data_every_x_seconds)

