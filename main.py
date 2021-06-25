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
import colorsys


udp_header = struct.pack("!bIBH", 66, 0, 0, 0)
s = socket(AF_INET, SOCK_DGRAM)

balls = [
	{
		'ip_address':237,
		'ring_attribute':'accel_x'
	},
	{
		'ip_address':19,
		'ring_attribute':'accel_x'
	},
	{
		'ip_address':85,
		'ring_attribute':'accel_x'
	}
]

# 'gyro_x':float(all_ring_data[-1].gyro.x),
# 'gyro_y':float(all_ring_data[-1].gyro.y),
# 'gyro_z':float(all_ring_data[-1].gyro.z),
# 'accel_x':float(all_ring_data[-1].accel.x)*255,
# 'accel_y':float(all_ring_data[-1].accel.y)*255,
# 'accel_z':float(all_ring_data[-1].accel.z)*255,
# 'raw_pose_x':float(all_ring_data[-1].raw_pose.x)*255,
# 'raw_pose_y':float(all_ring_data[-1].raw_pose.y)*255,
# 'raw_pose_z':float(all_ring_data[-1].raw_pose.z)*255,
# 'current_pose_x':float(all_ring_data[-1].current_pose.x),
# 'current_pose_y':float(all_ring_data[-1].current_pose.y),
# 'current_pose_z':float(all_ring_data[-1].current_pose.z),
# 'euler_roll':float(all_ring_data[-1].euler.roll)*127,
# 'euler_pitch':float(all_ring_data[-1].euler.pitch)*127,
# 'euler_yaw':float(all_ring_data[-1].euler.yaw)*127


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

	def hsv2rgb(h,s,v):
		return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h,s,v))

	def send_color_change(index, ipnumber, value, *args):
		ball_but[index]['text'] = value
		# if index == 0:
		# 	rgb = (value, 255-value, 0)
		# if index == 1:
		# 	rgb = (value, 0, 255-value)
		# if index == 2:
		# 	rgb = (0, value, 255-value)
		rgb = hsv2rgb(value,1,1)
		hex_code = '#{:02x}{:02x}{:02x}'.format(*rgb)
		ball_but[index]['bg'] = hex_code
		change_real_color(index, ipnumber, rgb)    	

	def ball_0_var_changed(self, *args):
		#print('ball_0_var_raw',ball_0_var.get())
		clean_value = min(255,abs(float(ball_0_var.get())))
		#print('ball_0_var_clean', clean_value)
		send_color_change(0,balls[0]['ip_address'], clean_value)

	def ball_1_var_changed(self, *args):
		#print('ball_1_var_raw',ball_1_var.get())
		clean_value = min(255,abs(float(ball_1_var.get())))
		#print('ball_1_var_clean', clean_value)
		send_color_change(1,balls[1]['ip_address'], clean_value)

	def ball_2_var_changed(self, *args):
		#print('ball_2_var_raw',ball_2_var.get())
		clean_value = min(255,abs(float(ball_2_var.get())))
		#print('ball_2_var_clean', clean_value)
		send_color_change(2,balls[2]['ip_address'], clean_value)

	# ball_string_vars = []
	# for i in range(balls):
	# 	this_var = StringVar()
	# 	this_var.trace(mode="w", callback=gyro_x_var_changed)
	# 	ball_string_vars.append(var)

	ball_0_var = StringVar()
	ball_0_var.trace(mode="w", callback=ball_0_var_changed)	

	ball_1_var = StringVar()
	ball_1_var.trace(mode="w", callback=ball_1_var_changed)	

	ball_2_var = StringVar()
	ball_2_var.trace(mode="w", callback=ball_2_var_changed)	

	l = Label(root)
	l.pack()
	e = Entry(root)
	e.pack()
	
	def submit():
		l.configure(text = e.get())

	ball_but = []

	ball_but.append(Button(text='',command=submit))
	ball_but[0].pack()
	ball_but.append(Button(text='',command=submit))
	ball_but[1].pack()
	ball_but.append(Button(text='',command=submit))
	ball_but[2].pack()

	def change_real_color(index, ipnumber, rgb):
		#rgb = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
		#data = struct.pack("!BBBB", 0x0a, rgb[0], rgb[1], rgb[2])

		# if index == 0:
		# 	data = struct.pack("!BBBB", 0x0a, value, 255-value, 0)
		# if index == 1:
		# 	data = struct.pack("!BBBB", 0x0a, value, 0, 255-value)
		# if index == 2:
		# 	data = struct.pack("!BBBB", 0x0a, 0, value, 255-value)

		data = struct.pack("!BBBB", 0x0a, rgb[0], rgb[1], rgb[2])
		s.sendto(udp_header+data, ('192.168.43.' + str(ipnumber), 41412));

	def get_ring_data_thread(arg):
		s = Sleeper(fetch_data_every_x_seconds)
		with reader_thread as wave:
			while True:
				all_ring_data = wave.queue.pop_all()
				if all_ring_data:
					for index, ball_data in enumerate(balls):
						def get_ring_value(i):
							switcher = {
								'gyro_x':float(all_ring_data[-1].gyro.x),
								'gyro_y':float(all_ring_data[-1].gyro.y),
								'gyro_z':float(all_ring_data[-1].gyro.z),
								'accel_x':float(all_ring_data[-1].accel.x),
								'accel_y':float(all_ring_data[-1].accel.y)*255,
								'accel_z':float(all_ring_data[-1].accel.z)*255,
								'raw_pose_x':round(float(all_ring_data[-1].raw_pose.x),3),
								'raw_pose_y':float(all_ring_data[-1].raw_pose.y)*255,
								'raw_pose_z':float(all_ring_data[-1].raw_pose.z)*255,
								'current_pose_x':float(all_ring_data[-1].current_pose.x)*255,
								'current_pose_y':float(all_ring_data[-1].current_pose.y)*255,
								'current_pose_z':float(all_ring_data[-1].current_pose.z)*255,
								'euler_roll':float(all_ring_data[-1].euler.roll)*160,
								'euler_pitch':float(all_ring_data[-1].euler.pitch)*160,
								'euler_yaw':float(all_ring_data[-1].euler.yaw)*160
							}
							return switcher.get(i,"Invalid value type")
						value = get_ring_value(ball_data['ring_attribute'])

						def get_ball_var(i):
							switcher = {
								0:ball_0_var,
								1:ball_1_var,
								2:ball_2_var
							}
							return switcher.get(i,"Invalid index number")
						this_ball_var = get_ball_var(index)
						this_ball_var.set(value)
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

